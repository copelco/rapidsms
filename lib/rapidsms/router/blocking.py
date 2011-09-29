import copy

from django.conf import settings

from .base import BaseRouter


class BlockingRouter(BaseRouter):
    """ Simple router that blocks while sending and receiving messages """

    def __init__(self, *args, **kwargs):
        """
        Apps and backends are added manually to the blocking backend.
        """
        super(BlockingRouter, self).__init__(*args, **kwargs)
        apps = settings.INSTALLED_APPS
        backends = settings.INSTALLED_BACKENDS
        for name in apps:
            try:
                self.add_app(name)
            except Exception as e:
                self.exception(e)
        for name, conf in backends.iteritems():
            parsed_conf = copy.copy(conf)
            engine = parsed_conf.pop('ENGINE')
            self.add_backend(name, engine, parsed_conf)

    def incoming(self, msg):
        # process incoming phases
        super(BlockingRouter, self).incoming(msg)
        # handle message responses from within router
        for response in msg.responses:
            self.outgoing(response)

    def outgoing(self, msg):
        # process outgoing phase
        super(BlockingRouter, self).outgoing(msg)
        # send message from within router
        self.sent = self.backends[msg.connection.backend.name].send(msg)
        msg.sent = self.sent