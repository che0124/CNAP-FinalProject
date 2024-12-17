function createDashboard(sessionData) {
    const { username } = sessionData;
    const dashboard = `
        <div class="dashboard-content">
            <div class="user-info">
                <div class="user">
                    <a href="/profile">
                        <div class="user-image">
                            <img src="/static/assets/user.png" alt="User Image">
                        </div>
                    </a>
                    <div class="user-names">
                        <a href="/profile/${sessionData.user_id}">
                            <span class="username">${username}</span>
                        </a>
                        <span class="name">Name</span>
                    </div>
                </div>
                <a href="./../auth/login.html" class="user-action">Switch</a>
            </div>
        </div>
    `;

    const gridContainer = document.getElementsByClassName('extra-content')[0];
    gridContainer.insertAdjacentHTML('afterbegin', dashboard);
}

function createPostPage(tag_id) {
    window.location.href = `/createPost/${tag_id}`;
}

document.addEventListener('DOMContentLoaded', () => {
    fetch('/get_session_data')
    .then(response => {
        if (!response.ok) {
            throw new Error('Failed to fetch session data');
        }
        return response.json();
    })
    .then(sessionData => {
        if (sessionData.error) {
            console.error(sessionData.error);
            return;
        }
        createDashboard(sessionData);
    })
    .catch(error => {
        console.error('Error:', error);
    });
});

document.addEventListener('DOMContentLoaded', function() {
    const tags = document.querySelectorAll('.posts-tags a');

    tags.forEach(tag => {
        tag.addEventListener('click', function() {
            // Remove active class from all tags
            tags.forEach(t => t.classList.remove('active'));
            // Add active class to the clicked tag
            this.classList.add('active');
        });
    });
});