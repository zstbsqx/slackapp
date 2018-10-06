from collections import namedtuple

def to_utf8(s, enc='utf8'):
    if s is None:
        return None
    return s.encode(enc) if isinstance(s, unicode) else str(s)

def slack_escape(text):
    #text = to_utf8(text)
    return text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

SlackTeam = namedtuple('SlackTeam', ['id', 'domain'])
SlackChannel = namedtuple('SlackChannel', ['id', 'name'])
SlackUser = namedtuple('SlackUser', ['id', 'name'])


class MessageContext(object):
    def __init__(self):
        self.bot = None
        self.client = None
        self.team = None
        self.channel = None
        self.user = None
    
    @classmethod
    def load(cls, data, bot=None, client=None):
        o = cls()
        o.bot = bot
        o.client = client
        team = data['team']
        o.team = SlackTeam(id=team['id'], domain=team['domain'])
        channel = data['channel']
        o.channel = SlackChannel(id=channel['id'], name=channel['name'])
        user = data['user']
        o.user = SlackUser(id=user['id'], name=user['name'])
        return o

class MessageText(object):
    def __init__(self, text=''):
        self._texts = []
        if text:
            self._texts.append(text)
    
    def text(self, text):
        escaped = slack_escape(text)
        self._texts.append(escaped)

    def url(self, url):
        escaped = slack_escape(url)
        self._texts.append(' {}'.format(escaped))
    
    def date(self, epoch_ts, text, fallback_text=''):
        '''
            <!date^unix_epoch_timestamp^string_containing_date_tokens^optional_link|fallback_text>
        Describe your date and time as a string, using any of the following tokens:
            {date_num} is displayed as 2014-02-18. It will include leading zeros before the month and date and is probably best for more technical integrations that require a developer-friendly date format.
            {date} is displayed as February 18th, 2014.
            {date_short} is displayed as Feb 18, 2014.
            {date_long} is displayed as Tuesday, February 18th, 2014.
            {date_pretty} displays the same as {date} but uses "yesterday", "today", or "tomorrow" where appropriate.
            {date_short_pretty} displays the same as {date_short} but uses "yesterday", "today", or "tomorrow" where appropriate.
            {date_long_pretty} displays the same as {date_long} but uses "yesterday", "today", or "tomorrow" where appropriate.
            {time} is displayed as 6:39 AM or 6:39 PM in 12-hour format. If the client is set to show 24-hour format, it is displayed as 06:39 or 18:39.
            {time_secs} is displayed as 6:39:45 AM 6:39:42 PM in 12-hour format. In 24-hour format it is displayed as 06:39:45 or 18:39:42.
        
        Examples:
            <!date^1392734382^Posted {date_num} {time_secs}|Posted 2014-02-18 6:39:42 AM> will display as: Posted 2014-02-18 6:39:42 AM
            <!date^1392734382^{date} at {time}|February 18th, 2014 at 6:39 AM PST> will display as: February 18th, 2014 at 6:39 AM
        '''
        escaped = slack_escape(text)
        self._texts.append('<!date^{}^{}|{}>'.format(epoch_ts, escaped, fallback_text))

    def pre(self, text):
        escaped = slack_escape(text)        
        self._texts.append('```{}```'.format(escaped))
    
    def code(self, text):
        escaped = slack_escape(text)        
        self._texts.append('`{}`'.format(escaped))
    
    def italic(self, text):
        escaped = slack_escape(text)        
        self._texts.append('_{}_'.format(escaped))

    def bold(self, text):
        escaped = slack_escape(text)        
        self._texts.append('*{}*'.format(escaped))

    def strike(self, text):
        escaped = slack_escape(text)        
        self._texts.append('~{}~'.format(escaped))


    def newline(self):
        self._texts.append('\n')

    @classmethod
    def load(cls, text):
        o = cls(text)
        return o

    def render(self):
        text = ''.join(self._texts)
        return text
    
    def response(self):
        return dict(
            text = self.render()
        )



class MessageAttachment(object):
    def __init__(self, callback_id):
        self._dict = {}
        self._actions = []
        self.callback_id = callback_id

    def fallback(self, text):
        pass
    
    def title(self, title):
        self._dict['title'] = slack_escape(title)
    
    def title_link(self, title_link):
        self._dict['title_link'] = title_link

    def text(self, text):
        self._dict['text'] = slack_escape(text)
    
    def color(self, color):
        self._dict['color'] = color
    
    def image_url(self, image_url):
        self._dict['image_url'] = image_url
    
    def fields(self, title, value, short=True):
        fields_list = self._dict.setdefault('fields', [])
        fields_list.append(dict(title=title, value=value, short=short))

    @property
    def actions(self):
        return self._actions

    def get_action(self, name, atype):
        for action in self._actions:
            if action.name == name and action.type == atype:
                return action
        return None

    def button(self, name, text):
        btn = MessageButton(name, text)
        self._actions.append(btn)
        return btn
    
    def menu(self):
        act_menu = MessageMenu()
        self._actions.append(act_menu)
        return act_menu

    @classmethod
    def load(cls, data):
        callback_id = data['callback_id']
        o = cls(callback_id)
        for key in ('title', 'title_link', 'text', 'color', 'image_ur', 'fields'):
            if key in data:
                o._dict[key] = data[key]
        if 'actions' in data:
            for action in data['actions']:
                action_type = action['type']
                if action_type == 'button':
                    o._actions.append(MessageButton.load(action))
                elif action_type == 'select':
                    pass
        return o


    def render(self):
        r = dict(self._dict)
        if self._actions:
            r['actions'] = list(map(lambda x: x.render(), self._actions))
        r['callback_id'] = self.callback_id
        return r


class MessageButton(object):
    def __init__(self, name, text):
        self.name = name
        self.text = text
        self.type = 'button'
        self._style = 'default'
        self._value = ''
        self._confirm = {}

    
    def style(self, style):
        self._style = style

    def value(self, value):
        self._value = value

    def confirm(self, title, text, ok_text='', dismiss_text=''):
        confirm_dict = dict(title=title, text=text)
        if ok_text:
            confirm_dict['ok_text'] = ok_text
        if dismiss_text:
            confirm_dict['dismiss_text'] = dismiss_text
        self._confirm = confirm_dict

    @classmethod
    def load(cls, data):
        name = data.get('name', '')
        text = data.get('text', '')
        o = cls(name, text)
        for key in ('type',):
            if key in data:
                setattr(o, key, data[key])
        for key in ('style', 'value', 'confirm'):
            if key in data:
                setattr(o, '_{}'.format(key), data[key])
        return o

        
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