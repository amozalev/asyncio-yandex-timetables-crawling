from aiopg.sa import create_engine
import sqlalchemy as sa
import config

metadata = sa.MetaData()

station = sa.Table('station', metadata,
                   sa.Column('id', sa.Sequence),
                   sa.Column('code', sa.Text),
                   sa.Column('title', sa.Text),
                   sa.Column('station_type_id', sa.Integer, sa.ForeignKey('station_type.id')),
                   sa.Column('transport_type_id', sa.Integer, sa.ForeignKey('transport_type.id'))
                   )

station_type = sa.Table('station_type', metadata,
                        sa.Column('id', ),
                        sa.Column('title', sa.Text)
                        )

transport_type = sa.Table('transport_type', metadata,
                          sa.Column('id', ),
                          sa.Column('number', ),
                          sa.Column('title', sa.Text),
                          sa.Column('uid', sa.Text),
                          sa.Column('carrier_id', ),
                          sa.Column('transport_type_id', ),
                          sa.Column('vehicle_id', )
                          )

carrier = sa.Table('carrier', metadata,
                   sa.Column('id', ),
                   sa.Column('code', sa.Text),
                   sa.Column('iata', sa.Text),
                   sa.Column('title', sa.Text)
                   )

vehicle = sa.Table('vehicle', metadata,
                   sa.Column('id', ),
                   sa.Column('name', sa.Text)
                   )

transport_thread = sa.Table('vehicle', metadata,
                            sa.Column('id', ),
                            sa.Column('number', sa.Text),
                            sa.Column('title', sa.Text),
                            sa.Column('uid', sa.Text),
                            sa.Column('carrier_id', ),
                            sa.Column('transport_type_id', ),
                            sa.Column('vehicle_id', )
                            )

thread = sa.Table('vehicle', metadata,
                  sa.Column('departure', sa.DateTime),
                  sa.Column('departure_terminal', sa.Text),
                  sa.Column('arrival', sa.DateTime),
                  sa.Column('arrival_terminal', sa.Text),
                  sa.Column('from_station_id', ),
                  sa.Column('days', sa.Text),
                  sa.Column('departuremonthday', sa.Text),
                  sa.Column('thread_id')
                  )


async def go():
    engine = await create_engine(user=config.DB_USER,
                                 database=config.DB_NAME,
                                 host=config.DB_HOST,
                                 password=config.DB_PASS)
    async with engine:
        async with engine.acquire() as conn:
            # await create_tables(conn)
            pass
