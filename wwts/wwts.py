from collections import defaultdict
import random
import logging

from .utils import get_user_id_for_username
from .database import User, Word

logger = logging.getLogger(__name__)


def _convert_words_to_dict(words):
    """Convert a list of word objects in to a frequency counter of pairs"""

    word_dict = defaultdict(lambda: defaultdict(lambda: 0))
    for word in words:
        word_dict[word.from_word][word.to_word] = word.count

    return word_dict


def _compute_next_word(first_word, words):
    """Given a word, compute the most likely next word choice based on 
    frequency pair
    """
    choice_words = words[first_word]
    total_usage = sum(choice_words.values())
    target_usage = total_usage * random.random()

    if not choice_words:
        return None

    next_word = None
    logger.info('word: %s, choice_words: %s', first_word, str(choice_words))
    for word, value in choice_words.items():
        target_usage -= value
        if target_usage < 0:
            next_word = word

    return next_word


def wwts_from_user(db_session, user):
    """Given a user, generate a sentence they might say

    NOTE: Maxed at a 50 word sentence 
    """
    words = db_session.query(Word).filter(Word.user == user).all()
    word_dict = _convert_words_to_dict(words)

    sentence = []
    next_word = random.choice(list(word_dict.keys()))
    sentence.append(next_word)

    # NOTE: This is arbitrarily capped at 50 words to prevent any weird
    # endless word loops
    while next_word and len(sentence) < 50:
        logger.debug(
            'next word: %s, sentence: %s',
            next_word,
            ' '.join(sentence)
        )
        next_word = _compute_next_word(next_word, word_dict)
        sentence.append(next_word)

    return ' '.join(sentence[:-1])


def wwts(db_session, slack_token, username):
    """Compute what a user might say"""
    user_id = get_user_id_for_username(
        db_session,
        username,
        slack_token
    )

    user = db_session.query(User).filter(User.slack_id == user_id).one()
    return wwts_from_user(db_session, user)

