# -*- encoding: utf-8 -*-


class Context(object):
    def __init__(self, team_id, token, timestamp):
        self.team_id = team_id
        self.token = token
        self.timestamp = timestamp


class ActionContext(Context):
    def __init__(self, action_type, team_id, channel, user, action_ts, message_ts, attachment_id, token, response_url):
        super(ActionContext, self).__init__(team_id, token, action_ts)


class EventContext(Context):
    def __init__(self, token, team_id, api_app_id, event_id, event_time, authed_users, **event_specified):
        super(EventContext, self).__init__(team_id, token, event_time)