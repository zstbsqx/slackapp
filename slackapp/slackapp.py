
from slackclient import SlackClient
from slackapp.view import MessageView
from slackapp.message import MessageContext


class SlackApp(object):
    def __init__(self, name, access_token, bot_access_token):
        self.name = name
        self.access_token = access_token
        self.bot_access_token = bot_access_token
        self._client = None
        self._bot = None
        self._views = {}

    @property
    def client(self):
        if not self._client:
            self._client = SlackClient(self.access_token)
        return self._client

    
    @property
    def bot(self):
        if not self._bot:
            self._bot = SlackClient(self.bot_access_token)
        return self._bot

    

    def handle_request(self, data):
        request_type = data.get('type', '')
        if request_type == 'interactive_message':
            self.handle_actions(data)
        elif request_type == 'dialog_submission':
            pass
        elif request_type == 'event_callback':
            pass
        elif request_type == 'message_action':
            pass
    
    def register(self, view_id, view_cls):
        if not isinstance(view_cls, MessageView):
            raise Exception('view_cls must be inherited from MessageView')
        if view_id not in self._views:
            self._views[view_id] = view_cls
        else:
            raise Exception('view_id {} exits'.format(view_id))


    def handle_actions(self, data):
        original_message = data.get('original_message')
        callback_id = data['callback_id']
        view_id = callback_id.split('____')[0]
        view_cls = self._views.get(view_id)
        context = MessageContext.load(data, bot=self.bot, client=self.client)
        if original_message:
            if not view_cls:
                raise Exception('View not defined')
            view = view_cls.load(context, original_message)
            actions = data['actions']
            for action in actions:
                view.handle_action(action)