
from slackapp.view import MessageView

class HelloView(MessageView):
    __callback_prefix__ = 'hello'
    def init(self):
        self.text('hello view')
        a = self.attachement('foo')
        a.title('how are you?')
        a.button('fine', 'fine, thanks')
        a.button('bad', 'not good')



def test_view_1():
    h = HelloView()
    h.init()
    r = h.render()
    assert r['text'] == 'hello view'
    assert len(r['attachments']) == 1
    a1 = r['attachments'][0]
    assert a1['callback_id'] == 'hello____foo'