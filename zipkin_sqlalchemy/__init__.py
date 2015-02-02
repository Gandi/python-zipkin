
from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    )

DBSession = None
Base = declarative_base()

if not DBSession:
    DBSession = scoped_session(sessionmaker())


