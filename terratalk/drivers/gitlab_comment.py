from os import getenv

import click
import gitlab

from .base import CommentDriver
from ..terraform_out import TerraformOut


class GitlabComment(CommentDriver):
    def __init__(self):
        super().__init__()
        self.gl = gitlab.Gitlab(
            self.server,
            private_token=getenv('GITLAB_TOKEN'),
        )

    def add(self, workspace: str, tf_out: TerraformOut):
        self.gl.auth()

        gl_project = self.gl.projects.get(self.project_key, lazy=True)
        gl_mr = gl_project.mergerequests.get(
            self.pull_request_id,
            lazy=True,
        )
        for discussion in gl_mr.discussions.list(get_all=True):
            for note in discussion.attributes['notes']:
                if note['body'].lstrip().startswith(
                    f"<!-- terratalk: {workspace} -->"
                ):
                    disc = gl_mr.discussions.get(discussion.id)
                    click.echo(
                        f"[tf-comment-plan] deleting previous comment: "
                        f"{note['id']}"
                    )
                    disc.notes.delete(id=note['id'])

        if not tf_out.does_nothing():
            gl_mr.discussions.create({'body': f'''
<!-- terratalk: {workspace} -->
### tf plan output: {workspace}
```diff
{tf_out.show()}
```
'''})

    def detect(self) -> bool:
        if getenv('CI_SERVER_NAME') == 'GitLab':
            self.type = 'gitlab'
            self.server = getenv('CI_SERVER_URL')
            self.project_key = int(getenv('CI_MERGE_REQUEST_PROJECT_ID'))
            self.pull_request_id = int(getenv('CI_MERGE_REQUEST_IID'))
            return True
        return False
