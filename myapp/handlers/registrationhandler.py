import re
from . import Handler
from myapp.models.models import User

class RegistrationPage(Handler):
	def get(self):
		if self.user:
			self.redirect('/')
		else:
			self.render('registration.html')

	def post(self):
		if self.login_check():
			self.login_handler('registration.html')
		elif self.request.get('registration-form'):
			username = self.request.get('username')
			password = self.request.get('password')
			verify = self.request.get('verify')
			email = self.request.get('email')
			error_check = False

			params = dict(reg_username = username, email = email)

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
				params['reg_username_error'] = "That's not a valid username."
				error_check = True

			if not valid_password(password):
				params['reg_password_error'] = "That's not a valid password."
				error_check = True
			elif not verify_password(password, verify):
				params['verify_error'] = "Your passwords didn't match."
				error_check = True

			if email and not valid_email(email):
				params['email_error'] = "That's not a valid email."
				error_check = True

			if error_check:
				self.render('registration.html', **params)
			else:
				# Check to see if user already exists.
				# If not, register user.
				user = User.by_username(username)
				if user:
					existing_error = "That username already exists."
					self.render('registration.html', username = username,
						existing_error = existing_error)
				else:
					user = User.register_user(username, password, email)
					user.put()
					self.login_cookie(user)
					self.render('registration.html')
					self.redirect('/')