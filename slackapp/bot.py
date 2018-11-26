from slackclient import SlackClient


class SlackBot(object):
    def __init__(self, token):
        self.token = token
        self.client = SlackClient(token)
    
    def info(self):
        bot_info = self.client.api_call(
            'auth.test'
        )
        self.name = bot_info.get('user', '')
        self.user_id = bot_info.get('user_id', '')
    
    def post_message(self, channel_or_user, message):
        if not isinstance(message, dict):
            message = {'text': message}
        
        ret = self.client.api_call(
            'chat.postMessage',
            channel=channel_or_user,
            # as_user=True,
            **message
        )
        return ret['ok']

