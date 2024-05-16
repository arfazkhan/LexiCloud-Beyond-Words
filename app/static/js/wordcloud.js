document.addEventListener('DOMContentLoaded', function() {
    var form = document.getElementById('wordcloud-form');
    form.addEventListener('submit', function(event) {
        event.preventDefault();
        var formData = new FormData(form);
        fetch('/', {
            method: 'POST',
            body: formData
        })
        .then(response => response.text())
        .then(data => {
            document.getElementById('wordcloud-container').innerHTML = data;
        })
        .catch(error => {
            console.error('Error:', error);
        });
    });
});
