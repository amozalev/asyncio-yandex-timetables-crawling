from aiopg import create_pool
import sqlalchemy as sa
# from sqlalchemy.schema import CreateTable, DropTable, CreateSequence, DropSequence
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
                   sa.Column('title', sa.Text))

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
                  sa.Column('departure_date', sa.DateTime),
                  sa.Column('departure_terminal', sa.Text),
                  sa.Column('to_station_id', sa.Integer, sa.ForeignKey('station.id')),
                  sa.Column('arrival_date', sa.DateTime),
                  sa.Column('arrival_terminal', sa.Text),
                  sa.Column('from_station_id', sa.Integer, sa.ForeignKey('station.id')),
                  sa.Column('days', sa.Text))


# sa.Column('departuremonthday', sa.Text))


async def create_all():
    dsn = f'dbname={config.DB_NAME} user={config.DB_USER} password={config.DB_PASS} host={config.DB_HOST} port=5432'
    pool = await create_pool(dsn)

    with (await pool.cursor()) as cur:
        await cur.execute('DROP TABLE IF EXISTS station_type CASCADE')
        await cur.execute('DROP TABLE IF EXISTS transport_type CASCADE')
        await cur.execute('DROP TABLE IF EXISTS station CASCADE')
        await cur.execute('DROP TABLE IF EXISTS carrier CASCADE')
        await cur.execute('DROP TABLE IF EXISTS vehicle CASCADE')
        await cur.execute('DROP TABLE IF EXISTS transport_thread CASCADE')
        await cur.execute('DROP TABLE IF EXISTS thread CASCADE')

        await cur.execute('''CREATE TABLE station_type(
                                                      id SERIAL PRIMARY KEY, 
                                                      title TEXT)''')

        await cur.execute('''CREATE TABLE transport_type(
                                                        id SERIAL PRIMARY KEY,
                                                        title TEXT)''')

        await cur.execute('''CREATE TABLE station(
                                                  id SERIAL PRIMARY KEY, 
                                                  code TEXT, 
                                                  title TEXT, 
                                                  station_type_id INT REFERENCES station_type(id),
                                                  transport_type_id INT REFERENCES transport_type(id))''')

        await cur.execute('''CREATE TABLE carrier(
                                                  id SERIAL PRIMARY KEY,
                                                  code TEXT,
                                                  iata TEXT,
                                                  title TEXT)''')

        await cur.execute('''CREATE TABLE vehicle(
                                                  id SERIAL PRIMARY KEY,
                                                  title TEXT)''')

        await cur.execute('''CREATE TABLE transport_thread(
                                                          id SERIAL PRIMARY KEY,
                                                          number TEXT,
                                                          title TEXT,
                                                          uid TEXT,
                                                          carrier_id INT REFERENCES carrier(id),
                                                          transport_type_id INT REFERENCES transport_type(id),
                                                          vehicle_id INT REFERENCES vehicle(id))''')

        await cur.execute('''CREATE TABLE thread(
                                                id SERIAL PRIMARY KEY,
                                                departure_date TIMESTAMP WITHOUT TIME ZONE,
                                                departure_terminal TEXT,
                                                to_station_id INT REFERENCES station(id),
                                                arrival_date TIMESTAMP WITHOUT TIME ZONE,
                                                arrival_terminal TEXT,
                                                from_station_id INT REFERENCES station(id),
                                                days TEXT)''')

    return pool
