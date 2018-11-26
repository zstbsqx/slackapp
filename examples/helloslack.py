import random

from flask import Flask

from slackapp.view import MessageView, on_action
from slackapp.component.message import Message
from slackapp.app import SlackApp


app = Flask(__name__)


class ButtonView(MessageView):

    @property
    def init_msg(self):
        msg = Message('what is it button view')
        a = msg.attachment()
        a.callback_id = 'foo'
        a.title('What is it')
        a.button('book', 'It is a book')
        a.button('pencil', 'It is a pencil')
        return msg

    @on_action('foo', 'book')
    def on_book_clicked(self, value):
        self.msg = Message('Yes, it is a book.')

    @on_action('foo', 'pencil')
    def on_pencil_clicked(self, value):
        self.msg = Message('Yes, it is a pencil.')


class MenuView(MessageView):

    @property
    def init_msg(self):
        msg = Message('how are you menu view')
        a = msg.attachment()
        a.callback_id = 'bar'
        a.title('How are you')
        menu = a.static_menu('how_are_you', 'How are you?')
        menu.add_option('fine', 'fine')
        menu.add_option('bad', 'bad')
        return msg

    @on_action('bar', 'how_are_you')
    def on_how_are_you_select(self, value):
        print('hi {}'.format(value))
        if value == 'fine':
            self.msg = Message('Glad to hear about that')
        elif value == 'bad':
            self.msg = Message('What happened?')
            a = self.msg.attachment()
            a.callback_id = 'bar2'
            a.button('bla', 'Blabla')

    @on_action('bar2', 'bla')
    def on_how_are_you_reply(self, value):
        self.msg = Message('Sorry to hear that')


hello_app = SlackApp('hello')


@hello_app.on_event('app_mention')
def send_some_view(event_data, ctx):
    channel_id = event_data['channel']
    view_cls = random.choice([ButtonView, MenuView])
    hello_app.send_view(view_cls, channel_id)


if __name__ == '__main__':
    import configparser
    config = configparser.ConfigParser()
    config.read('config.ini')
    conf = dict(config.items('hello'))
    hello_app.setup_config(**conf)
    hello_app.register_view(ButtonView)
    hello_app.register_view(MenuView)
    hello_app.mount_flask(app)
    app.run()

    print(ButtonView.action_handlers)
    print('------------')
    v = ButtonView()
    print(v.action_handlers)
