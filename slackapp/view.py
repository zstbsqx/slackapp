
from slackapp.message import MessageText, MessageAttachment
import json


class MessageView(object):
    __callback_prefix__ = ''

    def __init__(self):
        self._text = None
        self._attachments = []
        self.context = None

    @classmethod
    def register(cls, app):
        app.register(cls.__callback_prefix__, cls)

    def init(self):
        self.on_init(self)
    
    def on_init(self):
        pass

    def text(self, text=''):
        self._text = MessageText(text=text)
        return self._text

    def attachement(self, name):
        attachment = MessageAttachment('{}____{}'.format(self.__callback_prefix__, name))
        self._attachments.append(attachment)
        return attachment

    def render(self):
        r = {}
        if self._text:
            r['text'] = self._text.render()
        if self._attachments:
            r['attachments'] = list(map(lambda x:x.render(), self._attachments))
        return r
    
    @classmethod
    def load(cls, context, data):
        o = cls()
        o.context = context
        if 'text' in data:
            _text = MessageText.load(data['text'])
            o._text = _text
        
        if 'attachments' in data:
            _attachments = list(map(lambda x: MessageAttachment.load(x), data['attachments']))
            o._attachments = _attachments
        
        return o

    def handle_action(self, action):
        action_type = action['type']
        action_name = action['name']


    def handle_event(self, event):
        pass

    def to_json(self):
        return json.dumps(self.render())
