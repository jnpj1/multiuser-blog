import os
import jinja2
import webapp2
import re
import hashlib
import hmac
import random
import datetime
import time
import json
from string import letters
from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape = True)

SECRET = '0Ix.cF#2h1S?C*fQ6'

def make_salt():
	return ''.join(random.choice(letters) for x in xrange(5))

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

def render_str(template, **params):
	t = jinja_env.get_template(template)
	return t.render(params)

class User(db.Model):
	username = db.StringProperty(required = True)
	password_hash = db.StringProperty(required = True)
	email = db.StringProperty()

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
	modified = db.DateTimeProperty(auto_now_add = True)
	comments = db.IntegerProperty(required = True)
	likes = db.IntegerProperty(required = True)

	@classmethod
	def by_id(cls, post_id):
		return Post.get_by_id(int(post_id))

	@classmethod
	def most_recent(cls):
		recent_posts = Post.all().order('-created')
		return recent_posts.fetch(limit=10)

	def render(self):
		self.render_text = self.content.replace('\n', '<br>')
		return render_str('post.html', post = self)

class Comment(db.Model):
	author = db.StringProperty(required = True)
	content = db.StringProperty(required = True)
	created = db.DateTimeProperty(auto_now_add = True)

	@classmethod
	def by_id(cls, comment_id, parent):
		return Comment.get_by_id(int(comment_id), parent = parent)

	@classmethod
	def all_comments(cls, parent_post):
		comments = Comment.all().order('-created')
		return comments.ancestor(parent_post)

	def render(self, username, post_id):
		return render_str('comment.html', comment = self,
			username = username, post_id = post_id)

class Like(db.Model):
	user_id = db.IntegerProperty(required = True)
	value = db.IntegerProperty(required = True)

	@classmethod
	def check_previous_likes(self, user_id, parent_post):
		likes = Like.all().filter('user_id =', user_id)
		return likes.ancestor(parent_post).get()

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

	def comment_check(self):
		if self.request.get('comment-form'):
			return True

class MainPage(Handler):
	def get(self):
		self.render('mainpage.html', posts = Post.most_recent())

	def post(self):
		self.login_handler('mainpage.html', posts = Post.most_recent())

class RegistrationPage(Handler):
	def get(self):
		if self.user:
			self.redirect('/')
		else:
			self.render('registration.html')

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

class Logout(Handler):
	def get(self):
		self.logout_cookie()
		self.redirect('/')

class CreatePost(Handler):
	def get(self):
		if self.user:
			self.render('newpost.html', new_post = True)
		else:
			self.redirect('/')

	def post(self):
		subject = self.request.get('subject')
		content = self.request.get('content')

		subject_error = ''
		content_error = ''

		if not subject:
			subject_error = 'Please enter a subject.'
		if not content:
			content_error = 'Please enter content for the post.'
		if subject_error or content_error:
			self.render('newpost.html', subject_error = subject_error,
				content_error = content_error, subject = subject,
				content = content, new_post = True)
		else:
			post = Post(author = self.user.username, subject = subject,
				content = content, likes = 0, comments = 0)
			post.put()
			self.redirect('/post/%s?new_post=true' % post.key().id())

class PostPermalink(Handler):
	def get(self, post_id):
		new_post = self.request.get('new_post')
		edited_post = self.request.get('edited_post')
		post = Post.by_id(post_id)
		comments = Comment.all_comments(post)

		self.render('permalink.html', post = Post.by_id(post_id),
			new_post = new_post, edited_post = edited_post,
			comments = comments, number_comments = post.comments)

	def post(self, post_id):
		if self.login_check():
			self.login_handler('permalink.html', post = Post.by_id(post_id))
		elif self.comment_check():
			content = self.request.get('content')
			post = Post.by_id(post_id)
			comment = Comment(author = self.user.username, content = content,
				parent = post)
			comment.put()
			post.comments += 1
			post.put()
			self.redirect('/post/%s#comments-section' % post_id)

class EditPost(Handler):
	def get(self, post_id):
		post = Post.by_id(post_id)
		if self.user:
			if post.author == self.user.username:
				self.render('newpost.html', edit_post = True, author = post.author,
					original_subject = post.subject, content = post.content,
					created = post.created, post_id = post_id, subject = post.subject)
			else:
				self.redirect('/')
		else:
			self.redirect('/')

	def post(self, post_id):
		subject = self.request.get('subject')
		content = self.request.get('content')
		post = Post.by_id(post_id)

		subject_error = ''
		content_error = ''

		if not subject:
			subject_error = 'Please enter a subject.'
		if not content:
			content_error = 'Please enter content for the post.'
		if subject_error or content_error:
			self.render('newpost.html', subject_error = subject_error,
				content_error = content_error, subject = subject,
				content = content, edit_post = True, author = post.author,
				created = post.created, post_id = post_id,
				original_subject = post.subject)
		else:
			if subject:
				post.subject = subject
			if content:
				post.content = content

			post.modified = datetime.datetime.now()
			post.put()
			self.redirect('/post/%s?edited_post=true' % post.key().id())

class DeletePost(Handler):
	def get(self, post_id):
		post = Post.by_id(post_id)
		subject = post.subject
		if self.user:
			if post.author == self.user.username:
				self.render('delete.html', subject = subject,
					delete_post = True)
				post.delete()
			else:
				self.redirect('/')
		else:
			self.redirect('/')

class DeleteComment(Handler):
	def get(self, post_id):
		post = Post.by_id(post_id)
		comment_id = self.request.get('comment')
		comment = Comment.by_id(comment_id, post)
		comment.delete()
		post.comments -= 1
		post.put()
		self.redirect('/post/%s#comments-section' % post_id)

class LikeHandler(Handler):
	def post(self):
		post_id = int(self.request.get('postId'))
		vote_value = int(self.request.get('voteValue'))
		post = Post.by_id(post_id)
		user_id = int(self.user.key().id())
		new_like_value = post.likes + vote_value

		if self.user:
			if self.user.username == post.author:
				self.write(json.dumps({'error': "You can't like your own posts.", 'post_id': post_id}))
			elif Like.check_previous_likes(user_id, post):
				self.write(json.dumps({'error': "You can't like a post multiple times.", 'post_id': post_id}))
			else:
				new_like = Like(user_id = user_id, value = vote_value, parent = post)
				new_like.put()
				post.likes = new_like_value
				post.put()
				self.write(json.dumps({'likes': new_like_value, 'post_id': post_id}))
		else:
			self.write(json.dumps({'error': "You must be logged in to like a post.", 'post_id': post_id}))

app = webapp2.WSGIApplication([('/', MainPage),
								('/register', RegistrationPage),
								('/logout', Logout),
								('/newpost', CreatePost),
								('/post/(\d+)', PostPermalink),
								('/edit/(\d+)', EditPost),
								('/delete/(\d+)', DeletePost),
								('/delete_comment/(\d+)', DeleteComment),
								('/like', LikeHandler)
								],
								debug = True)