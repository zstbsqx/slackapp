
from slackclient import SlackClient
from dock.common import cached_property

class SlackApp(object):
    def __init__(self, name, access_token, bot_access_token):
        self.name = name
        self.access_token = access_token
        self.bot_access_token = bot_access_token

    
    @cached_property
    def client(self):
        return SlackClient(self.access_token)

    
    @cached_property
    def bot(self):
        return SlackClient(self.bot_access_token)

    

    def handle_request(self, data):
        request_type = data.get('type', '')
        if request_type == 'interactive_message':
            self.handle_actions(data)
        
    def handle_actions(self, data):
        pass