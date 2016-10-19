import webapp2
from myapp.functions.functions import *
from myapp.models.models import User

class Handler(webapp2.RequestHandler):
	def initialize(self, *a, **kw):
		webapp2.RequestHandler.initialize(self, *a, **kw)
		uid = self.read_secure_cookie('user_id')
		self.user = uid and User.by_id(int(uid))

	def write(self, *a, **kw):
		self.response.out.write(*a, **kw)

	def render_str(self, template, **params):
		params['user'] = self.user
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

	def login_check(self):
		if self.request.get('login-form'):
			return True

	def login_handler(self, template, **params):
		username = self.request.get('username')
		password = self.request.get('password')
		path = self.request.path
		has_error = False

		new_params = dict(params)

		if not username:
			new_params['username_error'] = 'Please enter username.'
			has_error = True

		if not password:
			new_params['password_error'] = 'Please enter password.'
			new_params['username'] = username
			has_error = True

		if has_error:
			self.render(template, **new_params)
		else:
			user = User.login_user(username, password)
			if user:
				self.login_cookie(user)
				self.redirect(path, params)
			else:
				new_params['signin_error'] = True
				self.render(template, **new_params)