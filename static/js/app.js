$(document).ready(function() {
	$('.new-post-success').fadeOut(3000);

	// Process clicking of like/dislike icons
	$('.fa').click(function(event) {
		$target = $(event.currentTarget);
		postId = $target.parents('.post-footer').data('postid')

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
			if (data['error']) {
				console.log(this);
				$(dataSelectorString).find('.like-error').fadeIn(500).html(data.error);
				setTimeout(function() {
					$(dataSelectorString).find('.like-error').fadeOut(1000);
				}, 2000);
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

	$('.comment-button').click(function() {
		$('.comments-form-box').slideToggle('fast');
	});

	$('.login-alternative').click(function() {
		$('.login').click();
	});
});