document.addEventListener('DOMContentLoaded', function () {
    const uploadForm = document.getElementById('upload-form');
    const fileInput = document.getElementById('file');
    const handSizeSelect = document.getElementById('hand_size');
    const resultDiv = document.getElementById('result');

    uploadForm.addEventListener('submit', function (event) {
        event.preventDefault();

        // Validate that a file is selected
        if (!fileInput.files || fileInput.files.length === 0) {
            resultDiv.innerHTML = '<div class="alert alert-danger">Please select a file to upload</div>';
            return;
        }

        const formData = new FormData();
        formData.append('file', fileInput.files[0]);
        formData.append('hand_size', handSizeSelect.value);

        // Show loading indicator
        resultDiv.innerHTML = '<div class="alert alert-info">Processing your file, please wait...</div>';

        fetch('/upload', {
            method: 'POST',
            body: formData
        })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok ' + response.statusText);
                }
                return response.json();
            })
            .then(data => {
                if (data.success) {
                    resultDiv.innerHTML = '<div class="alert alert-success">File processed successfully!</div>';
                    // Redirect to processing status page if applicable
                    if (data.task_id) {
                        window.location.href = `/processing-status?task_id=${data.task_id}&filename=${data.filename}&hand_size=${handSizeSelect.value}`;
                    }
                } else {
                    resultDiv.innerHTML = '<div class="alert alert-danger">Error processing file: ' + (data.error || 'Unknown error') + '</div>';
                }
            })
            .catch(error => {
                resultDiv.innerHTML = '<div class="alert alert-danger">An error occurred: ' + error.message + '</div>';
            });
    });

    // Optional: Add a visual indicator when a file is selected
    fileInput.addEventListener('change', function () {
        if (fileInput.files && fileInput.files.length > 0) {
            const fileName = fileInput.files[0].name;
            const fileLabel = fileInput.nextElementSibling; // Assuming there's a label next to the input
            if (fileLabel) {
                fileLabel.textContent = fileName;
            }
        }
    });
});