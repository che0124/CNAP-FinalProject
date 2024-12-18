function createDashboard(sessionData) {
    const { username } = sessionData;
    const dashboard = `
        <div class="extra-content">
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
                    <a href="/logout" class="user-action">Switch</a>
                </div>
            </div>
        </div>
    `;

    const gridContainer = document.getElementsByClassName('grid-container')[0];
    gridContainer.insertAdjacentHTML('beforeend', dashboard);
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