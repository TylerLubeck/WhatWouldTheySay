from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import (
    sessionmaker,
    relationship,
)
from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    String,
)

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    user_name = Column(String(255))
    slack_id = Column(String(255))

    def __repr__(self):
        return '<User(id={}, user_name={}, slack_id={})'.format(
            self.id,
            self.user_name,
            self.slack_id
        )


class Word(Base):
    __tablename__ = 'words'

    id = Column(Integer, primary_key=True)
    from_word = Column(String(255), index=True)
    to_word = Column(String(255), index=True)
    count = Column(Integer)

    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship('User', back_populates='words')

User.words = relationship('Word', order_by=Word.id, back_populates='user')


def create_sqlalchemy_session(sql_url):
    engine = create_engine(sql_url)
    Base.metadata.create_all(engine)  # Make the database tables

    Session = sessionmaker(bind=engine)

    return Session()
