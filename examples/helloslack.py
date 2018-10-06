

from flask import Flask
from flask import request
from flask import jsonify
import json

app = Flask(__name__)


from slackapp.view import MessageView
from slackapp import SlackApp

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
    
    def on_bad_clicked(self):
        self.reset()
        self.text("Oh, I'm sorry to hear that")


class HelloApp(SlackApp):
    def on_slack_app_mention(self):
        return ''
    
    def on_slack_message(self):
        return ''

hello_app = HelloApp('hello')
HelloView.register(hello_app)

@app.route('/slackapp/hello', methods=['GET', 'POST'])
def hello():
    data = json.loads(request.values.get('payload'))
    ret = hello_app.handle_request(data)
    return jsonify(**ret)

@app.route('/slackapp/hello/event', methods=['GET', 'POST'])
def hello_event():
    data = request.get_json(force=True)
    ret = hello_app.handle_slack_event(data)
    return jsonify(**ret)

if __name__ == '__main__':
    import configparser
    config = configparser.ConfigParser()
    config.read('config.ini')
    conf = dict(config.items('hello'))
    hello_app.setup_config(**conf)
    hello_app.send_view(HelloView, conf.get('user_id', ''))
    app.run()
    