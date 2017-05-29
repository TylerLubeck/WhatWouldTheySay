import click
import requests

from collections import defaultdict

from wwts.utils import (
    get_user_id_for_username,
)

from wwts.database import User, Word


def _build_markov_chain_data(messages):
    markov = defaultdict(lambda: defaultdict(lambda: 0))

    for message in messages:
        split_words = message.split()
        for idx, word in enumerate(split_words[:-1]):
            markov[word][split_words[idx+1]] += 1
        if split_words:
            markov[split_words[-1]][None] += 1

    return markov


def _get_list_of_channel_ids(slack_token):
    channels = requests.post(
        'https://slack.com/api/channels.list',
        data={
            'token': slack_token,
        }
    ).json()

    return [channel['id'] for channel in channels['channels']]


def _get_user_messages_from_list(messages, user_id):
    return [
        message['text'].strip().lstrip('`').rstrip('`')
        for message in messages
        if (
            message['type'] == 'message'
            and 'subtype' not in message
            and message['user'] == user_id
            and message['text'].strip()
        )
    ]


def _get_user_messages_in_channel(user_id, channel_id, token):
    has_more = True
    response = requests.post(
        'https://slack.com/api/channels.history',
        data={
            'token': token,
            'channel': channel_id,
            'count': 1000,
            'oldest': 0,
            'inclusive': True,
        }
    ).json()
    try:
        has_more = response['has_more']
        latest = has_more and response['latest']
    except:
        has_more = False

    messages = _get_user_messages_from_list(response['messages'], user_id)

    while has_more:
        response = requests.post(
            'https://slack.com/api/channels.history',
            data={
                'token': token,
                'channel': channel_id,
                'count': 1000,
                'oldest': latest,
            }
        ).json()
        try:
            has_more = response['has_more']
            latest = has_more and response['latest']
        except Exception as e:
            print(e)
            print(response.keys())

        messages += _get_user_messages_from_list(response['messages'], user_id)

    return messages


@click.command()
@click.pass_context
@click.argument('username', required=True, envvar='LOAD_USERNAME')
def load_user(context, username):
    token = context.obj.token
    user_id = get_user_id_for_username(
        context.obj.db_session,
        username,
        token
    )
    channels = _get_list_of_channel_ids(token)

    messages = []
    for channel in channels:
        messages += _get_user_messages_in_channel(user_id, channel, token)

    markov_dict = _build_markov_chain_data(messages)

    db_session = context.obj.db_session
    user = db_session.query(User).filter(User.slack_id == user_id).one()
    for from_word, to_words in markov_dict.items():
        for to_word, count in to_words.items():
            word = Word(
                from_word=from_word,
                to_word=to_word,
                count=count,
                user=user
            )
            db_session.add(word)
    db_session.commit()
    context.obj.db_session.close()
