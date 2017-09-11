TIMEOUT = 2


class auto_remove:
    def __init__(self, container):
        self.container = container

    def __enter__(self):
        return self.container

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.container:
            self.container.stop(timeout=TIMEOUT)
            self.container.remove()


class auto_remove_multiple:
    def __init__(self, containers):
        self.containers = containers

    def __enter__(self):
        return self.containers

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.containers:
            for container in self.containers:
                container.stop(timeout=TIMEOUT)
                container.remove()
