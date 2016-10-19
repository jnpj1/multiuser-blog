from . import Handler
from myapp.models.models import Post, Comment

class EditComment(Handler):
	def post(self):
		comment_id = int(self.request.get('commentId'))
		post_id = int(self.request.get('postId'))
		post = Post.by_id(post_id)
		comment = Comment.by_id(comment_id, post)

		if self.user.username == comment.author:
			comment.content = self.request.get('newContent')
			comment.put()
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