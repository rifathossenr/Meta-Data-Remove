from flask import render_template, jsonify, request, send_file
from app import app
from app.utils import remove_xmp_metadata, get_xmp_metadata, cleanup_old_files
import os
from werkzeug.utils import secure_filename
import uuid

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    app.logger.info('Upload request received')
    
    if 'files[]' not in request.files:
        app.logger.error('No files[] in request.files')
        return jsonify({'error': 'No file part'}), 400
    
    files = request.files.getlist('files[]')
    app.logger.info(f'Received {len(files)} files')
    results = []
    
    for file in files:
        if file.filename == '':
            app.logger.warning('Empty filename received')
            continue
            
        if file and file.filename.lower().endswith('.pdf'):
            try:
                # Generate unique filename
                filename = str(uuid.uuid4()) + '.pdf'
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                app.logger.info(f'File saved successfully: {filename}')
                
                # Extract metadata
                metadata = get_xmp_metadata(filepath)
                
                results.append({
                    'original_name': file.filename,
                    'temp_name': filename,
                    'metadata': metadata
                })
            except Exception as e:
                app.logger.error(f'Error processing file {file.filename}: {str(e)}')
                return jsonify({'error': str(e)}), 500
    
    return jsonify(results)

@app.route('/process', methods=['POST'])
def process_files():
    files = request.json.get('files', [])
    results = []
    
    for file in files:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file['temp_name'])
        if os.path.exists(filepath):
            # Process the file
            output_path = os.path.join(
                app.config['UPLOAD_FOLDER'],
                'processed_' + file['temp_name']
            )
            success = remove_xmp_metadata(filepath, output_path)
            
            if success:
                results.append({
                    'original_name': file['original_name'],
                    'processed_name': 'processed_' + file['temp_name'],
                    'status': 'success'
                })
            else:
                results.append({
                    'original_name': file['original_name'],
                    'status': 'error'
                })
    
    return jsonify(results)

@app.route('/download/<filename>')
def download_file(filename):
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(filepath):
        return send_file(
            filepath,
            as_attachment=True,
            download_name=filename.replace('processed_', '')
        )
    return jsonify({'error': 'File not found'}), 404 