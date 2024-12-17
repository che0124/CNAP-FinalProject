document.addEventListener('DOMContentLoaded', function() {
    fetch('/get_session_data')
    .then(response => response.json())
    .then(sessionData => {
        let headerRightContent;
        if (sessionData.user_id) {
            headerRightContent = `
                <a href="/logout">Logout</a>
            `;
        } else {
            headerRightContent = `
                <a href="/login">LogIn/SignUp</a>
            `;
        }

        const navbarHtml = `
            <nav id="sidebar" class="sidebar">
                <div class="nav-top">
                    <a class="nav-item" href="/">Home</a>
                    <a class="nav-item" href="/tags">Tags</a>
                    <a class="nav-item" href="/search">Search</a>
                    <a class="nav-item" href="/profile/${sessionData.user_id}">Profile</a>
                </div>
                <div class="nav-bottom">
                    <a class="nav-item" href="#">More</a>
                </div>
            </nav>
        `;

        const headerHtml = `
            <header class="header">
                <div class="header-left">
                    <a href="/">Joseph's site</a>
                </div>
                <div class="header-mid"></div>
                <div class="header-right">
                    ${headerRightContent}
                </div>
            </header>
        `;

        const body = document.body;
        body.insertAdjacentHTML('afterbegin', headerHtml);

        const gridContainer = document.getElementsByClassName('grid-container')[0];
        gridContainer.insertAdjacentHTML('afterbegin', navbarHtml);
    })
    .catch(error => {
        console.error('Error fetching session data:', error);
    });
});