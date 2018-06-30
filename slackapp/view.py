
from .message import Message
from .message import MessageText, MessageAttachment
import json

class MessageView(object):
    __callback_id = ''

    def __init__(self):
        self._text = None
        self._attachments = []

    @classmethod
    def register(cls, app):
        app.register(cls.__callback_id, cls)

    def init(self):
        self.on_init(self)
    
    def on_init(self):
        pass

    def text(self, text=''):
        self._text = MessageText(text=text)
        return self._text

    def attachement(self, ):
        attachment = MessageAttachment()
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
    def load(cls, data):
        o = cls()
        if 'text' in data:
            _text = MessageText.load(data['text'])
            o._text = _text
        
        if 'attachments' in data:
            _attachments = list(map(lambda x: MessageAttachment.load(x), data['attachments']))
            o._attachments = _attachments
        
        return o

    def handle_event(self, event):
        pass

    def to_json(self):
        return json.dumps(self.render())
