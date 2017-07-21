import requests
from wwts.database import User

import logging
logger = logging.getLogger(__name__)


def get_user_id_for_username(db_session, username, token):
    """Based on a username, get the slack user id

    We have to loop through all users in the slack team because slack
    doesn't provide an API for this mapping.

    # TODO: Cache this result. Simple lru_cache is probably fine
    """
    all_users = requests.post(
        'https://slack.com/api/users.list',
        data={
            'token': token,
        }
    ).json()

    user_id = None
    for member in all_users['members']:
        if member['name'] == username:
            user_id = member['id']
            break

    known_users = db_session.query(User).filter(
        User.user_name == username
    ).all()

    # First instance of this user
    if not known_users:
        logger.info('Not a known user')
        user = User(user_name=username, slack_id=user_id)
        db_session.add(user)
        logger.info('Added user: %s', user)

    if len(known_users) == 1:
        logger.info('Is a known user')
        user = known_users[0]
        if user.slack_id != user_id:
            user.slack_id = user_id
            logger.info('username changed for %s', user)
            db_session.add(user)

    # TODO: Handle more than one known user?

    logger.info('Committing session')
    db_session.commit()

    return user_id


