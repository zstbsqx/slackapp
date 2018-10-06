

from flask import Flask
import json

app = Flask(__name__)


from slackapp.view import MessageView
from slackapp import SlackApp
class WhatisthisView(MessageView):
    __callback_prefix__ = 'whatisit'
    def init(self):
        self.text('what is it view')
        a = self.attachement('foo')
        a.title('What is it?')
        a.button('book', 'it is a book.')
        a.button('pencil', 'it is a pencil.')
    
    def on_book_clicked(self):
        self.reset()
        self.text("Yes, it's a book")
    
    def on_pencil_clicked(self):
        self.reset()
        self.text("Yes, it's a pencil.")

class HelloView(MessageView):
    __callback_prefix__ = 'hello'
    def init(self):
        self.text('hello view')
        a = self.attachement('foo')
        a.title('how are you?')
        a.button('fine', 'fine, thanks')
        a.button('bad', 'not good')
    
    def on_fine_clicked(self):
        self.reset()
        self.text("I'm fine, too.")        
        w = WhatisthisView()
        w.init()
        return w
    
    def on_bad_clicked(self):
        self.reset()
        self.text("Oh, I'm sorry to hear that")


class HelloApp(SlackApp):
    def on_slack_app_mention(self):
        return ''
    
    def on_slack_message(self, message):
        user = message.get('user')
        if user:
            hello_app.send_view(HelloView, user)

hello_app = HelloApp('hello')
hello_app.register_view(WhatisthisView)
hello_app.register_view(HelloView)
hello_app.init_flaskapp(app, '/slackapp/hello')

if __name__ == '__main__':
    import configparser
    config = configparser.ConfigParser()
    config.read('config.ini')
    conf = dict(config.items('hello'))
    hello_app.setup_config(**conf)
    app.run()
    