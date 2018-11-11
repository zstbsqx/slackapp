# -*- encoding: utf-8 -*-
import json
import unittest

from slackapp.component.message import Message
from slackapp.component.attachment import MessageAttachment
from slackapp.component.action import MessageButton, MessageUserMenu, MessageChannelMenu, MessageStaticMenu, MenuOption
from slackapp.component.field import MessageField


class TestComplexMessage(unittest.TestCase):

    def test1(self):
        msg = Message('test', thread_ts=1234, response_type='ephemeral')

        att1 = msg.attachment()
        att1.text = 'hello'
        att1.field('field', 'nothing_here', True)
        att1.title('Fastgear', 'https://fastgear.ihandysoft.com/')
        att1.footer('slack', 'http://www.slack.com/favicon.ico')
        att1.author('Ji', 'https://github.com/zstbsqx/slackapp', 'https://avatars1.githubusercontent.com/u/4946367?s=32&v=4')

        att2 = msg.attachment()
        att2.callback_id = 'test_actions'
        att2.button('ok', 'ok')
        att2.button('cancel', 'cancel', action_confirm='Are your sure?', style='danger')
        att2.user_menu('user', 'user')
        att2.channel_menu('channel', 'channel')
        att2.static_menu('static', 'static', options=[MenuOption('a', 'a'), MenuOption('b', 'b', 'wow')])

        render_result = msg.render()
        json_result = json.dumps(render_result)
        # print(json_result)
        loaded_msg = Message.load(render_result)
        # print(json.dumps(loaded_msg.render()))
        self.assertEqual(loaded_msg.text, 'test')
        self.assertEqual(loaded_msg.thread_ts, 1234)
        self.assertEqual(loaded_msg.response_type, 'ephemeral')
        loaded_att1 = loaded_msg.attachments[0]
        self.assertEqual(loaded_att1.text, 'hello')
        self.assertEqual(loaded_att1.fields[0].title, 'field')
        self.assertEqual(loaded_att1.fields[0].value, 'nothing_here')
        self.assertEqual(loaded_att1.fields[0].short, True)
        self.assertEqual(loaded_att1.msg_title.title, 'Fastgear')
        self.assertEqual(loaded_att1.msg_title.title_link, 'https://fastgear.ihandysoft.com/')
        self.assertEqual(loaded_att1.msg_footer.footer, 'slack')
        self.assertEqual(loaded_att1.msg_footer.footer_icon, 'http://www.slack.com/favicon.ico')
        self.assertEqual(loaded_att1.msg_author.author_name, 'Ji')
        self.assertEqual(loaded_att1.msg_author.author_link, 'https://github.com/zstbsqx/slackapp')
        self.assertEqual(loaded_att1.msg_author.author_icon, 'https://avatars1.githubusercontent.com/u/4946367?s=32&v=4')
        loaded_att2 = loaded_msg.attachments[1]
        ok_button = loaded_att2.actions[0]
        self.assertIsInstance(ok_button, MessageButton)
        self.assertEqual(ok_button.name, 'ok')
        self.assertEqual(ok_button.text, 'ok')
        cancel_button = loaded_att2.actions[1]
        self.assertIsInstance(cancel_button, MessageButton)
        self.assertEqual(cancel_button.name, 'cancel')
        self.assertEqual(cancel_button.text, 'cancel')
        self.assertEqual(cancel_button.action_confirm.text, 'Are your sure?')
        self.assertEqual(cancel_button.style, 'danger')
        user_menu = loaded_att2.actions[2]
        self.assertIsInstance(user_menu, MessageUserMenu)
        self.assertEqual(user_menu.name, 'user')
        self.assertEqual(user_menu.text, 'user')
        channel_menu = loaded_att2.actions[3]
        self.assertIsInstance(channel_menu, MessageChannelMenu)
        self.assertEqual(channel_menu.name, 'channel')
        self.assertEqual(channel_menu.text, 'channel')
        static_menu = loaded_att2.actions[4]
        self.assertIsInstance(static_menu, MessageStaticMenu)
        self.assertEqual(static_menu.name, 'static')
        self.assertEqual(static_menu.text, 'static')
        self.assertEqual(static_menu.options[0].text, 'a')
        self.assertEqual(static_menu.options[0].value, 'a')
        self.assertEqual(static_menu.options[1].text, 'b')
        self.assertEqual(static_menu.options[1].value, 'b')
        self.assertEqual(static_menu.options[1].description, 'wow')


