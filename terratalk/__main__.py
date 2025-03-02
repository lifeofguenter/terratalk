import importlib
import pkgutil

import click

import terratalk.drivers
from terratalk.drivers.base import CommentDriver
from terratalk.terraform_out import TerraformOut


def get_comment_driver() -> CommentDriver:
    """Dynamically load and return the first matching PR driver."""
    for _, module_name, _ in pkgutil.iter_modules(terratalk.drivers.__path__):
        if module_name == 'base':
            continue

        module = importlib.import_module(f"terratalk.drivers.{module_name}")

        # Find a class that inherits from CommentDriver
        for obj in module.__dict__.values():
            if (isinstance(obj, type) and
               issubclass(obj, CommentDriver) and obj is not CommentDriver):
                driver_instance = obj()
                if driver_instance.detect():
                    return driver_instance

    raise RuntimeError("No PR driver matched the environment.")


@click.group()
@click.version_option()
def cli():
    pass


@cli.command()
@click.option('-w', '--workspace')
def comment(workspace):
    # fetch terraform output
    tf = TerraformOut(workspace + '.plan')

    if tf.does_nothing():
        click.echo('[terratalk] this plan does nothing')

    pr = get_comment_driver()
    pr.add(workspace, tf)


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
