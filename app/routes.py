from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, send_from_directory
from werkzeug.utils import secure_filename
import os
import sys
import traceback
import threading
import time
import uuid

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
ALLOWED_EXTENSIONS = {'musicxml', 'xml', 'txt', 'mid', 'midi', 'mscz', 'mscx'}

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
    """Process a file in a background thread"""
    try:
        # Update task status
        BACKGROUND_TASKS[task_id] = {'status': 'processing'}

        # Create a marker file to indicate processing started
        with open(output_path, 'w') as f:
            f.write("Processing started...\n")

        # Run the processor
        if run_annotate:
            run_annotate(
                filename=filepath,
                outputfile=output_path,
                **hand_size_params
            )
        else:
            # Simulate processing if run_annotate is not available (for testing)
            time.sleep(5)  # Simulate processing time
            with open(output_path, 'w') as f:
                f.write(f"Simulated processing for {filepath}\n")
                f.write(f"Hand size parameters: {hand_size_params}\n")

        # Update task status
        BACKGROUND_TASKS[task_id] = {
            'status': 'completed',
            'filename': os.path.basename(output_path)
        }

        print(f"File processing completed: {output_path}")
    except Exception as e:
        # Log the error
        print(f"Error processing file: {str(e)}")
        traceback.print_exc()

        # Create an error file
        try:
            with open(output_path, 'w') as f:
                f.write(f"ERROR: Could not process {filepath}\n")
                f.write(f"Error details: {str(e)}\n")
        except Exception as write_error:
            print(f"Error creating error file: {str(write_error)}")

        # Update task status
        BACKGROUND_TASKS[task_id] = {
            'status': 'failed',
            'error': str(e),
            'filename': os.path.basename(output_path)
        }

@app_bp.route('/', methods=['GET', 'POST'])
def index():
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
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                print(f"Saving file to: {filepath}")
                file.save(filepath)

                # Create output filename
                output_filename = f"output_{filename}"
                if filename.endswith('.mid') or filename.endswith('.midi'):
                    output_filename = output_filename.rsplit('.', 1)[0] + '.txt'
                else:
                    output_filename = output_filename.rsplit('.', 1)[0] + '.xml'

                # Create output path
                output_path = os.path.join(OUTPUT_FOLDER, output_filename)

                # Get hand size parameters
                hand_size_params = get_hand_size_params(hand_size)

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
    """API endpoint for checking task status via AJAX"""
    filename = request.args.get('filename')

    # First check our task dictionary
    if task_id in BACKGROUND_TASKS:
        return jsonify(BACKGROUND_TASKS[task_id])

    # Fallback to file-based checking
    if filename:
        output_path = os.path.join(OUTPUT_FOLDER, filename)
        if os.path.isfile(output_path):
            return jsonify({
                'status': 'completed',
                'filename': filename
            })

    # If we don't have any status, assume it's still processing
    return jsonify({'status': 'processing'})

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