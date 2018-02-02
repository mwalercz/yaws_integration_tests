BROKER_SETTINGS = dict(
    image='dist-queue/yawsm',
    name='yawsm',
    command='yawsm -c env.ini',
    environment={
        'YAWSM_DATABASE_HOSTNAME': 'postgres',
        'YAWSM_WEBSOCKET_PING_INTERVAL': '1',
        'YAWSM_WEBSOCKET_PING_TIMEOUT': '1',
        'YAWSM_DEFAULT_ADMIN_USERNAME': 'admin',
    },
    detach=True,
    network_mode='bridge',
    links=[('postgres', 'postgres')],
    ports={
        '9001/tcp': ('127.0.0.1', 9001),
        '443/tcp': ('127.0.0.1', 443)
    },
    hostname='yawsm',
)

POSTGRES_SETTINGS = dict(
    image='postgres:9.3-alpine',
    name='postgres',
    environment={
        'POSTGRES_USER': 'yawsm',
        'POSTGRES_PASSWORD': 'yawsm',
        'POSTGRES_DB': 'yawsm',
        'PGDATA': '/dev/shm/pgdata/data',
    },
    hostname='postgres',
    network_mode='bridge',
    detach=True,
)

WORKER_SETTINGS = dict(
    image='dist-queue/yawsd',
    command='yawsd -c env.ini',
    environment={
        'BROKER_URL': 'wss://yawsm:9000',
        # 'SSH_HOST': '127.0.0.1',
    },
    network_mode='bridge',
    links=[('yawsm', 'yawsm')],
    detach=True,
)
