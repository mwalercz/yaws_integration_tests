BROKER_SETTINGS = dict(
    image='mwalercz/dq_broker',
    name='broker',
    command='broker -c env.ini',
    environment={
        'BROKER_DATABASE_HOSTNAME': 'postgres',
        'BROKER_WEBSOCKET_PING_INTERVAL': '1',
        'BROKER_WEBSOCKET_PING_TIMEOUT': '1'
    },
    detach=True,
    network_mode='bridge',
    links=[('postgres', 'postgres')],
    ports={
        '9001/tcp': ('127.0.0.1', 9001),
        '443/tcp': ('127.0.0.1', 443)
    },
    hostname='broker',
)

POSTGRES_SETTINGS = dict(
    image='postgres:9.3-alpine',
    name='postgres',
    environment={
        'POSTGRES_USER': 'dq_broker',
        'POSTGRES_PASSWORD': 'dq_broker',
        'POSTGRES_DB': 'dq_broker',
        'PGDATA': '/dev/shm/pgdata/data',
    },
    hostname='postgres',
    network_mode='bridge',
    detach=True,
)

WORKER_SETTINGS = dict(
    image='mwalercz/dq_worker',
    command='worker -c env.ini',
    environment={
        'BROKER_URL': 'wss://broker:9000',
        'SSH_HOST': '127.0.0.1',
    },
    network_mode='bridge',
    links=[('broker', 'broker')],
    detach=True,
)
