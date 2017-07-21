import logging
import click

from wwts.database import create_sqlalchemy_session

from wwts.scripts.load_user import load_user, load_private_user
from wwts.scripts.wwts import what_would_they_say
from wwts.slack import slack

logging.basicConfig(level='INFO')
logger = logging.getLogger(__name__)


class Context:
    def __init__(self, slack_token, db_url):
        self.token = slack_token
        self.db_url = db_url
        self.db_session = create_sqlalchemy_session(db_url)


@click.group()
@click.pass_context
@click.option('--token', required=True, envvar='SLACK_TOKEN')
@click.option('--db_url', required=True, envvar='DB_URL')
def main(context, token, db_url):
    context.obj = Context(token, db_url)

main.add_command(load_user)
main.add_command(load_private_user)
main.add_command(what_would_they_say)
main.add_command(slack)

if __name__ == '__main__':
    main()
