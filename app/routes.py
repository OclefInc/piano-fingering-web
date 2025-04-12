from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, send_from_directory
from werkzeug.utils import secure_filename
import os
import sys
import traceback
import threading
import time
import uuid
import json
import random
from datetime import datetime

# Create the blueprint with the correct name
app_bp = Blueprint('app', __name__, template_folder='templates')

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the run_annotate function directly - no more celery imports
try:
    from pianoplayer.core import run_annotate
except ImportError:
    print("WARNING: Could not import run_annotate function")
    run_annotate = None

UPLOAD_FOLDER = os.path.abspath('uploads/')
OUTPUT_FOLDER = os.path.abspath('outputs/')
ALLOWED_EXTENSIONS = {'musicxml', 'xml', 'mxl'}

# Make sure directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Dictionary to track background tasks
BACKGROUND_TASKS = {}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_hand_size_params(hand_size):
    """Convert hand size string to parameters for run_annotate"""
    # Set all hand sizes to False
    params = {
        'hand_size_XXS': False,
        'hand_size_XS': False,
        'hand_size_S': False,
        'hand_size_M': False,
        'hand_size_L': False,
        'hand_size_XL': False,
        'hand_size_XXL': False
    }

    # Set only the selected one to True
    if hand_size in ['XXS', 'XS', 'S', 'M', 'L', 'XL', 'XXL']:
        params[f'hand_size_{hand_size}'] = True
    else:
        # Default to M if not valid
        params['hand_size_M'] = True

    return params

def process_file_task(filepath, output_path, hand_size_params, task_id):
    """Process a file in a background thread with file-based progress tracking"""
    try:
        # Determine status file path
        status_dir = os.path.dirname(output_path)
        status_file = os.path.join(status_dir, f"status_{task_id}.json")

        # Initialize status in file
        with open(status_file, 'w') as f:
            json.dump({
                'status': 'processing',
                'progress': 0,
                'measure': 0,
                'total_measures': 100,
                'message': 'Starting processing',
                'last_update': datetime.now().isoformat()
            }, f)

        # Create progress callback function
        def progress_callback(measure=0, total=100, status=""):
            progress = int((measure / total) * 100) if total > 0 else 0
            # print(f"Progress: {progress}% - {status}")

            # Update status file
            try:
                with open(status_file, 'w') as f:
                    json.dump({
                        'status': 'processing',
                        'progress': progress,
                        'measure': measure,
                        'total_measures': total,
                        'message': status,
                        'last_update': datetime.now().isoformat()
                    }, f)
            except Exception as e:
                print(f"Error updating status file: {str(e)}")

        # Run the processor with callback
        if run_annotate:
            run_annotate(
                filename=filepath,
                outputfile=output_path,
                callback=progress_callback,
                **hand_size_params
            )

        # Update final status
        with open(status_file, 'w') as f:
            json.dump({
                'status': 'completed',
                'progress': 100,
                'filename': os.path.basename(output_path),
                'last_update': datetime.now().isoformat()
            }, f)

        print(f"File processing completed: {output_path}")
    except Exception as e:
        # Log the error
        print(f"Error processing file: {str(e)}")
        traceback.print_exc()

        # Update error status
        try:
            with open(status_file, 'w') as f:
                json.dump({
                    'status': 'failed',
                    'error': str(e),
                    'filename': os.path.basename(output_path),
                    'last_update': datetime.now().isoformat()
                }, f)
        except Exception as write_error:
            print(f"Error updating status file: {str(write_error)}")

def cleanup_status_files(max_age_hours=24):
    """Clean up old status files"""
    try:
        current_time = time.time()
        for filename in os.listdir(OUTPUT_FOLDER):
            if filename.startswith('status_') and filename.endswith('.json'):
                filepath = os.path.join(OUTPUT_FOLDER, filename)
                file_age = current_time - os.path.getmtime(filepath)
                # If file is older than max_age_hours
                if file_age > (max_age_hours * 3600):
                    os.remove(filepath)
    except Exception as e:
        print(f"Error cleaning up status files: {str(e)}")

@app_bp.route('/', methods=['GET', 'POST'])
def index():
    if random.random() < 0.1:  # ~10% of requests
        cleanup_status_files()
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)

        file = request.files['file']
        hand_size = request.form.get('hand_size')

        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            try:
                # Save the uploaded file
                filename = secure_filename(file.filename)
                # append timestamp to filename to avoid overwriting
                timestamp = int(time.time())
                filename = f"{timestamp}_{filename}"
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                print(f"Saving file to: {filepath}")
                file.save(filepath)

                # Get hand size parameters
                hand_size_params = get_hand_size_params(hand_size)

                # Create output filename
                output_filename = f"{hand_size}_{filename}"
                if filename.endswith('.mid') or filename.endswith('.midi'):
                    output_filename = output_filename.rsplit('.', 1)[0] + '.txt'
                else:
                    output_filename = output_filename.rsplit('.', 1)[0] + '.musicxml'

                # Create output path
                output_path = os.path.join(OUTPUT_FOLDER, output_filename)

                # Generate a task ID
                task_id = str(uuid.uuid4())

                # Start a background thread for processing
                thread = threading.Thread(
                    target=process_file_task,
                    args=(filepath, output_path, hand_size_params, task_id)
                )
                thread.daemon = True
                thread.start()

                # Redirect to processing status page
                return redirect(url_for('app.processing_status', task_id=task_id, filename=output_filename, hand_size=hand_size))

            except Exception as e:
                error_traceback = traceback.format_exc()
                print(f"Error in file processing: {str(e)}")
                print(error_traceback)
                flash(f'Error processing file: {str(e)}')
                return redirect(request.url)
        else:
            flash(f'Invalid file type. Allowed types: {", ".join(ALLOWED_EXTENSIONS)}')
            return redirect(request.url)

    # For GET requests or if POST fails
    return render_template('index.html')

@app_bp.route('/processing-status')
def processing_status():
    task_id = request.args.get('task_id')
    filename = request.args.get('filename')
    hand_size = request.args.get('hand_size')

    # Use the processing.html template
    return render_template(
        'processing.html',
        task_id=task_id,
        filename=filename,
        hand_size=hand_size
    )

@app_bp.route('/check-status/<task_id>')
def check_status(task_id):
    """API endpoint for checking task status via file"""
    filename = request.args.get('filename')
    hand_size = request.args.get('hand_size', '')

    # Try to read from status file
    status_file = os.path.join(OUTPUT_FOLDER, f"status_{task_id}.json")

    if os.path.exists(status_file):
        try:
            # Check if file is being written to (avoid read errors)
            last_mod_time = os.path.getmtime(status_file)
            current_time = time.time()

            # If file was modified in the last second, wait briefly
            if current_time - last_mod_time < 1:
                time.sleep(0.5)

            with open(status_file, 'r') as f:
                status_data = json.load(f)

            # Add hand_size to response if it exists
            if hand_size:
                status_data['hand_size'] = hand_size

            return jsonify(status_data)
        except json.JSONDecodeError:
            # Handle potential corruption during writing
            return jsonify({'status': 'processing', 'progress': 0})
        except Exception as e:
            print(f"Error reading status file: {str(e)}")

    # Fallback to file-based checking
    if filename:
        output_path = os.path.join(OUTPUT_FOLDER, filename)
        if os.path.isfile(output_path):
            return jsonify({
                'status': 'completed',
                'filename': filename,
                'hand_size': hand_size
            })

    # If we don't have any status, assume it's still processing
    return jsonify({'status': 'processing', 'hand_size': hand_size})

@app_bp.route('/result')
def result():
    filename = request.args.get('filename')
    hand_size = request.args.get('hand_size')

    output_path = os.path.join(OUTPUT_FOLDER, filename) if filename else None
    file_exists = os.path.isfile(output_path) if output_path else False

    return render_template(
        'result.html',
        filename=filename,
        hand_size=hand_size,
        file_exists=file_exists,
        output_path=output_path
    )

@app_bp.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(OUTPUT_FOLDER, filename, as_attachment=True)