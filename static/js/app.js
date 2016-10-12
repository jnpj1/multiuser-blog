$(document).ready(function() {

	// Process clicking of like/dislike icons
	$('.fa').click(function(event) {
		$target = $(event.currentTarget);
		postId = $target.parent('.post-footer').data('postid')

		// Assign value of vote based on icon clicked
		var voteValue = 0;
		if ($target.hasClass('fa-thumbs-down')) {
			voteValue = -1;
		} else {
			voteValue = 1;
		}

		var data = {
			'voteValue' : voteValue,
			'postId' : postId
		}

		var urlString = '/post/' + postId + '/'

		// AJAX
		$.ajax({
			type: 'post',
			dataType: 'json',
			data: data,
			url: '/like'
		}).done(function(data) {
			var dataSelectorString = '[data-postid="' + data['post_id'] + '"]';
			console.log(data);
			if (data['error']) {
				console.log(data.error);
				console.log($(dataSelectorString).find('.like-error'));
				$(dataSelectorString).find('.like-error').html(data.error);
			} else {
				$(dataSelectorString).find('.like-counter').html('Likes: ' + data.likes);
			}
		}).error(function(error) {
			alert('Failed to log like.  Please try again.')
		});
	});

	$('.login').click(function() {
		$('.login-form').slideDown('fast');
		$('.login-error').hide('fast');
	});
});