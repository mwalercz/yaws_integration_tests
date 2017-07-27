BROKER_SETTINGS = dict(
    image='mwalercz/dq_broker',
    command='broker -c env.ini',
    environment={
        'BROKER_DATABASE_HOSTNAME': 'postgres'
    },
    detach=True,
    hostname='broker',
)

POSTGRE_SETTINGS = dict(
    image='postgres:9.3-alpine',
    environment={
        'POSTGRES_USER': 'dq_broker',
        'POSTGRES_PASSWORD': 'dq_broker',
        'POSTGRES_DB': 'dq_broker',
        'PGDATA': '/dev/shm/pgdata/data',
    },
    hostname='postgres',
    detach=True
)