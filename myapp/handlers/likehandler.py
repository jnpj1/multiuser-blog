import json
from . import Handler
from myapp.models.models import Post, Like

class LikeHandler(Handler):
	def post(self):
		post_id = int(self.request.get('postId'))
		vote_value = int(self.request.get('voteValue'))
		post = Post.by_id(post_id)
		new_like_value = post.likes + vote_value

		if self.user:
			user_id = int(self.user.key().id())
			if self.user.username == post.author:
				self.write(json.dumps({'error': "You can't like your own posts."}))
			elif Like.check_previous_likes(user_id, post):
				self.write(json.dumps({'error': "You can't like a post multiple times."}))
			else:
				new_like = Like(user_id = user_id, value = vote_value, parent = post)
				new_like.put()
				post.likes = new_like_value
				post.put()
				self.write(json.dumps({'likes': new_like_value}))
		else:
			self.write(json.dumps({'error': "You must be logged in to like a post."}))
