document.addEventListener('DOMContentLoaded', function() {
    const uploadForm = document.getElementById('upload-form');
    const fileInput = document.getElementById('file-input');
    const handSizeSelect = document.getElementById('hand-size-select');
    const resultDiv = document.getElementById('result');

    uploadForm.addEventListener('submit', function(event) {
        event.preventDefault();

        const formData = new FormData();
        formData.append('file', fileInput.files[0]);
        formData.append('hand_size', handSizeSelect.value);

        fetch('/upload', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                resultDiv.innerHTML = '<p>File processed successfully!</p>';
            } else {
                resultDiv.innerHTML = '<p>Error processing file: ' + data.error + '</p>';
            }
        })
        .catch(error => {
            resultDiv.innerHTML = '<p>An error occurred: ' + error.message + '</p>';
        });
    });
});