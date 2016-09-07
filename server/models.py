import sys
from sqlalchemy import (
    Table,
    Column,
    Integer,
    String,
    Text,
    DateTime,
    Float,
    ForeignKey,
    MetaData,
    create_engine
)
from sqlalchemy.sql import func

metadata = MetaData()


objects = Table("objects", metadata,
    Column("id", String(6), primary_key=True),
    Column("description", Text, nullable=False)
)

objects_status = Table("objects_status", metadata,
    Column("id", Integer, primary_key=True),
    Column("object_id", ForeignKey("objects.id"), index=True, nullable=False),
    Column("status", String(8), nullable=False),
    Column("x", Float(8), nullable=False),
    Column("y", Float(8), nullable=False),
    Column("timestamp", DateTime(timezone=True), index=True,
           server_default=func.now(), nullable=False),
)

def get_engine_args(host):
    return {'host': host,
            'port': 5432,
            'user': "postgres",
            'password': "postgres",
            'database': "postgres"}


def get_engine(host):
    tmpl = "postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}"
    return create_engine(tmpl.format(**get_engine_args(host)))


def create_tables(host):
    metadata.create_all(get_engine(host), checkfirst=True)

if __name__ == "__main__":
    create_tables(sys.argv[1])

