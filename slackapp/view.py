
from slackapp.message import MessageText, MessageAttachment, MessageButton
import json


class MessageView(object):
    __callback_prefix__ = ''

    def __init__(self):
        self._text = None
        self._attachments =  []
        self.context = None
        self.app = None

    def init(self):
        self.on_init(self)
    
    def on_init(self):
        pass
    
    def reset(self):
        self._text = None
        self._attachments = []

    def text(self, text=''):
        self._text = MessageText(text=text)
        return self._text

    def attachement(self, name):
        attachment = MessageAttachment('{}____{}'.format(self.__callback_prefix__, name))
        self._attachments.append(attachment)
        return attachment
    
    def get_action(self, name, atype):
        for attachment in self._attachments:
            action = attachment.get_action(name, atype)
            if action:
                return action
        return None

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
        action_obj = self.get_action(action_name, action_type)
        if action_obj:
            return self.on_action(action_obj, action.get('value', ''))
        else:
            return self.response('Oops.')


    def on_action(self, action, action_value):
        if isinstance(action, MessageButton):
            handler_name = 'on_{}_clicked'.format(action.name)
            handler = getattr(self, handler_name, None)
            if callable(handler):
                ret = handler() or self
                return self.response(ret)
        
        return self.response('No handler or not response.')
            

    def to_json(self):
        return json.dumps(self.render())
    
    def response(self, ret):
        if isinstance(ret, MessageView):
            return ret.render() or {}
        elif isinstance(ret, dict):
            return ret
        elif isinstance(ret, str):
            return MessageText(ret).response()
        else:
            return ret or {}
