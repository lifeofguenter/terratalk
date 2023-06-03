import os
import re

import click

from terratalk.terraform_out import TerraformOut


@click.group()
@click.version_option()
def cli():
    pass


@cli.command()
@click.option('-w', '--workspace')
def comment(workspace):

    m = re.search(
        r'\A(https?://.*?)/projects/([^/]+)/repos/([^/]+)/pull-requests/(\d+)',
        os.getenv('CHANGE_URL'),
        re.IGNORECASE,
    )

    if not m:
        m = re.search(
            r'\Ahttps://(github\.com|bitbucket\.org)'
            r'/([^/]+)/([^/]+)/(?:pull|pull-requests)/(\d+)\Z',
            os.getenv('CHANGE_URL'),
            re.IGNORECASE,
        )

    server = m.group(1)
    project_key = m.group(2)
    repository_slug = m.group(3)
    pull_request_id = int(m.group(4))

    # fetch terraform output
    tf = TerraformOut(workspace + '.plan')

    if tf.does_nothing():
        click.echo('[terratalk] this plan does nothing')

    if server == 'github.com':
        from github import Github

        gh = Github(os.getenv('GITHUB_TOKEN'))

        repo = gh.get_repo(f'{project_key}/{repository_slug}')
        issue = repo.get_issue(pull_request_id)

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

    elif server == 'bitbucket.org':
        from terratalk.bitbucket_cloud import BitbucketCloud

        bb = BitbucketCloud(
            username=os.getenv('BITBUCKET_USERNAME'),
            password=os.getenv('BITBUCKET_APP_PASSWORD'),
        )

        bb.pr(
            project_key=project_key,
            repository_slug=repository_slug,
            pull_request_id=pull_request_id,
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
            base_url=server,
            username=os.getenv('STASH_USER'),
            password=os.getenv('STASH_PASS'),
        )
        bs.pr(
            project_key=project_key,
            repository_slug=repository_slug,
            pull_request_id=pull_request_id,
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
