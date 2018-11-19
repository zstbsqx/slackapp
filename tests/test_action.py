# -*- encoding: utf-8 -*-
import unittest
from slackapp.component.action import MessageStaticMenu, MenuOption, MenuOptionGroup, MessageUserMenu


class TestMessageAction(unittest.TestCase):

    def test_set_selected(self):
        # test normal menu
        user_menu = MessageUserMenu('u', 'U')
        self.assertIsNone(user_menu.selected_option)
        user_menu.set_selected('U12345')
        self.assertIsNone(user_menu.selected_option.text)
        self.assertEqual(user_menu.selected_option.value, 'U12345')
        # test static menu
        #   test menu with options
        static_menu = MessageStaticMenu('s', 'S', options=[MenuOption('A', 'a'), MenuOption('B', 'b')])
        self.assertIsNone(static_menu.selected_option)
        static_menu.set_selected('a')
        self.assertEqual(static_menu.selected_option.text, 'A')
        self.assertEqual(static_menu.selected_option.value, 'a')
        static_menu.set_selected('b')
        self.assertEqual(static_menu.selected_option.text, 'B')
        self.assertEqual(static_menu.selected_option.value, 'b')
        with self.assertRaises(ValueError):
            static_menu.set_selected('c')
        #   test menu with option groups
        static_menu = MessageStaticMenu('s', 'S', option_groups=[
            MenuOptionGroup('G1', [MenuOption('A1', 'a1'), MenuOption('B1', 'b1')]),
            MenuOptionGroup('G2', [MenuOption('A2', 'a2'), MenuOption('B2', 'b2')])
        ])
        self.assertIsNone(static_menu.selected_option)
        static_menu.set_selected('a1')
        self.assertEqual(static_menu.selected_option.text, 'A1')
        self.assertEqual(static_menu.selected_option.value, 'a1')
        static_menu.set_selected('b2')
        self.assertEqual(static_menu.selected_option.text, 'B2')
        self.assertEqual(static_menu.selected_option.value, 'b2')
        with self.assertRaises(ValueError):
            static_menu.set_selected('c')