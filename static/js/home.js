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