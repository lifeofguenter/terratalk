import re
from os import getenv

import click
from github import Github

from .base import CommentDriver
from ..terraform_out import TerraformOut


class GithubComment(CommentDriver):
    DETECT_REGEX = re.compile(
        r"\Ahttps://(github\.com)/([^/]+)/([^/]+)/pull/(\d+)\Z",
        re.IGNORECASE,
    )

    def add(self, workspace: str, tf_out: TerraformOut):
        gh = Github(getenv('GITHUB_TOKEN'))

        repo = gh.get_repo(
            f"{self.project_key}/{self.repository_slug}"
        )
        issue = repo.get_issue(self.pull_request_id)

        # delete any older comments
        for c in issue.get_comments():
            if c.body.lstrip().startswith(f'<!-- terratalk: {workspace} -->'):
                click.echo(
                    f'[tf-comment-plan] deleting previous comment: {c.id}'
                )
                c.delete()

        if not tf_out.does_nothing():
            issue.create_comment(f'''
<!-- terratalk: {workspace} -->
### tf plan output: {workspace}
```diff
{tf_out.show()}
```
''')

    def detect(self) -> bool:
        m = self.DETECT_REGEX.search(getenv('CHANGE_URL', ''))
        if m:
            self.server = m.group(1)
            self.type = 'github'
            self.project_key = m.group(2)
            self.repository_slug = m.group(3)
            self.pull_request_id = int(m.group(4))
            return True

        return False
