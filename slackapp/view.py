from slackapp.logging import logger
from slackapp.component.message import Message


class ActionHandler(object):

    def __init__(self, callback_id, action_name, callback):
        self.callback_id = callback_id
        self.action_name = action_name
        self.callback = callback

    @classmethod
    def register(cls, callback_id, action_name):
        def make_handler(f):
            if not callable(f):
                raise TypeError('ActionHandler must be a callable')
            return cls(callback_id, action_name, f)
        return make_handler

    def __call__(self, msg, context):
        return self.callback(msg, context)


on_action = ActionHandler.register


class classproperty(object):

    def __init__(self, method):
        self.method = method

    def __get__(self, obj, cls):
        return self.method(cls)


class MessageView(object):

    @classproperty
    def action_handlers(cls):
        if getattr(cls, '_action_handlers', None) is None:
            cls._action_handlers = cls._build_action_handler_mapping()
        return cls._action_handlers

    @classmethod
    def _build_action_handler_mapping(cls):
        result = {}
        for k, v in cls.__dict__.items():
            if isinstance(v, ActionHandler):
                logger.debug('Adding handler for callback_id "{}" action "{}"'.format(v.callback_id, v.action_name))
                if (v.callback_id, v.action_name) in result:
                    raise KeyError('Duplicate entry for action {}'.format(v.action_name))
                result[(v.callback_id, v.action_name)] = v
        return result

    def __init__(self, msg=None, context=None):
        self.msg = msg or self.init_msg
        self.context = context

    def handle_action(self, callback_id, action_name, action_value):
        handler = self.action_handlers.get((callback_id, action_name))
        if callable(handler):
            return handler(self, action_value)

    @property
    def init_msg(self):
        return Message()

    def reset(self):
        self.msg = self.init_msg

    def clear(self):
        self.msg = Message()
