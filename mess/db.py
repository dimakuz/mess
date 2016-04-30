from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


Base = declarative_base()

_engine = None
_Session = None


def init(path=':memory:'):
    global _engine

    url = 'sqlite:///{0}'.format(path)
    _engine = create_engine(url, echo=False)


def deploy():
    if _engine is None:
        raise RuntimeError('Database connection was not initialized')
    print 'create all'
    print Base.metadata.sorted_tables
    Base.metadata.create_all(_engine)


def get_session():
    global _Session

    if _engine is None:
        raise RuntimeError('Database connection was not initialized')

    if _Session is None:
        _Session = sessionmaker()
        _Session.configure(bind=_engine)

    return _Session()
