# -*- coding: utf-8 -*-
# -*- encoding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu
#
# Based on https://weechat.org/scripts/source/mqtt_notify.py.html/
# but doesn't use the paho client because I had strange connection-problems even on localhost.
# 
# So I use mosquitto_pub instead, which works great and is fast enough for my usecase.

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)
try:
    import weechat
    import_ok = True
except ImportError:
    weechat.prnt('', 'mqtt_notify: this script must be run under WeeChat.')
    weechat.prnt('', 'Get WeeChat now at: http://www.weechat.org/')
    import_ok = False

try:
    import subprocess
    import json
    import pipes
    import shlex
except ImportError as message:
    weechat.prnt('', 'mqtt_notify: missing package(s): %s' % (message))
    import_ok = False
import sys


SCRIPT_MAINTAINER = 'aligator <aligator@suncraft-server.de>'

SCRIPT_NAME = 'mqtt_pub'
SCRIPT_AUTHOR = 'aligator <aligator@suncraft-server.de>'
SCRIPT_VERSION = '0.1'
SCRIPT_LICENSE = 'MIT'
SCRIPT_DESC = 'Sends notifications using MQTT'

DEFAULT_OPTIONS = {
    'mqtt_host': 'localhost',
    'mqtt_port': '1883',
    'mqtt_keepalive': '60',
    'mqtt_user': '',
    'mqtt_password': '',
    'mqtt_channel': 'weechat',
    'mqtt_client_name': 'weechat_mqtt_notify',
    'mqtt_message_data': '',  # string passed in the data field of the callback
    'mqtt_private_data': 'private',
}

def weechat_on_msg_cb(*a):
    keys = ['data', 'buffer', 'timestamp', 'tags', 'displayed', 'highlight',
                'sender', 'message']
    msg = dict(zip(keys, a))

    msg['buffer_long'] = weechat.buffer_get_string(msg['buffer'], 'name')
    msg['buffer_full'] = weechat.buffer_get_string(msg['buffer'], 'full_name')
    msg['buffer'] = weechat.buffer_get_string(msg['buffer'], 'short_name')
    
    keys.append('buffer_long')
    keys.append('buffer_full')
    keys.append('buffer')
   
#    msg['message'] = 'ü' + msg['message'] 
    # escape " (with \\ so that it is compatible with js JSON.parse)
    # also escape \ with \\ if someone writes a \
    # uses u'...' because of unicode-compatibility
    for key in keys:
        if isinstance(msg[key], basestring): 
            msg[key] = msg[key].decode('iso-8859-1')
           # msg[key] = msg[key].encode('utf-8')
            msg[key] = msg[key].replace(u'\\', u'\\\\').replace(u'"', u'\\"')
            msg[key] = msg[key].encode('utf-8')

    
    # build cmd
    cmd = ' '.join([
        '/usr/bin/mosquitto_pub',
        '-k', weechat.config_get_plugin('mqtt_keepalive'),
        '-i', weechat.config_get_plugin('mqtt_client_name') + msg["buffer"],
        '-h ', weechat.config_get_plugin('mqtt_host'),
        '-t', weechat.config_get_plugin('mqtt_channel') + "/" + msg["buffer"].replace('#', ''),
        '-m', pipes.quote(json.dumps(msg)),
        '-u', weechat.config_get_plugin('mqtt_user'),
        '-P', weechat.config_get_plugin('mqtt_password')])
    
    # send cmd
    subprocess.call(shlex.split(cmd))

    return weechat.WEECHAT_RC_OK

if import_ok:

    weechat.register(SCRIPT_NAME, SCRIPT_AUTHOR, SCRIPT_VERSION,
                     SCRIPT_LICENSE, SCRIPT_DESC, '', '')

    for key, val in DEFAULT_OPTIONS.items():
        if not weechat.config_is_set_plugin(key):
            weechat.config_set_plugin(key, val)
    
    
    weechat.hook_print("", "notify_message", "", 1, "weechat_on_msg_cb",
                       weechat.config_get_plugin("mqtt_message_data"))
    weechat.hook_print("", "notify_private", "", 1, "weechat_on_msg_cb",
                       weechat.config_get_plugin("mqtt_private_data"))
