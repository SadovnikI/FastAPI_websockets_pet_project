import asyncio
import enum
from sqlalchemy import Column, Enum
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy import event
import random
from sqlalchemy.orm import Session

from manager.websocket_manager import websocket_manager

Base = declarative_base()


class Author(Base):
    __tablename__ = 'author'

    id = Column(Integer, primary_key=True)
    name = Column(String(30))
    fullname = Column(String)

    articles = relationship(
        "Article", back_populates="author", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"User(id={self.id!r}, name={self.name!r}, fullname={self.fullname!r})"


class StatusEnum(enum.Enum):
    draft = 'DRAFT'
    pending = 'STARTED'
    finished = 'FINISHED'
    failed = 'FAILED'


class Article(Base):
    __tablename__ = 'article'

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    text = Column(String, nullable=False)
    author_id = Column(Integer, ForeignKey("author.id"), nullable=False)
    status = Column(Enum(StatusEnum), server_default=StatusEnum.draft.value)

    author = relationship("Author", back_populates="articles")

    def __repr__(self):
        return f"Article(id={self.id!r}, title={self.title!r})"

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


@event.listens_for(Author, "before_insert")
def author_to_upper_case(mapper, connection, target):
    target.fullname = target.fullname.capitalize()
    target.name = target.name.capitalize()


@event.listens_for(Author, "after_insert")
def initial_article(mapper, connection, target):

    session = Session(bind=connection)

    data = {
        'id': random.randint(0, 1000000),
        'title': 'My first post',
        'text': 'Yay, my first article !!!!!!!!!!!!!',
        'author_id': target.id
    }
    session.commit()
    article = Article(**data)
    session.add(article)
    session.commit()
    session.refresh(article)


async def async_as_sync(target):
    await websocket_manager.broadcast(target.as_dict(), str(target.author_id))


@event.listens_for(Article, "before_update")
def broadcast_message(mapper, connection, target):
    session = Session(bind=connection)
    old_article = session.query(Article).get(target.id)
    if old_article.status != StatusEnum.finished.value and \
            target.status == StatusEnum.finished.value:
        asyncio.create_task(async_as_sync(target))


def run_async_function(function, *arguments):
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None
    if loop and loop.is_running():
        loop.create_task(function(*arguments))
    else:
        asyncio.run(function(*arguments))