import re
from os import getenv

import click
import requests

from .base import CommentDriver
from ..terraform_out import TerraformOut


class GiteaComment(CommentDriver):
    PR_REGEX = re.compile(r"refs/pull/(\d+)/head", re.IGNORECASE)

    def add(self, workspace: str, tf_out: TerraformOut):
        gitea = Gitea(self.server, getenv('TERRATALK_GITEA_TOKEN'))
        gitea.pr(self.repository_slug, self.pull_request_id)

        for c in gitea.comments():
            if c['body'].lstrip().startswith(
                f'<!-- terratalk: {workspace} -->'
            ):
                click.echo(
                    f"[tf-comment-plan] deleting previous comment: {c['id']}"
                )
                gitea.comment_delete(c['id'])

        if not tf_out.does_nothing():
            gitea.comment_add(f'''
<!-- terratalk: {workspace} -->
### tf plan output: {workspace}
```diff
{tf_out.show()}
```
''')

    def detect(self) -> bool:
        if getenv('GITEA_ACTIONS') == 'true':
            self.type = 'gitea'
            self.server = getenv('GITHUB_API_URL')
            self.project_key = getenv('GITHUB_REPOSITORY_OWNER')
            self.repository_slug = getenv('GITHUB_REPOSITORY')
            m = self.PR_REGEX.search(getenv('GITHUB_REF', ''))
            if m:
                self.pull_request_id = int(m.group(1))
                return True
        return False


class Gitea:
    def __init__(self, server: str, token: str):
        self.server = server
        self.token = token
        self.repository_slug = None
        self.pull_request_id = None

    def pr(self, repository_slug: str, pull_request_id: int):
        self.repository_slug = repository_slug
        self.pull_request_id = pull_request_id

    def comments(self) -> list[dict]:
        return [
            c for c in self.get(
                f"repos/{self.repository_slug}/issues/comments"
            )
            if c.get('pull_request_url', '').endswith(
                f"/{self.pull_request_id}"
            )
        ]

    def comment_delete(self, comment_id: int):
        self.delete(
            f"repos/{self.repository_slug}/issues/comments/{comment_id}"
        )

    def comment_add(self, body: str):
        self.post(
            f"repos/{self.repository_slug}/issues/"
            f"{self.pull_request_id}/comments",
            {"body": body},
        )

    def get(self, path: str) -> dict:
        return requests.get(
            f"{self.server}/{path}",
            headers={"Authorization": f"token {self.token}"},
        ).json()

    def post(self, path: str, data: dict) -> dict:
        return requests.post(
            f"{self.server}/{path}",
            headers={"Authorization": f"token {self.token}"},
            json=data,
        ).json()

    def delete(self, path: str):
        return requests.delete(
            f"{self.server}/{path}",
            headers={"Authorization": f"token {self.token}"},
        )
