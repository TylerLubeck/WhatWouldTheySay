from sqlalchemy.orm.exc import NoResultFound
import click
import time
from slackclient import SlackClient
import re

from wwts.database import User
from wwts.wwts import wwts_from_user

import logging
logger = logging.getLogger(__name__)

msg_format_regex = re.compile('^what would <@(?P<slack_id>.*)> say\??$')


def _handle_message(db_session, slack_client, event):
    message_text = event['text']
    match = msg_format_regex.match(message_text)

    markov_message = None
    slack_user = None
    if match:
        logger.info(message_text, match)
        slack_id = match['slack_id']
        logger.info('Looking up %s', slack_id)
        try:
            user = db_session.query(User).filter(
                User.slack_id == slack_id
            ).one()
        except NoResultFound:
            markov_message = 'ERROR: We don\'t know what they\'ll say.'
        else:
            what_would_they_say = wwts_from_user(db_session, user)
            slack_user = _get_slack_user(slack_client, user.slack_id)
            markov_message = what_would_they_say

    return markov_message, slack_user


def _get_slack_user(slack_client, slack_user_id):
    result = slack_client.api_call('users.info', user=slack_user_id)
    user = None
    if result['ok']:
        user = result['user']

    return user


@click.command()
@click.pass_context
def slack(context):
    slack_token = context.obj.token
    db_session = context.obj.db_session
    slack_client = SlackClient(slack_token)

    if slack_client.rtm_connect():
        while True:
            events = slack_client.rtm_read()
            for event in events:
                if event.get('type') == 'message' and 'subtype' not in event:
                    markov_message, slack_user = _handle_message(
                        db_session,
                        slack_client,
                        event
                    )

                    if markov_message and slack_user:
                        channel_id = event['channel']
                        image = slack_user['profile']['image_32']
                        name = '{} Bot'.format(
                            slack_user['profile']['real_name']
                        )
                        response = slack_client.api_call(
                            'chat.postMessage',
                            channel=channel_id,
                            text=markov_message,
                            icon_url=image,
                            username=name
                        )

                        logger.info(response)

            time.sleep(1)  # Just to be polite
    else:
        logger.error('Connection failed, invalid token?')
