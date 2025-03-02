import re
from os import getenv
from time import sleep

import click
import requests

from .base import CommentDriver
from ..terraform_out import TerraformOut


class BitbucketCloudComment(CommentDriver):
    DETECT_REGEX = re.compile(
        r"\Ahttps://(bitbucket\.org)/([^/]+)/([^/]+)/pull-requests/(\d+)\Z",
        re.IGNORECASE,
    )

    def add(self, workspace: str, tf_out: TerraformOut):
        bb = BitbucketCloud(
            username=getenv('BITBUCKET_USERNAME'),
            password=getenv('BITBUCKET_APP_PASSWORD'),
        )

        bb.pr(
            project_key=self.project_key,
            repository_slug=self.repository_slug,
            pull_request_id=self.pull_request_id,
        )

        for c in bb.comments():
            if c['content']['raw'].lstrip().startswith(
                f'### tf plan output: {workspace}'
            ):
                click.echo(f"[terratalk] deleting previous comment {c['id']}")
                bb.comment_delete(c['id'])

        if not tf_out.does_nothing():
            bb.comment_add(f'''
### tf plan output: {workspace}
```diff
{tf_out.show()}
```
''')

    def detect(self) -> bool:
        m = self.DETECT_REGEX.search(getenv('CHANGE_URL', ''))
        if m:
            self.server = m.group(1)
            self.type = 'bitbucket'
            self.project_key = m.group(2)
            self.repository_slug = m.group(3)
            self.pull_request_id = int(m.group(4))
            return True

        return False


class BitbucketCloud:
    BASE_URL = 'https://api.bitbucket.org/2.0'

    def __init__(self, username: str, password: str) -> None:
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
        request_url = f'{self.BASE_URL}/repositories/{self.project_key}/' \
                      f'{self.repository_slug}/pullrequests/' \
                      f'{self.pull_request_id}/comments'
        comments = []

        for comment in self.paginator(request_url):
            if not comment['deleted']:
                comments.append(comment)

        return comments

    def comment_add(self, comment: str):
        request_url = f'{self.BASE_URL}/repositories/{self.project_key}/' \
                      f'{self.repository_slug}/pullrequests/' \
                      f'{self.pull_request_id}/comments'

        r = requests.post(
            request_url,
            json={'content': {'raw': comment}},
            auth=(self.username, self.password),
        )
        return r

    def comment_delete(self, comment_id):
        request_url = f'{self.BASE_URL}/repositories/{self.project_key}/' \
                      f'{self.repository_slug}/pullrequests/' \
                      f'{self.pull_request_id}/comments/{comment_id}'

        r = requests.delete(
            request_url,
            auth=(self.username, self.password),
        )
        return r

    def paginator(self, url, params=None):
        if params is None:
            params = {}

        values = []
        retries = 0

        buf = {'next': url}
        while 'next' in buf:
            r = requests.get(
                buf['next'],
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

            retries = 0

        return values
