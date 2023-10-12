from os import getenv

import click

from terratalk.pr_details import PrDetails
from terratalk.terraform_out import TerraformOut


@click.group()
@click.version_option()
def cli():
    pass


@cli.command()
@click.option('-w', '--workspace')
def comment(workspace):

    pr = PrDetails()

    # fetch terraform output
    tf = TerraformOut(workspace + '.plan')

    if tf.does_nothing():
        click.echo('[terratalk] this plan does nothing')

    if pr.type == 'gitlab':
        import gitlab
        gl = gitlab.Gitlab(
            pr.server,
            private_token=getenv('GITLAB_TOKEN'),
        )
        gl.auth()

        gl_project = gl.projects.get(pr.project_key, lazy=True)
        gl_mr = gl_project.mergerequests.get(
            pr.pull_request_id,
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

    elif pr.type == 'github':
        from github import Github

        gh = Github(getenv('GITHUB_TOKEN'))

        repo = gh.get_repo(
            f"{pr.project_key}/{pr.repository_slug}"
        )
        issue = repo.get_issue(pr.pull_request_id)

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

    elif pr.type == 'bitbucket':
        from terratalk.bitbucket_cloud import BitbucketCloud

        bb = BitbucketCloud(
            username=getenv('BITBUCKET_USERNAME'),
            password=getenv('BITBUCKET_APP_PASSWORD'),
        )

        bb.pr(
            project_key=pr.project_key,
            repository_slug=pr.repository_slug,
            pull_request_id=pr.pull_request_id,
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
            base_url=pr.server,
            username=getenv('STASH_USER'),
            password=getenv('STASH_PASS'),
        )
        bs.pr(
            project_key=pr.project_key,
            repository_slug=pr.repository_slug,
            pull_request_id=pr.pull_request_id,
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
