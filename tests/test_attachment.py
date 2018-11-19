# -*- encoding: utf-8 -*-
import unittest
from slackapp.component.attachment import SelectValueProxy, MessageAttachment
from slackapp.component.action import MenuOption


class TestMessageAttachment(unittest.TestCase):

    def test_select_value_proxy(self):
        att = MessageAttachment()
        user_menu = att.user_menu('u', 'U')
        static_menu = att.static_menu('s', 'S', options=[MenuOption('A', 'a'), MenuOption('B', 'b')])
        # test get
        self.assertIsNone(att.select_values['u'], None)
        self.assertIsNone(att.select_values['s'], None)
        with self.assertRaises(KeyError):
            att.select_values['btn']
        with self.assertRaises(KeyError):
            att.select_values['not_exist']
        # test set
        att.select_values['u'] = 'U12345'
        self.assertIsNone(user_menu.selected_option.text)
        self.assertEqual(user_menu.selected_option.value, 'U12345')
        self.assertEqual(att.select_values['u'], 'U12345')
        att.select_values['s'] = 'a'
        self.assertEqual(static_menu.selected_option.text, 'A')
        self.assertEqual(static_menu.selected_option.value, 'a')
        self.assertEqual(att.select_values['s'], 'a')
        with self.assertRaises(KeyError):
            att.select_values['btn'] = '4'
        with self.assertRaises(KeyError):
            att.select_values['not_exist'] = 'sth'
