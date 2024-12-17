document.addEventListener('DOMContentLoaded', function() {
    function updateTime() {
        const now = new Date();
        const year = now.getFullYear();
        const month = (now.getMonth() + 1).toString().padStart(2, '0');
        const day = now.getDate().toString().padStart(2, '0');
        const hours = now.getHours().toString().padStart(2, '0');
        const minutes = now.getMinutes().toString().padStart(2, '0');

        const formattedTime = `${year}年${month}月${day}日 ${hours}:${minutes}`;
        document.getElementById('current-time').textContent = formattedTime;
    }

    updateTime();
    setInterval(updateTime, 1000);

    document.getElementById('createPostForm').addEventListener('submit', function(event) {
        event.preventDefault();
        sendPost();
    });
});

