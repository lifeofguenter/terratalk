import re
from os import getenv
from time import sleep

import click
import requests

from .base import CommentDriver
from ..terraform_out import TerraformOut


class BitbucketServerComment(CommentDriver):
    DETECT_REGEX = re.compile(
        r"\A(https?://.*?)/projects/([^/]+)/repos/([^/]+)/pull-requests/(\d+)",
        re.IGNORECASE,
    )

    def add(self, workspace: str, tf_out: TerraformOut):
        bs = BitbucketServer(
            base_url=self.server,
            username=getenv('STASH_USER'),
            password=getenv('STASH_PASS'),
        )
        bs.pr(
            project_key=self.project_key,
            repository_slug=self.repository_slug,
            pull_request_id=self.pull_request_id,
        )

        # delete any older comments
        for c in bs.comments():
            if c['comment']['text'].lstrip().startswith(
                f'[comment]: # (terratalk: {workspace})'
            ):
                click.echo(f"[terratalk] deleting previous comment {c['id']}")
                bs.comment_delete(c['comment']['id'], c['comment']['version'])

        if not tf_out.does_nothing():
            # https://bitbucket.org/tutorials/markdowndemo/issues/15/how-can-you-insert-comments-in-the#comment-22433250
            bs.comment_add(f'''
[comment]: # (terratalk: {workspace})
### tf plan output: {workspace}
```diff
{tf_out.show()}
```
''')

    def detect(self) -> bool:
        m = self.DETECT_REGEX.search(getenv('CHANGE_URL', ''))
        if m:
            self.type = 'bitbucket-server'
            self.server = m.group(1)
            self.project_key = m.group(2)
            self.repository_slug = m.group(3)
            self.pull_request_id = int(m.group(4))
            return True

        return False


class BitbucketServer:
    def __init__(self, base_url: str, username: str, password: str) -> None:
        self.base_url = f'{base_url}/rest/api/1.0'
        self.username = username
        self.password = password
        self.project_key = None
        self.repository_slug = None
        self.pull_request_id = None

    def pr(self, project_key=None, repository_slug=None, pull_request_id=None):
        self.project_key = project_key
        self.repository_slug = repository_slug
        self.pull_request_id = pull_request_id

    def comments(self):
        request_url = f'{self.base_url}/projects/{self.project_key}/repos/' \
                      f'{self.repository_slug}/pull-requests/' \
                      f'{self.pull_request_id}/activities'
        comments = []
        for value in self.paginator(request_url):
            if value['action'] == 'COMMENTED':
                comments.append(value)

        return comments

    def comment_add(self, comment: str):
        request_url = f'{self.base_url}/projects/{self.project_key}/repos/' \
                      f'{self.repository_slug}/pull-requests/' \
                      f'{self.pull_request_id}/comments'

        r = requests.post(
            request_url,
            json={'text': comment},
            auth=(self.username, self.password),
        )
        return r

    def comment_delete(self, comment_id, version):
        request_url = f'{self.base_url}/projects/{self.project_key}/repos/' \
                      f'{self.repository_slug}/pull-requests/' \
                      f'{self.pull_request_id}/comments/{comment_id}'

        r = requests.delete(
            request_url,
            params={'version': version},
            auth=(self.username, self.password),
        )
        return r

    def paginator(self, url, params=None):
        if params is None:
            params = {}

        values = []
        retries = 0

        while True:
            r = requests.get(
                url,
                params=params,
                auth=(self.username, self.password),
            )
            buf = r.json()

            if 'values' not in buf and retries < 3:
                print(buf)
                retries = retries + 1
                sleep(1)
                continue

            values += buf['values']

            if buf['isLastPage']:
                break
            else:
                params['start'] = buf['nextPageStart']

            retries = 0

        return values
