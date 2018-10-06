
from flask import request, jsonify
from functools import partial
import json

def handle_slackapp_request(slackapp, *args, **kwargs):
    data = json.loads(request.values.get('payload'))
    ret = slackapp.handle_request(data)
    return jsonify(**ret)

def handle_slackapp_event(slackapp, *args, **kwargs):
    data = request.get_json(force=True)
    ret = slackapp.handle_slack_event(data)
    return jsonify(**ret)

def init_flaskapp(slackapp, flaskapp, url_prefix):
    flaskapp.add_url_rule(url_prefix, 'handle_{}_request'.format(slackapp.name), 
        view_func=partial(handle_slackapp_request, slackapp), methods=['GET', 'POST'])
    flaskapp.add_url_rule('{}/event'.format(url_prefix), 'handle_{}_event'.format(slackapp.name), 
        view_func=partial(handle_slackapp_event, slackapp), methods=['GET', 'POST'])