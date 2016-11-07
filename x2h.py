#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import logging
import sleekxmpp
import httplib
import urllib
from slackclient import SlackClient

from config import *

sys.setdefaultencoding('utf8')

slack_client = SlackClient(slack['token'])

class JabberBot(sleekxmpp.ClientXMPP):
    def __init__(self, jid, password, logfile=None):
        sleekxmpp.ClientXMPP.__init__(self, jid, password)
        self.add_event_handler('session_start', self.start)
        self.add_event_handler('message', self.message)
        self.log = self.setlogging(logfile)

    def start(self, event):
        self.send_presence()
        self.get_roster()

    def message(self, msg):
        if msg['type'] in ('chat', 'normal'):
            self.log.info('Message received.')
            self.log.info('Message from: %s' % msg['from'])
            self.log.info('Message text: %s' % msg['body'])
            # msg.reply("?").send()
            out_msg = 'Message from: %s\nMessage text: %s' % (msg['from'], msg['body'])
            self.pushover_send(out_msg)
            slack_client.api_call("chat.postMessage", channel='#general',
                                          text=out_msg, as_user=True)

    def pushover_send(self, msg):
        conn = httplib.HTTPSConnection('api.pushover.net:443')
        conn.request('POST', '/1/messages.json',
        urllib.urlencode({
            'token':   pushover['token'],
            'user':    pushover['user'],
            'message': msg,
        }), { 'Content-type': 'application/x-www-form-urlencoded' })
        conn.getresponse()
        self.log.info('Pushover message sent.')
    
    def setlogging(self, logfile=None):
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)
        formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        if logfile:
                filelevel = logging.INFO
                fh = logging.FileHandler(logfile)
                fh.setLevel(filelevel)
                fh.setFormatter(formatter)
                logger.addHandler(fh)
        return logger

if __name__ == '__main__':

    jab = JabberBot(jabber['id'], jabber['password'], 'x2h.log')
    jab.log.info('Jabber bot started')
    jab.register_plugin('xep_0030')  # Service Discovery
    jab.register_plugin('xep_0004')  # Data Forms
    jab.register_plugin('xep_0060')  # PubSub
    jab.register_plugin('xep_0199')  # XMPP Ping

    if jab.connect():
        jab.process(block=True)
        jab.log.info('Jabber process done.')
    else:
        jab.log.info('Unable to connect to Jabber.')
 
