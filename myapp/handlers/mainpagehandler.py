from myapp.functions.functions import *
from . import Handler
from myapp.models.models import Post

class MainPage(Handler):
	def get(self):
		self.render('mainpage.html', posts = Post.most_recent())

	def post(self):
		self.login_handler('mainpage.html', posts = Post.most_recent())

class Logout(Handler):
	def get(self):
		self.logout_cookie()
		self.redirect('/')