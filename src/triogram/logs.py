import logging


class ContextVarAdapter(logging.LoggerAdapter):

    def process(self, msg, kwargs):
        kwargs.setdefault('extra', {})[self.extra.name] = self.extra.get()
        return msg, kwargs
