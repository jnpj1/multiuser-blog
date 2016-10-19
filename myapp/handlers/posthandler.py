import datetime
from . import Handler
from myapp.models.models import Post, Comment, Like

class PostPermalink(Handler):
	def get(self, post_id):
		new_post = self.request.get('new_post')
		edited_post = self.request.get('edited_post')
		post = Post.by_id(post_id)
		comments = Comment.all_comments(post)

		self.render('permalink.html', post = post,
			new_post = new_post, edited_post = edited_post,
			comments = comments, number_comments = post.comments)

	def post(self, post_id):
		if self.login_check():
			self.login_handler('permalink.html', post = Post.by_id(post_id))
		elif self.request.get('comment-form'):
			post = Post.by_id(post_id)
			comments = Comment.all_comments(post)
			if self.user:
				content = self.request.get('content')

				if not content:
					self.render('permalink.html', post = post,
						comments = comments, number_comments = post.comments,
						content_error = True)
				else:
					post = Post.by_id(post_id)
					comment = Comment(author = self.user.username, content = content,
						parent = post)
					comment.put()
					post.comments += 1
					post.put()
					self.redirect('/post/%s#comments-section' % post_id)
			else:
				self.render('permalink.html', post = post, comments = comments,
					number_comments = post.comments, comment_error = True)

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
				comments = Comment.all_comments(post)
				for comment in comments:
					comment.delete()
				likes = Like.all_likes(post)
				for like in likes:
					like.delete()
				self.render('delete.html', subject = subject,
					delete_post = True)
				post.delete()
			else:
				self.redirect('/')
		else:
			self.redirect('/')