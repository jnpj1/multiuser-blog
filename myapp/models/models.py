from google.appengine.ext import db
from myapp.functions.functions import *

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
		if not user:
			return False
		else:
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

	@classmethod
	def all_likes(cls, parent_post):
		return Like.all().ancestor(parent_post)