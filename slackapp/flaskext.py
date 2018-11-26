import json
from functools import partial

from flask import request, jsonify

from slackapp.logging import logger


def handle_action_request(slackapp):
    data = json.loads(request.values.get('payload'))
    ret = slackapp.handle_action_request(data)
    return jsonify(ret)


def handle_event_request(slackapp):
    data = request.get_json()
    ret = slackapp.handle_event_request(data)
    return jsonify(ret)


def mount_flask(slackapp, flaskapp, url_prefix):
    action_path = '{}/actions'.format(url_prefix)
    flaskapp.add_url_rule(action_path, 'handle_actions', view_func=partial(handle_action_request, slackapp),
                          methods=['GET', 'POST'])
    event_path = '{}/events'.format(url_prefix)
    flaskapp.add_url_rule(event_path, 'handle_events', view_func=partial(handle_event_request, slackapp),
                          methods=['GET', 'POST'])
    logger.info('Your action path: {}'.format(action_path))
    logger.info('Your event path: {}'.format(event_path))
