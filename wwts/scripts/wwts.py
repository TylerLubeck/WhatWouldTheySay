import click

from wwts.wwts import wwts


@click.command()
@click.pass_context
@click.argument('username', required=True, envvar='LOAD_USERNAME')
def what_would_they_say(context, username):
    print(wwts(context.obj.db_session, context.obj.token, username))
