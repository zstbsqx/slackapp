

from flask import Flask

app = Flask(__name__)

app.route('/slackapp/hello')
def hello():
    pass

if __name__ == '__main__':
    pass