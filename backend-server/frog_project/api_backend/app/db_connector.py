from sqlalchemy import create_engine, MetaData, ForeignKey, DateTime, Column, String, Integer, Numeric
from sqlalchemy.orm import declarative_base, create_session
from .secrets import Secrets
from .settings import Settings


db_type = "postgresql"
db_user = "postgres"
db_password = Secrets.db_password
db_hostname = Settings.database_hostname
db_name = Settings.database_name

db_uri = f"{db_type}://{db_user}:{db_password}@{db_hostname}/{db_name}"


Base = declarative_base()
metadata_obj = MetaData()


def main():
    engine = create_engine(db_uri)
    session = create_session(engine)


if __name__ == '__main__':
    main()
