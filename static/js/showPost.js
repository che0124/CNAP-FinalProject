document.addEventListener('DOMContentLoaded', function() {
    const likeIcon = document.querySelector('.like-icon');
    console.log(likeIcon);
    if (likeIcon) {
        likeIcon.addEventListener('click', function() {
            const postId = this.getAttribute('data-post-id');
            fetch(`/like_post/${postId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    const likesCountElem = document.querySelector('.likes-count');
                    let likesCount = parseInt(likesCountElem.textContent);
                    if (data.liked) {
                        likesCount += 1;
                        this.classList.add('liked');
                    } else {
                        likesCount -= 1;
                        this.classList.remove('liked');
                    }
                    likesCountElem.textContent = likesCount;
                } else {
                    alert('Error liking post');
                }
            })
            .catch(error => {
                console.error('Error:', error);
            });
        });
    }
});