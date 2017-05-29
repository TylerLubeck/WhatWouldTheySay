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
    slack_user_image = None
    if match:
        slack_id = match['slack_id']
        logger.info('Looking up %s', slack_id)
        user = db_session.query(User).filter(User.slack_id == slack_id).one()
        what_would_they_say = wwts_from_user(db_session, user)

        slack_user_image = _get_slack_user_image(slack_client, slack_id)

        markov_message = what_would_they_say

    return markov_message, slack_user_image


def _get_slack_user_image(slack_client, slack_user_id):
    result = slack_client.api_call('users.info', user=slack_user_id)
    image = None
    if result['ok']:
        image = result['user']['profile']['image_32']

    return image


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
                logger.debug(event)
                if event.get('type') == 'message' and 'subtype' not in event:
                    markov_message, image = _handle_message(
                        db_session,
                        slack_client,
                        event
                    )

                    channel_id = event['channel']
                    slack_client.api_call(
                        'chat.postMessage',
                        channel=channel_id,
                        text=markov_message,
                        icon_url=image
                    )

            time.sleep(1)  # Just to be polite
    else:
        logger.error('Connection failed, invalid token?')
