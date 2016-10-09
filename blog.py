import os
import jinja2
import webapp2
import re
import hashlib
import hmac
import random
from string import letters
from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape = True)

SECRET = '0Ix.cF#2h1S?C*fQ6'

def make_salt():
	return ''.join(random.choice(string.letters) for x in xrange(5))

def make_pw_hash(name, pw, salt = None):
	if not salt:
		salt = make_salt()
	h = hashlib.sha256(name + pw + salt).hexdigest()
	return '%s|%s' % (h, salt)

def validate_pw(name, pw, h):
	salt = h.split('|')[1]
	return h == make_pw_hash(name, pw, salt)

def hash_user(user):
	return hmac.new(SECRET, user).hexdigest()

def make_secure_val(user):
	return '%s|%s' % (user, hash_user(user))

def check_secure_val(h):
	val = h.split('|')[0]
	if h == make_secure_val(val):
		return val

class User(db.Model):
	username = db.StringProperty(required = True)
	password_hash = db.StringProperty(required = True)
	email = db.EmailProperty()

	@classmethod
	def by_id(cls, uid):
		return User.get_by_id(uid)

	@classmethod
	def by_username(cls, username):
		return User.all().filter('username =', username).get()

	@classmethod
	def login_user(cls, username, password):
		user = cls.by_username(username)
		valid_password = validate_pw(username, password, user.password_hash)
		if user and valid_password:
			return user

	@classmethod
	def register_user(cls, username, password, email = None):
		pass_hash = make_pw_hash(username, password)
		return User(username = username,
					password_hash = pass_hash,
					email = email)

class Post(db.Model):
	author = db.StringProperty(required = True)
	subject = db.StringProperty(required = True)
	content = db.TextProperty(required = True)
	created = db.DateTimeProperty(auto_now_add = True)
	modified = db.DateTimeProperty(auto_now = True)
	likes = db.IntegerProperty(required = True)

	def render(self):
		self.render_text = self.content.replace('\n', '<br>')
		return render_str('post.html', post = self)

class Comment(db.Model):
	author = db.StringProperty(required = True)
	content = db.StringProperty(required = True)
	created = db.DateTimeProperty(auto_now_add = True)
	modified = db.DateTimeProperty(auto_now = True)

	def render(self):
		return render_str('comment.html', comment = self)

class Like(db.Model):
	uid = db.StringProperty(required = True)
	value = db.IntegerProperty(required = True)

class Handler(webapp2.RequestHandler):
	def write(self, *a, **kw):
		self.response.out.write(*a, **kw)

	def render_str(self, template, **params):
		t = jinja_env.get_template(template)
		return t.render(params)

	def render(self, template, **kw):
		self.write(self.render_str(template, **kw))

	def set_secure_cookie(self, name, val):
		cookie_val = make_secure_val(val)
		self.response.headers.add_header(
			'Set-Cookie',
			'%s=%s; Path=/' % (name, cookie_val))

	def read_secure_cookie(self, name):
		cookie_val = self.request.cookies.get(name)
		return cookie_val and check_secure_val(cookie_val)

	def login_cookie(self, user):
		self.set_secure_cookie('user_id', str(user.key().id()))

	def logout_cookie(self):
		self.response.headers.add_header('Set-Cookie', 'user_id=; Path=/')

	def initialize(self, *a, **kw):
		webapp2.RequestHandler.initialize(self, *a, **kw)
		uid = self.read_secure_cookie('user_id')
		self.user = uid and User.by_id(int(uid))

class MainPage(Handler):
	def get(self):
		all_posts = Post.all().order('-created')
		posts = all_posts.fetch(limit=10)
		self.render('signinstatus.html', user = self.user)
		self.render('mainpage.html', posts = posts)

	def post(self):
		username = self.request.get('username')
		password = self.request.get('password')

		username_error = ''
		password_error = ''

		if not username:
			username_error = 'Please enter username.'

		if not password:
			password_error = 'Please enter password.'

		if username_error or password_error:
			self.render('signinstatus.html', username = username,
				username_error = username_error,
				password_error = password_error)
		else:
			user = User.login_user(username, password)

			if user:
				self.render('signinstatus.html', user = user)
				self.login_cookie(user)
			else:
				self.render('signinstatus.html', signin_error = True)

class RegistrationPage(Handler):
	def get(self):
		if user:
			self.redirect('/')
		else:
			self.render('loginform.html')

	def post(self):
		username = self.request.get('username')
		password = self.request.get('password')
		verify = self.request.get('verify')
		email = self.request.get('email')
		error_check = False

		params = dict(username = username, email = email)

		USER_RE = re.compile(r'^[a-zA-Z0-9_-]{3,20}$')
		def valid_username(username):
			return USER_RE.match(username)

		PASSWORD_RE = re.compile(r'^.{3,20}$')
		def valid_password(password):
			return PASSWORD_RE.match(password)

		EMAIL_RE = re.compile(r'^[\S]+@[\S]+.[\S]+$')
		def valid_email(email):
			return EMAIL_RE.match(email)

		def verify_password(password, verify):
			return password == verify

		if not valid_username(username):
			params['username_error'] = "That's not a valid username."
			error_check = True

		if not valid_password(password):
			params['password_error'] = "That's not a valid password."
			error_check = True
		elif not verify_password(password, verify):
			params['verify_error'] = "Your passwords didn't match."
			error_check = True

		if email and not valid_email(email):
			params['email_error'] = "That's not a valid email."
			error_check = True

		if error_check:
			self.render('loginform.html', **params)

		# if username_cookie_str:
		# 	current_user = username_cookie_str.split('|')[0]
		# 	if current_user == username:
		# 		username_error = "That user already exists."

		# if not username_error:
		# 	new_username_cookie = str(make_secure_val(username))
		# 	self.response.headers.add_header('Set-Cookie', 'username=%s;Path=/' % new_username_cookie)

		# if verify and verify_check:
		# 	new_password_cookie = make_pw_hash(username, password)
		# 	self.response.headers.add_header('Set-Cookie', 'password=%s;Path=/' % new_password_cookie)
		# else:
		# 	verify_error = "Your passwords didn't match."


		# if username_error or password_error or email_error or verify_error:
		# 	self.render('loginform.html', username = username, email = email,
		# 		username_error = username_error, password_error = password_error,
		# 		email_error = email_error, verify_error = verify_error)
		# else:
		# 	self.redirect('/welcome')

app = webapp2.WSGIApplication([('/', MainPage),
								('/register', RegistrationPage),
								],
								debug = True)