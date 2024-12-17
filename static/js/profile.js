document.addEventListener('DOMContentLoaded', function() {
    const followBtn = document.getElementById('follow-btn');
    if (followBtn) {
        followBtn.addEventListener('click', function() {
            const userId = this.getAttribute('data-user-id');
            const action = this.textContent.trim().toLowerCase();
            const url = action === 'follow' ? `/follow/${userId}` : `/unfollow/${userId}`;
            fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    if (action === 'follow') {
                        this.textContent = 'Unfollow';
                        this.classList.remove('follow');
                        this.classList.add('unfollow');
                    } else {
                        this.textContent = 'Follow';
                        this.classList.remove('unfollow');
                        this.classList.add('follow');
                    }
                    // Optionally update followers count
                } else {
                    alert(data.error);
                }
            })
            .catch(error => {
                console.error('Error:', error);
            });
        });
    }
});