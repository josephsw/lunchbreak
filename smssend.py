import datetime
import os
import re
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app

from twilio.rest import TwilioRestClient


#should be user object
'''class Numbers(db.Model):
    number = db.StringProperty()
    name = db.StringProperty()
    created = db.DateTimeProperty(auto_now_add=True)
    count = db.IntegerProperty()'''

#when invited

#on confirmation

class SmsSend(webapp.RequestHandler):
    #upon event creation, send SMS to those that 

    def post(self):
        number = self.request.get('number').strip().replace(" ", "").replace("-","")
        message = self.request.get('message').strip()
        template_values = { 'return': False, 'number': number, 'message': message, 'error': False }
        if re.search(r'^\d+$',number) and len(number) == 10:
            self.sms_number(number, message)
        else:
            template_values['error'] = True
        path = os.path.join(os.path.dirname(__file__), 'index.html')
        self.response.out.write(template.render(path, template_values))


    #THE GOOD STUFF
    #make sure the twilio library (folder) is there
    #do the import above for twilio.rest
    #sms_number takes a 10-digit number as an arg1, and a message string as arg2
    # This function will send the number specified the given message.
    def sms_number(self, number, msg):
        account = "AC2bca3b527c9d4be4956b0cb8374f981a"
        token = "29ca474294d5555b1b3dc5ed046a40f8"
        SIZE = 155
        client = TwilioRestClient(account, token)
        num_messages = len(msg) / SIZE + 1
        number = number.strip().replace(" ", "").replace("-","")
        if len(number) == 10:
            if num_messages == 1:
                client.sms.messages.create(to="+1"+number, from_="+15123944123", body=msg)
            else:
                for i in xrange(num_messages):
                    client.sms.messages.create(to="+1"+number, from_="+15123944123",
                        body="%d/%d: %s" % ((i+1), num_messages, msg[i*155:((i+1)*155)] ))
    '''
    def sms_user(self, user, msg):
        SIZE = 155
        account = "AC2bca3b527c9d4be4956b0cb8374f981a"
        token = "29ca474294d5555b1b3dc5ed046a40f8"
        client = TwilioRestClient(account, token)
        num_messages = len(msg) / SIZE + 1
        if user.number != "":
            if num_messages == 1:
                client.sms.messages.create(to="+1"+user.number, from_="+15123944123", body=msg)
            else:
                for i in xrange(num_messages):
                    client.sms.messages.create(to="+1"+user.number, from_="+15123944123",
                        body="%d/%d: %s" % ((i+1), num_messages, msg[i*155:((i+1)*155)] ))
    '''

application = webapp.WSGIApplication([('/sms_confirm', MainPage)], debug=False)

def main():
    run_wsgi_app(application)

if __name__ == '__main__':
    main()