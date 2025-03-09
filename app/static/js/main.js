class FileUploader {
    constructor() {
        this.files = [];
        this.initializeEventListeners();
    }

    initializeEventListeners() {
        const dropzone = document.getElementById('dropzone');
        const fileInput = document.getElementById('fileInput');
        const processButton = document.getElementById('processButton');

        dropzone.addEventListener('click', () => fileInput.click());
        dropzone.addEventListener('dragover', (e) => {
            e.preventDefault();
            e.stopPropagation();
            dropzone.classList.add('dragover');
        });
        dropzone.addEventListener('dragleave', () => {
            dropzone.classList.remove('dragover');
        });
        dropzone.addEventListener('drop', (e) => {
            e.preventDefault();
            e.stopPropagation();
            dropzone.classList.remove('dragover');
            this.handleFiles(e.dataTransfer.files);
        });

        fileInput.addEventListener('change', (e) => {
            this.handleFiles(e.target.files);
        });

        processButton.addEventListener('click', () => {
            this.processFiles();
        });
    }

    async handleFiles(fileList) {
        if (fileList.length === 0) {
            this.showError('No files selected');
            return;
        }

        const formData = new FormData();
        let hasValidFiles = false;

        for (let file of fileList) {
            if (file.type === 'application/pdf') {
                formData.append('files[]', file);
                hasValidFiles = true;
            } else {
                this.showError(`${file.name} is not a PDF file`);
            }
        }

        if (!hasValidFiles) {
            return;
        }

        this.showMessage('Uploading files...');

        try {
            const response = await fetch('/upload', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Upload failed');
            }

            const results = await response.json();
            
            if (results.length === 0) {
                this.showError('No files were processed');
                return;
            }

            this.files = [...this.files, ...results];
            this.updateFileList();
            document.getElementById('processButton').disabled = false;
            this.showMessage('Files uploaded successfully!');
        } catch (error) {
            console.error('Upload error:', error);
            this.showError(`Upload failed: ${error.message}`);
        }
    }

    showError(message) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'error-message';
        messageDiv.textContent = message;
        document.querySelector('.container').insertBefore(
            messageDiv,
            document.getElementById('fileList')
        );
        setTimeout(() => messageDiv.remove(), 5000);
    }

    showMessage(message) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'info-message';
        messageDiv.textContent = message;
        document.querySelector('.container').insertBefore(
            messageDiv,
            document.getElementById('fileList')
        );
        setTimeout(() => messageDiv.remove(), 3000);
    }

    updateFileList() {
        const fileList = document.getElementById('fileList');
        fileList.innerHTML = this.files.map(file => `
            <div class="file-item">
                <h3>${file.original_name}</h3>
                <div class="metadata">
                    ${Object.entries(file.metadata).map(([key, value]) => 
                        `<div><strong>${key}:</strong> ${value}</div>`
                    ).join('')}
                </div>
            </div>
        `).join('');
    }

    async processFiles() {
        const progressSection = document.getElementById('progressSection');
        const progressBar = document.getElementById('progressBar');
        const progressText = document.getElementById('progressText');
        
        progressSection.style.display = 'block';
        
        try {
            const response = await fetch('/process', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ files: this.files })
            });
            
            const results = await response.json();
            
            // Update progress bar
            progressBar.style.width = '100%';
            progressText.textContent = 'Processing complete!';
            
            // Generate download links
            results.forEach(result => {
                if (result.status === 'success') {
                    const downloadLink = document.createElement('a');
                    downloadLink.href = `/download/${result.processed_name}`;
                    downloadLink.textContent = `Download ${result.original_name}`;
                    downloadLink.className = 'button';
                    progressSection.appendChild(downloadLink);
                }
            });
        } catch (error) {
            console.error('Processing error:', error);
            progressText.textContent = 'Error processing files';
        }
    }
}

// Initialize the uploader when the page loads
document.addEventListener('DOMContentLoaded', () => {
    new FileUploader();
}); 