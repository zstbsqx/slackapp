# -*- encoding: utf-8 -*-
from six.moves import builtins

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
        self.action_confirm = action_confirm if isinstance(action_confirm, (ActionConfirm, builtins.type(None)))\
            else ActionConfirm(action_confirm)

    def confirm(self, text, title=None, ok_text=None, dismiss_text=None):
        self.action_confirm = ActionConfirm(text, title, ok_text, dismiss_text)
        return self.action_confirm

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
        if data.pop('type') is not 'button':
            raise TypeError('Invalid action type')
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

    def __iter__(self):
        return iter(self.options)

    def render(self):
        return {
            'text': self.text,
            'options': [option.render() for option in self.options]
        }

    @classmethod
    def load(cls, data):
        return cls(data['text'], [MenuOption.load(option) for option in data['options']])


class MessageMenu(MessageAction):

    def __init__(self, name, text, value=None, action_confirm=None, data_source='default', selected_option=None):
        super(MessageMenu, self).__init__(name, text, 'select', value, action_confirm)
        self.data_source = data_source
        self.selected_option = selected_option

    def set_selected(self, value):
        self.selected_option = MenuOption(None, str(value))

    def render(self):
        result = super(MessageMenu, self).render()
        for key in ('data_source',):
            value = getattr(self, key)
            if value is not None:
                result[key] = value
        result['selected_options'] = [self.selected_option.render()]
        return result

    @classmethod
    def load(cls, data):
        if data.pop('type') is not 'select':
            raise TypeError('Invalid action type')
        obj = super(MessageMenu, cls).load(data)
        obj.data_source = data['data_source']
        return obj


class MessageStaticMenu(MessageMenu):
    def __init__(self, name, text, value=None, action_confirm=None, options=None, option_groups=None,
                 selected_option=None):
        super(MessageStaticMenu, self).__init__(name, text, value, action_confirm, 'static', selected_option)
        self.options = options
        self.option_groups = option_groups

    def set_selected(self, value):
        # find option by value
        if self.option_groups:
            for group in self.option_groups:
                for option in group:
                    if option.value == value:
                        self.selected_option = option
                        return
        elif self.options:
            for option in self.options:
                if option.value == value:
                    self.selected_option = option
                    return
        raise ValueError('Option with value "{}" not found'.format(value))

    def add_option(self, text, value, description=None):
        option = MenuOption(text, value, description)
        if self.options is None:
            self.options = []
        self.options.append(option)
        return option

    def add_option_to_group(self, group_text, option_text, option_value, option_description=None):
        if self.option_groups is None:
            self.option_groups = []
        target_groups = filter(lambda g: g.text == group_text, self.option_groups)
        if target_groups:
            target_group = target_groups[0]
            option = target_group.add_option(option_text, option_value, option_description)
        else:
            option = MenuOption(option_text, option_value, option_description)
            self.option_groups.append(MenuOptionGroup(group_text, [option]))
        return option

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
        if data['data_source'] not in ('default', 'static'):
            raise TypeError('Invalid data source')
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

    @property
    def selected_user(self):
        return SlackUser(self.selected_option['value']) if self.selected_option else None

    @selected_user.setter
    def selected_user(self, value):
        if value is not None:
            self.selected_option = MenuOption(None, value.id)

    @classmethod
    def load(cls, data):
        if data['data_source'] is not 'users':
            raise TypeError('Invalid data source')
        obj = super(MessageUserMenu, cls).load(data)
        selected_options = data.get('selected_options')
        if selected_options:
            obj.selected_user = SlackUser(selected_options[0]['value'])
        return obj


class MessageChannelMenu(MessageMenu):

    def __init__(self, name, text, value=None, action_confirm=None, selected_channel=None):
        super(MessageChannelMenu, self).__init__(name, text, value, action_confirm, 'channels')
        self.selected_channel = selected_channel

    @property
    def selected_channel(self):
        return SlackUser(self.selected_option['value']) if self.selected_option else None

    @selected_channel.setter
    def selected_channel(self, value):
        if value is not None:
            self.selected_option = MenuOption(None, value.id)

    @classmethod
    def load(cls, data):
        if data['data_source'] is not 'channels':
            raise TypeError('Invalid data source')
        obj = super(MessageChannelMenu, cls).load(data)
        selected_options = data.get('selected_options')
        if selected_options:
            obj.selected_channel = SlackChannel(selected_options[0]['value'])
        return obj


class MessageConversationMenu(MessageMenu):

    def __init__(self, name, text, value=None, action_confirm=None, selected_conversation=None):
        super(MessageConversationMenu, self).__init__(name, text, value, action_confirm, 'conversations')
        self.selected_conversation = selected_conversation

    @property
    def selected_conversation(self):
        return SlackUser(self.selected_option['value']) if self.selected_option else None

    @selected_conversation.setter
    def selected_conversation(self, value):
        if value is not None:
            self.selected_option = MenuOption(None, value.id)

    @classmethod
    def load(cls, data):
        if data['data_source'] is not 'conversations':
            raise TypeError('Invalid data source')
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
    action_type = data['type']
    if action_type is 'button':
        return MessageButton.load(data)
    elif action_type is 'select':
        data_source = data.get('data_source', 'default')
        source_menu_mapping = {
            'default': MessageStaticMenu,
            'static': MessageStaticMenu,
            'users': MessageUserMenu,
            'channels': MessageChannelMenu,
            'conversations': MessageConversationMenu,
            'external': MessageExternalMenu
        }
        if data_source not in source_menu_mapping:
            raise TypeError('Unknown data source')
        return source_menu_mapping[data_source].load(data)
    else:
        raise TypeError('Unknown action type: "{}"'.format(action_type))
