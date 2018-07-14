
from slackapp.view import MessageView
from slackapp.message import MessageText

def test_text_1():
    t = MessageText()
    t.text('hello')
    r = t.render()
    assert r == 'hello'

def test_text_2():
    t = MessageText()
    t.text('hello&world')
    r = t.render()
    assert r == 'hello&amp;world'