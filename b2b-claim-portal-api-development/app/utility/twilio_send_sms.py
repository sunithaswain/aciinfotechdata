import os
import re
import traceback
from twilio.rest import Client


class SendSms(object):
    def __init__(self, config, msgbody, tophnumber):
        self.config = config
        self.msgbody = msgbody
        self.tophnumber = tophnumber
        self.fromphnumber = config.RESPONSE_PHONENUMBER
        self.TWILIO_SID = config.TWILIO_SID
        self.TWILIO_AUTH_TOKEN = config.TWILIO_AUTH_TOKEN

    def sendSMS(self):

        try:
            # Account Sid and Auth Token from twilio.com/console
            account_sid = self.TWILIO_SID
            auth_token = self.TWILIO_AUTH_TOKEN
            client = Client(account_sid, auth_token)

            # if no phone number
            if not self.tophnumber or self.tophnumber == '':
                return 'failed', 'Destination phone number not identified'

            tophnumber = re.sub('[^0-9]', '', self.tophnumber)[-10:]
            if len(tophnumber) != 10:
                return 'failed', 'Destination phone number is incorrect'
            tophnumber = '+1' + tophnumber

            message = client.messages.create(
                body=self.msgbody, from_=self.fromphnumber, to=tophnumber)
            # print(message.status)
            return 'success', message.sid
        except Exception as e:
            # traceback.print_exc()
            print(e)
            return 'failed', str(e)
