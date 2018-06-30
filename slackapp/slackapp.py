
from slackclient import SlackClient
from dock.common import cached_property

class SlackApp(object):
    def __init__(self, name, access_token, bot_access_token):
        self.name = name
        self.access_token = access_token
        self.bot_access_token = bot_access_token
        self._client = None
        self._bot = None

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


    def handle_actions(self, data):
        pass