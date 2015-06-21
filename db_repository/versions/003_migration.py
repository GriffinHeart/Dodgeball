from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
event = Table('event', pre_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('summary', String),
    Column('description', String),
    Column('location', String),
    Column('start_dt', DateTime),
    Column('end_dt', DateTime),
    Column('google_id', String),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    pre_meta.tables['event'].columns['description'].drop()
    pre_meta.tables['event'].columns['end_dt'].drop()
    pre_meta.tables['event'].columns['location'].drop()
    pre_meta.tables['event'].columns['start_dt'].drop()
    pre_meta.tables['event'].columns['summary'].drop()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    pre_meta.tables['event'].columns['description'].create()
    pre_meta.tables['event'].columns['end_dt'].create()
    pre_meta.tables['event'].columns['location'].create()
    pre_meta.tables['event'].columns['start_dt'].create()
    pre_meta.tables['event'].columns['summary'].create()
