import cgi
import webapp2
import jinja2
import os
import urllib
import datetime

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

from google.appengine.api import users
from google.appengine.ext import db
class User(db.Model):
  email = db.StringProperty()
  phonenumber = db.StringProperty()
  displayname = db.StringProperty()
  events = db.ListProperty(db.Key)
  attending = db.ListProperty(db.Key)
  textalerts = db.StringProperty()

def get_current_user_User():

  current_user = users.get_current_user()
  if  users.get_current_user():
    user_query = User.all().ancestor(
                user_key(current_user.email()))
    query_result = user_query.fetch(1)
    if not query_result:
      self.redirect("/")
    else:
      return query_result[0]
    
def user_key(email):
  return db.Key.from_path('Users', email)

class EditPreferences(webapp2.RequestHandler):
    def get(self):
        #edit preferences
        display_name = ''
        phone_number = ''
        text_alerts = ''
        current_user = users.get_current_user()
        if users.get_current_user():
            user_query = User.all().ancestor(user_key(current_user.email()))
            query_result = user_query.fetch(1)[0]
            if not query_result:
                self.redirect('/')
            else:
                display_name = query_result.displayname
                phone_number = query_result.phonenumber
                text_alerts = query_result.textalerts
        else:
          self.redirect('/')
          
        template_values = {
            'displayname': display_name,
            'phonenumber': phone_number,
            'textalerts': text_alerts,
            'editPreferences': '/preferences' 
        }
        template = jinja_environment.get_template('editPreferences.html')
        self.response.out.write(template.render(template_values))
        
    def post(self):
        current_user = users.get_current_user()
        user_query = User.all().ancestor(user_key(current_user.email()))
        query_result = user_query.fetch(1)[0]
        query_result.displayname = self.request.get('displayname')
        query_result.phonenumber = self.request.get('phonenumber')
        query_result.textalerts = self.request.get('textalerts')
        query_result.put()
        self.redirect('/')
      
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
            'editRatings': '/ratings',
            'editPreferences': '/preferences' 
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
            #'inviteList': inviteList,,
            'editPreferences': '/preferences' 
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
            'editPreferences': '/preferences' 
        }
        template3 = jinja_environment.get_template('eventPage.html')
        self.response.out.write(template3.render(template_values3))

class Restaurant(db.Model):
  name = db.StringProperty()
  location = db.StringProperty()
  rating = db.RatingProperty()

def restaurant_key():
  return db.Key.from_path('Restaurants', 'default_restaurants')

class Restaurants(webapp2.RequestHandler):
    def get(self):
        template3 = jinja_environment.get_template('addRestaurant.html')
        self.response.out.write(template3.render([]))
    def post(self):
        restaurant = Restaurant(parent=restaurant_key())
        restaurant.name = self.request.get('name')
        restaurant.location = self.request.get('location')
        restaurant.put()
        self.redirect('/restaurants')
        #self.redirect('/?' + urllib.urlencode({'name': restaurant.name}))

class Rating(db.Model):
  restaurantID = db.StringProperty()
  rating = db.RatingProperty()
  
def rating_key(user):
  return db.Key.from_path('User', user)
		
class Ratings(webapp2.RequestHandler):
  def get(self):
    current_user = get_current_user_User()
    rating_query = Rating.all().ancestor(rating_key(current_user.email))
    ratings = rating_query.fetch(30)
    restaurants = Restaurant.all().ancestor(restaurant_key()).fetch(40)
    res_rating = []
    for x in ratings:
      restaurant = filter(lambda res: res.name == x.restaurantID, restaurants)
      if len(restaurant) > 0:
        res_rating.append((restaurant[0], x))
        restaurants.remove(restaurant[0])
    for x in restaurants:
      res_rating.append((x,))
    
    template_values3 = {
      'restaurants': res_rating,
      'editPreferences': '/preferences' 
    }
    template3 = jinja_environment.get_template('ratings.html')
    self.response.out.write(template3.render(template_values3))

  def post(self):
    current_user = get_current_user_User()
    rating_query = Rating.all().ancestor(rating_key(current_user.email))
    ratings = rating_query.fetch(40)
    rating = Rating(rating_key(current_user.email))
    for x in ratings:
        val = filter(lambda rat: rat.restaurantID == self.request.get('restaurantID'), ratings)
        if len(val) == 0:
          rating = Rating(rating_key(current_user.email))
        else:
          rating = val[0]
    rating.restaurantID = self.request.get('restaurantID')
    rating.rating = int(self.request.get('rating'))
    rating.put()
    self.redirect('/ratings')


class Review(webapp2.RequestHandler):
  def get(self):
    current_user = get_current_user_User()
    res = self.request.get('restaurantID')
    rating_query = Rating.all().ancestor(rating_key(current_user.email))
    my_list = rating_query.fetch(40)
    rating = filter(lambda rat: rat.restaurantID == res, my_list)
    if len(rating) > 0:
      rating = Rating(rating_key(current_user.email))
      rating.rating = 0
    else:
      rating = rating[0]
    template_values3 = {
      'restaurantname': res,
      'rating': rating.rating,
      'editPreferences': '/preferences' 
    }
    template3 = jinja_environment.get_template('restaurant.html')
    self.response.out.write(template3.render(template_values3))
		
class Event (db.Model):
  name = db.StringProperty()
  eventdate = db.DateTimeProperty()
  eventtime = db.DateTimeProperty()
  location = db.StringProperty()
  lockdowntime = db.DateTimeProperty
  invited = db.StringListProperty()
  attending = db.StringListProperty()

def event_key():
  return db.Key.from_path('Events', 'default_event')  

class CreateEvent(webapp2.RequestHandler):
    def get(self):
        #create an event!
        template2 = jinja_environment.get_template('createEvent.html')
        self.response.out.write(template2.render())
    def post(self):
        event = Event(parent=event_key())
        event.name = self.request.get('name')
        rawdate = self.request.get('eventdate')
        rawtime = self.request.get('eventtime')
        d = rawdate.split('/')
        t = rawtime.split(':')
        event.eventtime = datetime.datetime(int(d[2]), int(d[0]), int(d[1]), int(t[0]), int(t[1]))
        event.location = ''
        event.lockdowntime = self.request.get('lockdowntime')
        invitees = self.request.get('invited')
        listOfPeople = invitees.split(',')
        invited2 = []
        for i in listOfPeople:
          i.strip()
          invited2.append(i)
        event.invited = invited2
        event.attending = [get_current_user_User().email,]
        event.put()
        self.redirect('/')
        #self.redirect('/?' + urllib.urlencode({'name': event.name}))

app = webapp2.WSGIApplication([('/', MainPage),
                              ('/create', CreateEvent),
                               ('/preferences', EditPreferences),
                              ('/viewevent', EventPage),
                               ('/restaurants',Restaurants),
                               ('/ratings', Ratings),
				('/review', Review)],
                              debug=True)
