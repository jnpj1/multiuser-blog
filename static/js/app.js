// Defines ajax functionality for like handling and comment editing
// Handles some simple form and success/error display functionality
$(document).ready(function() {
	$('.new-post-success').fadeOut(3000);

	// Process clicking of like/dislike icons
	$('.fa').click(function(event) {
		var $target = $(event.currentTarget);
		var postId = $target.parents('.post-footer').data('postid');

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

		// AJAX for post request to add like to up/down voted post
		$.ajax({
			type: 'post',
			dataType: 'json',
			data: data,
			url: '/like'
		}).done(function(data) {
			// Adds error message or updated like count to page
			var dataSelectorString = '[data-postid="' + postId + '"]';
			if (data['error']) {
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

	// Show login form
	$('.login').click(function() {
		$('.login-form').slideDown('fast');
		$('.login-error').hide('fast');
	});

	// Show login form
	$('.login-alternative').click(function() {
		$('.login').click();
	});

	// Shows new comment form
	$('.comment-button').click(function() {
		$('.comments-form-box').slideToggle('fast');
	});

	// Opens modal with comment editing form
	$('.comment-edit').click(function(event) {
		var $target = $(event.currentTarget);
		$target.parents('.comment').find('.modal').css('display', 'block');
	});

	// Closes modal when user clicks on modal's 'X'
	$('.modal-close').click(function(event) {
		$('.modal').css('display', 'none');
	});

	// Handles comment editing
	$('.comment-edit-form').on('submit', function(event) {
		event.preventDefault();
		var $target = $(event.currentTarget);
		var postId = $('.post-footer').data('postid');
		var commentId = $target.parents('.comment').data('commentid');
		var commentSelectorString = '[data-commentid="' + commentId + '"]';
		var content = $(commentSelectorString).find('input[name="edited-content"]').val();

		var data = {
			'postId' : postId,
			'commentId' : commentId,
			'newContent' : content
		};

		// AJAX for post request to edit comment content
		$.ajax({
			type: 'post',
			data: data,
			url: '/edit_comment'
		}).done(function(data) {
			// Adds updated content to page
			$(commentSelectorString).find('.comment-text').html(content);
			console.log($(commentSelectorString));
			$('.modal-close').click();
		}).error(function(error) {
			alert('Failed to update comment.  Please try again.')
		});
	});
});