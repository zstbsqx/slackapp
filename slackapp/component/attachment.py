# -*- encoding: utf-8 -*-
from slackapp.component.field import MessageField
from slackapp.component.action import MessageButton, MessageStaticMenu, MessageUserMenu, MessageChannelMenu,\
    MessageConversationMenu, parse_action


class MessageAuthor(object):
    def __init__(self, author_name, author_link=None, author_icon=None):
        self.author_name = author_name
        self.author_link = author_link
        self.author_icon = author_icon

    def render(self):
        result = {}
        for key in ('author_name', 'author_link', 'author_icon'):
            value = getattr(self, key)
            if value is not None:
                result[key] = value
        return result


class MessageTitle(object):
    def __init__(self, title, title_link=None):
        self.title = title
        self.title_link = title_link

    def render(self):
        result = {}
        for key in ('title', 'title_link'):
            value = getattr(self, key)
            if value is not None:
                result[key] = value
        return result


class MessageFooter(object):
    def __init__(self, footer, footer_icon=None):
        self.footer = footer
        self.footer_icon = footer_icon

    def render(self):
        result = {}
        for key in ('footer', 'footer_icon'):
            value = getattr(self, key)
            if value is not None:
                result[key] = value
        return result


class MessageAttachment(object):

    def __init__(self, fallback='Upgrade your Slack', color=None, pretext=None, msg_author=None, msg_title=None,
                 text=None, fields=None, image_url=None, thumb_url=None, msg_footer=None, ts=None,
                 callback_id=None, actions=None):
        self.fallback = fallback
        self.color = color
        self.pretext = pretext
        self.msg_author = msg_author if isinstance(msg_author, (MessageAuthor, type(None))) else MessageAuthor(msg_author)
        self.msg_title = msg_title if isinstance(msg_title, (MessageTitle, type(None))) else MessageTitle(msg_title)
        self.text = text
        self.fields = fields
        self.image_url = image_url
        self.thumb_url = thumb_url
        self.msg_footer = msg_footer if isinstance(msg_footer, (MessageFooter, type(None))) else MessageFooter(msg_footer)
        self.ts = ts
        self.callback_id = callback_id
        self.actions = actions
        self.attachment_type = 'default'    # There's no other type now.

    def author(self, author, author_link=None, author_icon=None):
        self.msg_author = MessageAuthor(author, author_link, author_icon)
        return self

    def title(self, title, title_link=None):
        self.msg_title = MessageTitle(title, title_link)
        return self

    def footer(self, footer, footer_icon=None):
        self.msg_footer = MessageFooter(footer, footer_icon)
        return self

    def field(self, title, value, short=False):
        field = MessageField(title, value, short)
        if self.fields is None:
            self.fields = []
        self.fields.append(field)
        return self

    def _add_action(self, action):
        if self.actions is None:
            self.actions = []
        self.actions.append(action)

    def button(self, name, text, value=None, action_confirm=None, style=None):
        button = MessageButton(name, text, value, action_confirm, style)
        self._add_action(button)
        return self

    def static_menu(self, name, text, value=None, action_confirm=None, options=None, option_groups=None,
                    selected_option=None):
        menu = MessageStaticMenu(name, text, value, action_confirm, options, option_groups, selected_option)
        self._add_action(menu)
        return self

    def user_menu(self, name, text, value=None, action_confirm=None, selected_user=None):
        menu = MessageUserMenu(name, text, value, action_confirm, selected_user)
        self._add_action(menu)
        return self

    def channel_menu(self, name, text, value=None, action_confirm=None, selected_channel=None):
        menu = MessageChannelMenu(name, text, value, action_confirm, selected_channel)
        self._add_action(menu)
        return self

    def conversation_menu(self, name, text, value=None, action_confirm=None, selected_conversation=None):
        menu = MessageConversationMenu(name, text, value, action_confirm, selected_conversation)
        self._add_action(menu)
        return self

    @classmethod
    def load(cls, data):
        params = {}
        for key in ('fallback', 'color', 'pretext', 'text', 'image_url', 'thumb_url', 'ts', 'callback_id'):
            params[key] = data.get(key)
        fields = data.get('fields')
        if fields:
            params['fields'] = map(MessageField.load, fields)
        actions = data.get('actions')
        if actions:
            params['actions'] = map(parse_action, data.get('actions', actions))
        if data.get('author_name'):
            params['msg_author'] = MessageAuthor(data['author_name'], data.get('author_link'), data.get('author_icon'))
        if data.get('title'):
            params['msg_title'] = MessageTitle(data['title'], data.get('title_link'))
        if data.get('footer'):
            params['msg_footer'] = MessageFooter(data['footer'], data.get('footer_icon'))
        return cls(**params)

    def render(self):
        result = {}
        for key in ('fallback', 'color', 'pretext', 'text', 'image_url', 'thumb_url', 'ts',
                    'callback_id', 'attachment_type'):
            value = getattr(self, key)
            if value is not None:
                result[key] = value
        for key in ('msg_author', 'msg_title', 'msg_footer'):
            value = getattr(self, key)
            if value is not None:
                result.update(value.render())
        for key in ('actions', 'fields'):
            value = getattr(self, key)
            if value is not None:
                result[key] = [item.render() for item in value]
        return result
