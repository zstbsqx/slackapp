
from slackclient import SlackClient
from slackapp.view import MessageView
from slackapp.message import MessageContext, MessageText


class SlackApp(object):
    def __init__(self, name):
        self.name = name
        self._client = None
        self._bot = None
        self._views = {}
        self.config = {}
    
    def setup_config(self, signing_secret, access_token='access_token', 
            bot_access_token='bot_access_token', **kwargs):
        self.config.update(dict(
            signing_secret = signing_secret,
            access_token = access_token,
            bot_access_token = bot_access_token
        ))
        

    @property
    def client(self):
        if not self._client:
            self._client = SlackClient(self.config['access_token'])
        return self._client

    
    @property
    def bot(self):
        if not self._bot:
            self._bot = SlackClient(self.config['bot_access_token'])
        return self._bot

    

    def handle_request(self, data):
        request_type = data.get('type', '')
        if request_type == 'interactive_message':
            return self.handle_actions(data)
        elif request_type == 'dialog_submission':
            pass
        elif request_type == 'event_callback':
            pass
        elif request_type == 'message_action':
            pass
        return MessageText('No right handler or not return valid response').response()
    
    def register(self, view_id, view_cls):
        if not issubclass(view_cls, MessageView):
            raise Exception('view_cls must be inherited from MessageView')
        if view_id not in self._views:
            self._views[view_id] = view_cls
        else:
            raise Exception('view_id {} exits'.format(view_id))

    def send_view(self, view_class, slack_user_id):
        view_instance = view_class()
        view_instance.init()
        self.bot.api_call(
                "chat.postMessage",
                channel=slack_user_id,
                as_user = True,
                **view_instance.render()
                )


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
            action = actions[0] if actions else None
            if not action:
                return {}
            return view.handle_action(action) or MessageText('{} handle_action not response valid.'.format(view_cls.__name__)).response()
        return {}
    
    def handle_slack_event(self, data):
        event_type = data.get('type', '')
        if event_type == 'url_verification':
            token = data.get('token','')
            challenge = data.get('challenge', '')
            return dict(challenge=challenge)
        elif event_type == 'event_callback':
            sub_event_type = data.get('event', {}).get('type', '')
            if sub_event_type == 'app_mention':
                return self.on_app_mention()
            else:
                event_handler = getattr(self, 'on_slack_{}'.format(sub_event_type), None)
                if callable(event_handler):
                    return event_handler() or dict()
                return dict(text="No event handler")
    
    def on_slack_app_mention(self):
        pass
    
    def on_slack_message(self):
        pass