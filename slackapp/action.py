

class MessageButton(object):
    def __init__(self, name, text):
        self.name = name
        self.text = text
        self.type = 'button'
        self._style = 'default'
        self._value = ''
        self._confirm = {}
        self._click_handler = None

    
    def style(self, style):
        self._style = style

    def value(self, value):
        self._value = value

    def on_click(self, click_handler):
        self._click_handler = click_handler

    def confirm(self, title, text, ok_text='', dismiss_text='')
        confirm_dict = dict(title=title, text=text)
        if ok_text:
            confirm_dict['ok_text'] = ok_text
        if dismiss_text:
            confirm_dict['dismiss_text'] = dismiss_text
        self._confirm = confirm_dict

    def render(self):
        rst = dict(name= self.name,
            text = self.text,
            type = self.type,
            style = self._style
        )
        if self._value:
            rst['value'] = self._value

        if self._confirm:
            rst['confirm'] = self._confirm
        return rst


class MessageMenu(object):
    pass


class MessageChannelMenu(MessageMenu):
    pass


class MessageUserMenu(MessageMenu):
    pass