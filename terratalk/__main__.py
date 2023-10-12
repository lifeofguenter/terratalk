import os
import re

import click

from terratalk.terraform_out import TerraformOut


def _get_pr_details() -> dict:
    pr_type = ''
    pr_server = ''
    pr_project_key = ''
    pr_repository_slug = ''
    pr_pull_request_id = ''

    if os.getenv('CI_SERVER_NAME') == 'GitLab':
        pr_type = 'gitlab'
        pr_server = os.getenv('CI_SERVER_URL')
        pr_project_key = int(os.getenv('CI_MERGE_REQUEST_PROJECT_ID'))
        pr_pull_request_id = int(os.getenv('CI_MERGE_REQUEST_IID'))

    else:
        m = re.search(
            r'\A(https?://.*?)/projects/([^/]+)/repos/([^/]+)'
            r'/pull-requests/(\d+)',
            os.getenv('CHANGE_URL', ''),
            re.IGNORECASE,
        )

        if not m:
            m = re.search(
                r'\Ahttps://(github\.com|bitbucket\.org)'
                r'/([^/]+)/([^/]+)/(?:pull|pull-requests)/(\d+)\Z',
                os.getenv('CHANGE_URL', ''),
                re.IGNORECASE,
            )

        if m:
            pr_server = m.group(1)
            if 'github.com' in pr_server:
                pr_type = 'github'
            elif 'bitbucket.org' in pr_server:
                pr_type = 'bitbucket'
            else:
                pr_type = 'bitbucket-server'
            pr_project_key = m.group(2)
            pr_repository_slug = m.group(3)
            pr_pull_request_id = int(m.group(4))

    return {
        'type': pr_type,
        'server': pr_server,
        'project_key': pr_project_key,
        'repository_slug': pr_repository_slug,
        'pull_request_id': pr_pull_request_id,
    }


@click.group()
@click.version_option()
def cli():
    pass


@cli.command()
@click.option('-w', '--workspace')
def comment(workspace):

    pr_details = _get_pr_details()

    # fetch terraform output
    tf = TerraformOut(workspace + '.plan')

    if tf.does_nothing():
        click.echo('[terratalk] this plan does nothing')

    if pr_details['type'] == 'gitlab':
        # CI_SERVER_NAME=GitLab
        import gitlab
        gl = gitlab.Gitlab(
            pr_details['server'],
            private_token=os.getenv('GITLAB_TOKEN'),
        )
        gl.auth()

        gl_project = gl.projects.get(pr_details['project_key'], lazy=True)
        gl_mr = gl_project.mergerequests.get(
            pr_details['pull_request_id'],
            lazy=True,
        )
        for discussion in gl_mr.discussions.list(get_all=True):
            for note in discussion.attributes['notes']:
                if note['body'].lstrip().startswith(
                   f'<!-- terratalk: {workspace} -->'):
                    disc = gl_mr.discussions.get(discussion.id)
                    disc.notes.delete(id=note['id'])

        if not tf.does_nothing():
            gl_mr.discussions.create({'body': f'''
<!-- terratalk: {workspace} -->
### tf plan output: {workspace}
```diff
{tf.show()}
```
'''})

    elif pr_details['type'] == 'github':
        from github import Github

        gh = Github(os.getenv('GITHUB_TOKEN'))

        repo = gh.get_repo(
            f"{pr_details['project_key']}/{pr_details['repository_slug']}"
        )
        issue = repo.get_issue(pr_details['pull_request_id'])

        # delete any older comments
        for c in issue.get_comments():
            if c.body.lstrip().startswith(f'<!-- terratalk: {workspace} -->'):
                click.echo(
                    f'[tf-comment-plan] deleting previous comment: {c.id}'
                )
                c.delete()

        if not tf.does_nothing():
            issue.create_comment(f'''
<!-- terratalk: {workspace} -->
### tf plan output: {workspace}
```diff
{tf.show()}
```
''')

    elif pr_details['type'] == 'bitbucket':
        from terratalk.bitbucket_cloud import BitbucketCloud

        bb = BitbucketCloud(
            username=os.getenv('BITBUCKET_USERNAME'),
            password=os.getenv('BITBUCKET_APP_PASSWORD'),
        )

        bb.pr(
            project_key=pr_details['project_key'],
            repository_slug=pr_details['repository_slug'],
            pull_request_id=pr_details['pull_request_id'],
        )

        for c in bb.comments():
            if c['content']['raw'].lstrip().startswith(
                f'### tf plan output: {workspace}'
            ):
                click.echo(f"[terratalk] deleting previous comment {c['id']}")
                bb.comment_delete(c['id'])

        if not tf.does_nothing():
            bb.comment_add(f'''
### tf plan output: {workspace}
```diff
{tf.show()}
```
''')

    else:
        from terratalk.bitbucket_server import BitbucketServer

        bs = BitbucketServer(
            base_url=pr_details['server'],
            username=os.getenv('STASH_USER'),
            password=os.getenv('STASH_PASS'),
        )
        bs.pr(
            project_key=pr_details['project_key'],
            repository_slug=pr_details['repository_slug'],
            pull_request_id=pr_details['pull_request_id'],
        )

        # delete any older comments
        for c in bs.comments():
            if c['comment']['text'].lstrip().startswith(
                f'[comment]: # (terratalk: {workspace})'
            ):
                click.echo(f"[terratalk] deleting previous comment {c['id']}")
                bs.comment_delete(c['comment']['id'], c['comment']['version'])

        if not tf.does_nothing():
            # https://bitbucket.org/tutorials/markdowndemo/issues/15/how-can-you-insert-comments-in-the#comment-22433250
            bs.comment_add(f'''
[comment]: # (terratalk: {workspace})
### tf plan output: {workspace}
```diff
{tf.show()}
```
''')


@cli.command()
@click.option('-w', '--workspace')
def output(workspace):
    tf = TerraformOut(workspace + '.plan')

    if tf.does_nothing():
        click.echo('[terratalk] this plan does nothing')
    else:
        click.echo(tf.show())


if __name__ == '__main__':
    cli()
