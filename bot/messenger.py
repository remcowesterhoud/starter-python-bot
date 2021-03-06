# -*- coding: utf-8 -*-

import logging
import random
import datetime
import urllib2
import simplejson
import os
import fileinput

logger = logging.getLogger(__name__)


class Messenger(object):
    def __init__(self, slack_clients):
        self.clients = slack_clients

    def send_message(self, channel_id, msg):
        # in the case of Group and Private channels, RTM channel payload is a complex dictionary
        if isinstance(channel_id, dict):
            channel_id = channel_id['id']
        logger.debug('Sending msg: %s to channel: %s' % (msg, channel_id))
        channel = self.clients.rtm.server.channels.find(channel_id)
        channel.send_message(msg)

    def write_help_message(self, channel_id):
        bot_uid = self.clients.bot_user_id()
        txt = '{}\n{}\n{}\n{}'.format(
            "I'm your friendly Slack bot written in Python.  I'll *_respond_* to the following commands:",
            "> `hi <@" + bot_uid + ">` - I'll respond with a randomized greeting mentioning your user. :wave:",
            "> `<@" + bot_uid + "> joke` - I'll tell you one of my finest jokes, with a typing pause for effect. :laughing:",
            "> `<@" + bot_uid + "> attachment` - I'll demo a post with an attachment using the Web API. :paperclip:")
        self.send_message(channel_id, txt)

    def write_greeting(self, channel_id, user_id):
        greetings = ['Hola']
        txt = '{}, <@{}>!'.format(random.choice(greetings), user_id)
        self.send_message(channel_id, txt)

    def write_prompt(self, channel_id):
        bot_uid = self.clients.bot_user_id()
        txt = "I'm sorry, I didn't quite understand... Can I help you? (e.g. `<@" + bot_uid + "> help`)"
        self.send_message(channel_id, txt)

    def write_joke(self, channel_id):
        question = "Why did the python cross the road?"
        self.send_message(channel_id, question)
        self.clients.send_user_typing_pause(channel_id)
        answer = "To eat the chicken on the other side! :laughing:"
        self.send_message(channel_id, answer)

    def write_error(self, channel_id, err_msg):
        txt = ":face_with_head_bandage: my maker didn't handle this error very well:\n>```{}```".format(err_msg)
        self.send_message(channel_id, txt)

    def demo_attachment(self, channel_id):
        txt = "Beep Beep Boop is a ridiculously simple hosting platform for your Slackbots."
        attachment = {
            "pretext": "We bring bots to life. :sunglasses: :thumbsup:",
            "title": "Host, deploy and share your bot in seconds.",
            "title_link": "https://beepboophq.com/",
            "text": txt,
            "fallback": txt,
            "image_url": "https://storage.googleapis.com/beepboophq/_assets/bot-1.22f6fb.png",
            "color": "#7CD197",
        }
        self.clients.web.chat.post_message(channel_id, txt, attachments=[attachment], as_user='true')

    def time_foosball(self, channel_id, user_id):
        time = datetime.datetime.now()
        # Increase time by 2 hours to fix timezone differences
        time = time.replace(hour=time.hour + 2)
        txt = "I forgot my watch so I don't know the time. You decide yourself if it's time to play."
        if time.hour <= 11:
            txt = "Keep working you lazy twat. It's not even close to foosball time!"
            self.add_warning(channel_id, user_id)
        elif time.hour < 12:
            if time.minutes <= 30:
                txt = "Shouldn't you be worried about the daily stand-up first?"
            else:
                txt = "Already done with the stand-up huh? Sure, have a little game of foosball."
        elif time.hour >= 12 and time.hour < 13:
            txt = "Prime time! What're you waiting for? IT'S FOOSBALL TIME!"
        elif time.hour >= 13 and time.hour <= 14:
            txt = "You've missed your chance. Keep working!"
        elif time.hour < 15:
            txt = "Almooooooooost."
        else:
            txt = "Nearing the end of the day. A little game won't hurt anyone."
        self.send_message(channel_id, txt)

    def current_time(self, channel_id):
        time = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S')
        self.send_message(channel_id, time)

    def traffic_info(self, channel_id, user_id):
        if 'U2NQHH8TG' in user_id:
            orig_coord = "52.040381,5.535294"
            dest_coord = "52.057345,4.328507"
            url = "http://maps.googleapis.com/maps/api/distancematrix/json?origins={0}&destinations={1}&mode=driving&language=en-EN&sensor=false".format(str(orig_coord),str(dest_coord))
            result = simplejson.load(urllib2.urlopen(url))
            driving_time = result['rows'][0]['elements'][0]['duration']['text']
            self.send_message(channel_id, "If you leave now you should be home in approximately {}".format(driving_time))
        elif 'U2NQF7L4Q' in user_id:
            self.send_message(channel_id, "I can't be arsed to sign up for the NS API. Sorry :( (also they use XML...)")
        else:
            self.send_message(channel_id,
                              "I'm sorry <@{}>, I don't have any traffic information for you :(".format(user_id))

    def get_uid(self, channel_id, user_id):
        self.send_message(channel_id, "Your user id is: {}".format(user_id))

    def add_warning(self, channel_id, user_id):
        path = os.path.join(os.getcwd(), 'warnings.txt')
        for line in fileinput.input(path, inplace=True):
            if user_id in line:
                user, warnings = line.split(":")
                line.replace(warnings, str(int(warnings) + 1))
                break
        else:
            with open(path, "a") as myfile:
                myfile.write(user_id + ":1")
        fileinput.close()
        self.send_message(channel_id, "<@{}>, you have been warned!".format(user_id))

    def get_warnings(self, channel_id, user_id):
        path = os.path.join(os.getcwd(), 'warnings.txt')
        for line in fileinput.input(path, inplace=True):
            if user_id in line:
                user, warnings = line.split(":")
                self.send_message(channel_id, "<@{}>, you have {} warnings.".format(user_id, warnings))
                break
        else:
            self.send_message(channel_id, "Great job <@{}>! You don't have any warnings!".format(user_id))
        fileinput.close()

