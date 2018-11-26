import json

from slackclient import SlackClient

from slackapp.bot import SlackBot
from slackapp.view import MessageView
from slackapp.context import ActionContext, EventContext
from slackapp.component.message import Message, MessageContext, MessageText
from slackapp.logging import logger


class SlackApp(object):

    def __init__(self, name):
        self.name = name
        self.config = {}
        self._client = None
        self._bot = None
        self._id_view_mapping = {}
        self._event_handlers = {}
    
    def setup_config(self, access_token, bot_access_token, signing_secret=None):
        self.config.update({
            'signing_secret': signing_secret,
            'access_token': access_token,
            'bot_access_token': bot_access_token
        })
        
    @property
    def client(self):
        if not self._client:
            self._client = SlackClient(self.config['access_token'])
        return self._client

    @property
    def bot(self):
        if not self._bot:
            self._bot = SlackBot(self.config['bot_access_token'])
            self._bot.info()
        return self._bot

    def register_view(self, view_cls):
        logger.info('Registering view class {}'.format(view_cls.__name__))
        if not issubclass(view_cls, MessageView):
            raise Exception('view_cls must be inherited from MessageView')
        for (callback_id, action_name) in view_cls.action_handlers.keys():
            if self._id_view_mapping.get(callback_id, view_cls) != view_cls:
                raise KeyError('Multiple view classes handling callback_id {}'.format(callback_id))
            self._id_view_mapping[callback_id] = view_cls

    def handle_action_request(self, data):
        action_type = data['type']
        if action_type == 'interactive_message':
            return self.handle_interactive_message(data)
        elif action_type == 'dialog_submission':
            return {}
        elif action_type == 'message_action':
            return {}

    def handle_interactive_message(self, data):
        # find corresponding view
        callback_id = data['callback_id']
        view_cls = self._id_view_mapping.get(callback_id)
        if view_cls is None:
            logger.warning('No handler for callback_id "{}"'.format(callback_id))
            return
        # construct view object
        message = Message.load(data['original_message'])
        context = ActionContext(
            data['type'], data['team']['id'], data['channel']['id'], data['user']['id'], data['action_ts'],
            data['message_ts'], data['attachment_id'], data['token'], data['response_url']
        )
        view_instance = view_cls(message, context)
        # handle actions
        for action in data['actions']:
            name = action['name']
            if action.get('type') == 'button':
                value = action['value']
            else:
                value = action['selected_options'][0]['value']
            view_instance.handle_action(callback_id, name, value)
        return view_instance.msg.render()

    def handle_command_request(self, data):
        pass

    def handle_event_request(self, data):
        request_type = data['type']
        if request_type == 'event_callback':
            return self.handle_event(data)
        elif request_type == 'url_verification':
            token = data['token']
            challenge = data['challenge']
            return {'challenge': challenge}

    def handle_event(self, data):
        event_type = data['event']['type']
        handler = self._event_handlers.get(event_type)
        if handler is None:
            logger.warning('No handler for event "{}"'.format(event_type))
        else:
            event_data = data['event']  # TODO: use class instead of dict
            context = EventContext(data['token'], data['team_id'], data['api_app_id'], data['event_id'],
                                   data['event_time'], data['authed_users'])
            handler(event_data, context)    # TODO: error handling
        return {'text': 'ok'}

    def send_view(self, view_cls, slack_user_id):
        view_instance = view_cls()
        self.bot.post_message(slack_user_id, view_instance.msg.render())

    def on_event(self, event):
        def _handle_event_decorator(func):
            logger.debug('Adding handler for event {}'.format(event))
            if not callable(func):
                raise TypeError('Event handler must be a callable')
            if event in self._event_handlers:
                raise KeyError('Multiple event handlers for event {}'.format(event))
            self._event_handlers[event] = func
            return func
        return _handle_event_decorator

    def mount_flask(self, flaskapp, url_prefix=''):
        from slackapp.flaskext import mount_flask
        url_prefix = url_prefix or '/slackapp/{}'.format(self.name)
        mount_flask(self, flaskapp, url_prefix)
