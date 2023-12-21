import contextlib

from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from src.conf.config import config


class DatabaseSessionManager:
    def __init__(self, url: str):
        self._engine: Engine | None = create_engine(url)
        self._session_maker = sessionmaker(autocommit=False, autoflush=False, bind=self._engine)

    @contextlib.contextmanager
    def session(self):
        if self._session_maker is None:
            raise Exception('Session is not initialized')
        session = self._session_maker()
        try:
            yield session
        except Exception as err:
            print(err)
            session.rollback()
        finally:
            session.close()


sessionmanager = DatabaseSessionManager(config.DB_URL)


def get_db():
    with sessionmanager.session() as session:
        yield session
