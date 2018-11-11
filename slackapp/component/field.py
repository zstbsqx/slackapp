# -*- encoding: utf-8 -*-
class MessageField(object):

    def __init__(self, title, value, short=False):
        self.title = title
        self.value = value
        self.short = short

    def render(self):
        return {
            'title': self.title,
            'value': self.value,
            'short': self.short
        }

    @classmethod
    def load(cls, data):
        return cls(data['title'], data['value'], data['short'])
