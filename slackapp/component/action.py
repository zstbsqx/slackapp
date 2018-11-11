# -*- encoding: utf-8 -*-
from slackapp.object import SlackUser, SlackChannel, SlackConversation


class ActionConfirm(object):

    def __init__(self, text, title=None, ok_text=None, dismiss_text=None):
        self.text = text
        self.title = title
        self.ok_text = ok_text
        self.dismiss_text = dismiss_text

    def render(self):
        result = {
            'title': self.title,
            'text': self.text,
            'ok_text': self.ok_text,
            'dismiss_text': self.dismiss_text
        }
        return {k: v for k, v in result.items() if v is not None}


class MessageAction(object):

    def __init__(self, name, text, type, value=None, action_confirm=None):
        self.name = name
        self.text = text
        self.type = type
        self.value = value
        self.action_confirm = action_confirm if isinstance(action_confirm, (ActionConfirm, type(None)))\
            else ActionConfirm(action_confirm)

    def confirm(self, text, title=None, ok_text=None, dismiss_text=None):
        self.action_confirm = ActionConfirm(text, title, ok_text, dismiss_text)
        return self

    def render(self):
        result = {}
        for key in ('name', 'text', 'type', 'value'):
            value = getattr(self, key)
            if value is not None:
                result[key] = value
        if self.action_confirm:
            result['confirm'] = self.action_confirm.render()
        return {k: v for k, v in result.items() if v is not None}

    @classmethod
    def load(cls, data):
        params = {}
        for key in ('name', 'text', 'type', 'value'):
            value = data.get(key)
            if value is not None:
                params[key] = value
        if data.get('confirm'):
            params['action_confirm'] = ActionConfirm(**data['confirm'])
        return cls(**params)


class MessageButton(MessageAction):

    def __init__(self, name, text, value=None, action_confirm=None, style=None):
        """ Has "style" attribute """
        super(MessageButton, self).__init__(name, text, 'button', value, action_confirm)
        self.style = style

    def render(self):
        result = super(MessageButton, self).render()
        if self.style:
            result['style'] = self.style
        return result

    @classmethod
    def load(cls, data):
        print(data)
        obj = super(MessageButton, cls).load(data)
        obj.style = data.get('style')
        return obj


class MenuOption(object):
    def __init__(self, text, value, description=None):
        self.text = text
        self.value = value
        self.description = description

    def render(self):
        result = {
            'text': self.text,
            'value': self.value
        }
        if self.description:
            result['description'] = self.description
        return result

    @classmethod
    def load(cls, data):
        return cls(**data)


class MenuOptionGroup(object):
    def __init__(self, text, options):
        self.text = text
        self.options = options

    def add_option(self, text, value, description=None):
        self.options.append(MenuOption(text, value, description))

    def render(self):
        return {
            'text': self.text,
            'options': [option.render() for option in self.options]
        }

    @classmethod
    def load(cls, data):
        return cls(data['text'], [MenuOption.load(option) for option in data['options']])


class MessageMenu(MessageAction):

    def __init__(self, name, text, value=None, action_confirm=None, data_source='default'):
        super(MessageMenu, self).__init__(name, text, 'select', value, action_confirm)
        self.data_source = data_source

    def render(self):
        result = super(MessageMenu, self).render()
        for key in ('data_source',):
            value = getattr(self, key)
            if value is not None:
                result[key] = value
        return result

    @classmethod
    def load(cls, data):
        obj = super(MessageMenu, cls).load(data)
        obj.data_source = data['data_source']
        return obj


class MessageStaticMenu(MessageMenu):
    def __init__(self, name, text, value=None, action_confirm=None, options=None, option_groups=None,
                 selected_option=None):
        super(MessageStaticMenu, self).__init__(name, text, value, action_confirm, 'static')
        self.options = options
        self.option_groups = option_groups
        self.selected_option = selected_option

    def add_option(self, text, value, description=None):
        if self.options is None:
            self.options = []
        self.options.append(MenuOption(text, value, description))
        return self

    def add_option_to_group(self, group_text, option_text, option_value, option_description=None):
        option = MenuOption(option_text, option_value, option_description)
        if self.option_groups is None:
            self.option_groups = []
        target_groups = filter(lambda g: g.text == group_text, self.option_groups)
        if target_groups:
            target_group = target_groups[0]
            target_group.add_option(option_text, option_value, option_description)
        else:
            self.option_groups.append(MenuOptionGroup(group_text, [option]))
        return self

    def render(self):
        result = super(MessageStaticMenu, self).render()
        for key in ('options', 'option_groups'):
            value = getattr(self, key)
            if value is not None:
                result[key] = [item.render() for item in value]
        if self.selected_option is not None:
            result['selected_options'] = [self.selected_option.render()]
        return result

    @classmethod
    def load(cls, data):
        obj = super(MessageStaticMenu, cls).load(data)
        options = data.get('options')
        if options:
            obj.options = [MenuOption.load(option) for option in options]
        option_groups = data.get('option_groups')
        if option_groups:
            obj.option_groups = [MenuOptionGroup.load(group) for group in option_groups]
        obj.selected_option = data.get('selected_options')
        return obj


class MessageUserMenu(MessageMenu):

    def __init__(self, name, text, value=None, action_confirm=None, selected_user=None):
        super(MessageUserMenu, self).__init__(name, text, value, action_confirm, 'users')
        self.selected_user = selected_user

    def render(self):
        result = super(MessageUserMenu, self).render()
        if self.selected_user is not None:
            result['selected_options'] = [{'value': self.selected_user.id}]
        return result

    @classmethod
    def load(cls, data):
        obj = super(MessageUserMenu, cls).load(data)
        selected_options = data.get('selected_options')
        if selected_options:
            obj.selected_user = SlackUser(selected_options[0]['value'])
        return obj


class MessageChannelMenu(MessageMenu):

    def __init__(self, name, text, value=None, action_confirm=None, selected_channel=None):
        super(MessageChannelMenu, self).__init__(name, text, value, action_confirm, 'channels')
        self.selected_channel = selected_channel

    def render(self):
        result = super(MessageChannelMenu, self).render()
        if self.selected_channel is not None:
            result['selected_options'] = [{'value': self.selected_channel.id}]
        return result

    @classmethod
    def load(cls, data):
        obj = super(MessageChannelMenu, cls).load(data)
        selected_options = data.get('selected_options')
        if selected_options:
            obj.selected_channel = SlackChannel(selected_options[0]['value'])
        return obj


class MessageConversationMenu(MessageMenu):

    def __init__(self, name, text, value=None, action_confirm=None, selected_conversation=None):
        super(MessageConversationMenu, self).__init__(name, text, value, action_confirm, 'conversations')
        self.selected_conversation = selected_conversation

    def render(self):
        result = super(MessageConversationMenu, self).render()
        if self.selected_conversation is not None:
            result['selected_options'] = [{'value': self.selected_conversation.id}]
        return result

    @classmethod
    def load(cls, data):
        obj = super(MessageConversationMenu, cls).load(data)
        selected_options = data.get('selected_options')
        if selected_options:
            obj.selected_channel = SlackConversation(selected_options[0]['value'])
        return obj


class MessageExternalMenu(MessageMenu):
    """ Not Implemented """

    def __init__(self, name, text, value=None, action_confirm=None, min_query_length=1):
        super(MessageExternalMenu, self).__init__(name, text, value, action_confirm, 'external')
        self.min_query_length = min_query_length
        raise NotImplementedError('This class is not implemented yet')


def parse_action(data):
    action_type = data.pop('type')
    if action_type is 'button':
        return MessageButton.load(data)
    elif action_type is 'select':
        return MessageMenu.load(data)
    else:
        raise TypeError('Unknown action type: "{}"'.format(action_type))
