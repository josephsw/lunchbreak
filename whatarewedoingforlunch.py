import cgi
import webapp2
import jinja2
import os
jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

from google.appengine.api import users


class User(db.Model):
  email = db.StringProperty()
  phonenumber = db.StringProperty()
  displayname = db.StringProperty()
  events = db.ListProperty(db.Key)
  attending = db.ListProperty(db.Key)
  
def user_key(email):
  return db.Key.from_path('Users', email)
  
  
class MainPage(webapp2.RequestHandler):
    def get(self):
        if users.get_current_user():
            current_user = users.get_current_user()
            user_query = User.all().ancestor(
                        user_key(current_user.email()))
            query_result = user_query.fetch(1)
            
            if not query_result:
              #need to add user to the database
              user = User(parent=user_key(current_user.email()))
              user.email = current_user.email()
              user.displayname = current_user.nickname()
              user.put()
              
            url = users.create_logout_url(self.request.uri)  
            url_linktext = 'Logout'
        else:
            url = users.create_login_url(self.request.uri)
            url_linktext = 'Login'

        template_values = {
            'url_linktext': url_linktext,
            'url': url,
            'users': users,
            'createEvent': '/create',
        }
        #'events': events,
        template = jinja_environment.get_template('index.html')
        self.response.out.write(template.render(template_values))

class CreateEvent(webapp2.RequestHandler):
    def get(self):
        #create an event!
        template_values2 = {
            'eventName': 'Where are we going for lunch',
            'time': '11:00AM',
            'lockdownTime':'10:30AM',
            #'inviteList': inviteList,
        }
        template2 = jinja_environment.get_template('createEvent.html')
        self.response.out.write(template2.render(template_values2))

class EventPage(webapp2.RequestHandler):
    def get(self):
        #create an event!
        attending = ['Elynn', 'Alex', 'Ian', 'Joseph', 'Aaron']
        template_values3 = {
            'eventName': "CoCo's Cafe",
            'eventDate': '10/21/2012',
            'time': '11:00AM',
            'lockdownTime':'10:30AM',
            'attending': attending,
        }
        template3 = jinja_environment.get_template('eventPage.html')
        self.response.out.write(template3.render(template_values3))

        
app = webapp2.WSGIApplication([('/', MainPage),
                              ('/create', CreateEvent),
                              ('/viewevent', EventPage)],
                              debug=True)
