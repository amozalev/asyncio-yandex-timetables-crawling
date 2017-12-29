from aiopg.sa import create_engine
import sqlalchemy as sa
from sqlalchemy.schema import CreateTable, DropTable, CreateSequence, DropSequence
import config

metadata = sa.MetaData()

station_type = sa.Table('station_type', metadata,
                        sa.Column('id', sa.INTEGER, primary_key=True),
                        sa.Column('title', sa.Text))

transport_type = sa.Table('transport_type', metadata,
                          sa.Column('id', sa.Integer, primary_key=True),
                          sa.Column('title', sa.Text))

station = sa.Table('station', metadata,
                   sa.Column('id', sa.Integer, primary_key=True),
                   sa.Column('code', sa.Text),
                   sa.Column('title', sa.Text),
                   sa.Column('station_type_id', sa.Integer, sa.ForeignKey('station_type.id')),
                   sa.Column('transport_type_id', sa.Integer, sa.ForeignKey('transport_type.id')))

carrier = sa.Table('carrier', metadata,
                   sa.Column('id', sa.Integer, primary_key=True),
                   sa.Column('code', sa.Text),
                   sa.Column('iata', sa.Text),
                   sa.Column('title', sa.Text))

vehicle = sa.Table('vehicle', metadata,
                   sa.Column('id', sa.Integer, primary_key=True),
                   sa.Column('name', sa.Text))

transport_thread = sa.Table('transport_thread', metadata,
                            sa.Column('id', sa.Integer, primary_key=True),
                            sa.Column('number', sa.Text),
                            sa.Column('title', sa.Text),
                            sa.Column('uid', sa.Text),
                            sa.Column('carrier_id', sa.Integer, sa.ForeignKey('carrier.id')),
                            sa.Column('transport_type_id', sa.Integer, sa.ForeignKey('transport_type.id')),
                            sa.Column('vehicle_id', sa.Integer, sa.ForeignKey('vehicle.id')))

thread = sa.Table('thread', metadata,
                  sa.Column('id', sa.Integer, primary_key=True),
                  sa.Column('departure', sa.DateTime),
                  sa.Column('departure_terminal', sa.Text),
                  sa.Column('arrival', sa.DateTime),
                  sa.Column('arrival_terminal', sa.Text),
                  sa.Column('from_station_id', sa.Integer, sa.ForeignKey('station.id')),
                  sa.Column('days', sa.Text),
                  sa.Column('departuremonthday', sa.Text))


async def create_all(conn):
    await conn.execute('DROP TABLE IF EXISTS station_type CASCADE')
    await conn.execute('DROP TABLE IF EXISTS transport_type CASCADE')
    await conn.execute('DROP TABLE IF EXISTS station CASCADE')
    await conn.execute('DROP TABLE IF EXISTS carrier CASCADE')
    await conn.execute('DROP TABLE IF EXISTS vehicle CASCADE')
    await conn.execute('DROP TABLE IF EXISTS transport_thread CASCADE')
    await conn.execute('DROP TABLE IF EXISTS thread CASCADE')

    await conn.execute(CreateTable(station_type))
    await conn.execute(CreateTable(transport_type))
    await conn.execute(CreateTable(station))
    await conn.execute(CreateTable(carrier))
    await conn.execute(CreateTable(vehicle))
    await conn.execute(CreateTable(transport_thread))
    await conn.execute(CreateTable(thread))


async def go():
    engine = await create_engine(user=config.DB_USER,
                                 database=config.DB_NAME,
                                 host=config.DB_HOST,
                                 password=config.DB_PASS)
    async with engine:
        async with engine.acquire() as conn:
            await create_all(conn)
