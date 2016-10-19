import webapp2
from myapp.handlers.mainpagehandler import MainPage, Logout
from myapp.handlers.registrationhandler import RegistrationPage
from myapp.handlers.posthandler import PostPermalink, CreatePost, EditPost, DeletePost
from myapp.handlers.commenthandler import EditComment, DeleteComment
from myapp.handlers.likehandler import LikeHandler

app = webapp2.WSGIApplication([('/', MainPage),
								('/register', RegistrationPage),
								('/logout', Logout),
								('/post/(\d+)', PostPermalink),
								('/newpost', CreatePost),
								('/edit/(\d+)', EditPost),
								('/delete/(\d+)', DeletePost),
								('/edit_comment', EditComment),
								('/delete_comment/(\d+)', DeleteComment),
								('/like', LikeHandler)
								],
								debug = True)