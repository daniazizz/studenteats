const submitButton = document.getElementById("trigger");
const userComment = document.getElementById("userComment");
const postedComments = document.getElementById("postedComments");
var firstComment = true;

/*This function is used for adding the different comments on the comment section
  - commentOfUser: the comment to add
  - userName: the username of whom wrote the comment
  - commentId: Id of the comment
  - mayDelete: boolean value that tells the function to add a "delete-button" on the comment
  - datum: datum of when the comment was posted
  - userUrl: link to the profile of the poster of the comment
  - sendUrl: Url where the ajax request should be send.
 */
function createComment(commentOfUser, userName, commentId, mayDelete, datum, userURL, sendUrl) {
    if (firstComment) {
		let intro = document.getElementById("intro");
		intro.parentNode.removeChild(intro);
		firstComment = false;
	}
	let newComment = document.createElement("section"); //Section containing all the elements about the comment.
	newComment.classList.add("oldComments");

	let meta = document.createElement("p"); //Paragraph containing some information about the comment (username + datum)
	meta.classList.add("metaData");
	meta.innerHTML = '<a href="' + userURL + '">' + userName + '</a>' + " - " + "<small>" + datum + "</small>";

	let comment = document.createElement("p"); //The comment itself
	comment.innerText = commentOfUser;

	newComment.appendChild(meta);
	newComment.appendChild(comment);
	postedComments.prepend(newComment);

	//A delete-button is created on all the comments that have been posted by the user.
	if (mayDelete) {
		let buttonDelete = document.createElement("button");
		buttonDelete.innerText = "Delete";
		buttonDelete.classList.add("btn");
		buttonDelete.classList.add("btn-sm");
 		buttonDelete.classList.add("btn-danger");
		buttonDelete.onclick = function() {
			$.ajax({
				url: sendUrl,
				method: "DELETE",
				data: {
					'comment_id': commentId
				},
				success: function() {
					newComment.parentNode.removeChild(newComment);
				}
			});
		};
		newComment.appendChild(buttonDelete);
	}
}

/* This function adds an event when the "comment" button is clicked on
    - sendUrl: url where the post request should be sended
    - username: username of the user writing the post
    - postId: Id of the post
    - userUrl: link to the profile of the user.
 */
function linkToSubmitButton(sendUrl, username, postId, userUrl) {
	submitButton.onclick = function() {
		if (userComment.value !== "") {
			let comment = userComment.value;
			$.ajax({
				url: sendUrl,
				method: "POST",
				data: {
					'content': comment,
					'author': username,
					'post_id': postId
				},
                //When the post-request is succesfull, the comment of the user is added to the comment section
				success: function(data) {
					createComment(comment, username, data.comment_id, true, "Now", userUrl, sendUrl);
				}
			});
			userComment.value = "";
		}
	}
}