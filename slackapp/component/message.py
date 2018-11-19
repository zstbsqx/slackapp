from collections import namedtuple

from slackapp.component.attachment import MessageAttachment


SlackTeam = namedtuple('SlackTeam', ['id', 'domain'])
SlackChannel = namedtuple('SlackChannel', ['id', 'name'])
SlackUser = namedtuple('SlackUser', ['id', 'name'])


def to_utf8(s, enc='utf8'):
    if s is None:
        return None
    return s.encode(enc) if isinstance(s, unicode) else str(s)


def slack_escape(text):
    #text = to_utf8(text)
    return text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


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


class Message(object):

    def __init__(self, text=None, attachments=None, thread_ts=None, response_type='in_channel'):
        self.text = text
        self.attachments = attachments
        self.thread_ts = thread_ts
        self.response_type = response_type

    def attachment(self):
        attachment = MessageAttachment()
        if self.attachments is None:
            self.attachments = []
        self.attachments.append(attachment)
        return attachment

    def render(self):
        result = {}
        for key in ('text', 'thread_ts', 'response_type'):
            value = getattr(self, key)
            if value is not None:
                result[key] = value
        if self.attachments:
            result['attachments'] = [att.render() for att in self.attachments]
        return result

    @classmethod
    def load(cls, data):
        params = {}
        for key in ('text', 'thread_ts', 'response_type'):  # maybe there are some other strange
            params[key] = data.get(key)
        attachments = data.get('attachments')
        if attachments:
            params['attachments'] = [MessageAttachment.load(att) for att in attachments]
        return cls(**params)
