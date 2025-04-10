from flask import Blueprint, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
import os
import sys
import subprocess
import traceback  # Add this for detailed error messages

# Add the project root to the Python path so imports work correctly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from pianoplayer.core import run_annotate

# Specify template_folder explicitly
app = Blueprint('app', __name__, template_folder='templates')

UPLOAD_FOLDER = os.path.abspath('uploads/')  # Use absolute path
OUTPUT_FOLDER = os.path.abspath('outputs/')  # Use absolute path
ALLOWED_EXTENSIONS = {'musicxml', 'xml', 'txt', 'mid', 'midi', 'mscz', 'mscx'}

# Make sure the uploads and outputs directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_hand_size_params(hand_size):
    """Convert hand size string to parameters for run_annotate"""
    # First, set all hand sizes to False
    params = {
        'hand_size_XXS': False,
        'hand_size_XS': False,
        'hand_size_S': False,
        'hand_size_M': False,
        'hand_size_L': False,
        'hand_size_XL': False,
        'hand_size_XXL': False
    }

    # Then set only the selected one to True
    if hand_size in ['XXS', 'XS', 'S', 'M', 'L', 'XL', 'XXL']:
        params[f'hand_size_{hand_size}'] = True
    else:
        # Default to M if not valid
        params['hand_size_M'] = True

    return params

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        print("Processing POST request")  # Debug
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)

        file = request.files['file']
        hand_size = request.form.get('hand_size')
        print(f"Received file: {file.filename}, Hand size: {hand_size}")  # Debug

        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            try:
                filename = secure_filename(file.filename)
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                print(f"Saving file to: {filepath}")  # Debug
                file.save(filepath)
                print(f"File saved successfully to {filepath}")  # Debug

                # Process the file with piano player
                output_filename = f"output_{filename}"
                if filename.endswith('.mid') or filename.endswith('.midi'):
                    output_filename = output_filename.rsplit('.', 1)[0] + '.txt'
                else:
                    output_filename = output_filename.rsplit('.', 1)[0] + '.xml'

                output_path = os.path.join(OUTPUT_FOLDER, output_filename)
                print(f"Output will be saved to: {output_path}")  # Debug

                # Set hand size parameters based on user selection
                hand_size_params = get_hand_size_params(hand_size)
                print(f"Using hand size parameters: {hand_size_params}")  # Debug

                try:
                    # Process the file with the piano player
                    print(f"Starting processing with run_annotate...")  # Debug


                    # Normal processing with run_annotate
                    run_annotate(
                        filename=filepath,
                        outputfile=output_path,
                        hand_size_XXS=hand_size_params['hand_size_XXS'],
                        hand_size_XS=hand_size_params['hand_size_XS'],
                        hand_size_S=hand_size_params['hand_size_S'],
                        hand_size_M=hand_size_params['hand_size_M'],
                        hand_size_L=hand_size_params['hand_size_L'],
                        hand_size_XL=hand_size_params['hand_size_XL'],
                        hand_size_XXL=hand_size_params['hand_size_XXL']
                    )

                    print(f"Processing completed successfully")  # Debug
                    flash('File successfully processed!')
                    return redirect(url_for('app.result', filename=output_filename, hand_size=hand_size))
                except IndexError as e:
                    error_traceback = traceback.format_exc()
                    print(f"IndexError in processing: {str(e)}")
                    print(error_traceback)
                    flash('The file could not be processed correctly. It may not contain valid musical data or be in an unsupported format.')

                    # Create a simple error file so the user has something to download
                    with open(output_path, 'w') as f:
                        f.write(f"Error processing file {filename} with hand size {hand_size}\n")
                        f.write("The file could not be processed correctly. It may not contain valid musical data or be in an unsupported format.\n")
                        f.write(f"Error details: {str(e)}\n")

                    return redirect(url_for('app.result', filename=output_filename, hand_size=hand_size))
                except Exception as e:
                    error_traceback = traceback.format_exc()
                    print(f"Error in processing: {str(e)}")
                    print(error_traceback)
                    flash(f'Error processing file: {str(e)}')
                    return redirect(request.url)
            except Exception as e:
                error_traceback = traceback.format_exc()
                print(f"Error in file saving: {str(e)}")
                print(error_traceback)
                flash(f'Error saving file: {str(e)}')
                return redirect(request.url)
        else:
            flash(f'Invalid file type. Allowed types: {", ".join(ALLOWED_EXTENSIONS)}')
            return redirect(request.url)

    # For GET requests or if POST fails
    return render_template('index.html')

@app.route('/result')
def result():
    filename = request.args.get('filename')
    hand_size = request.args.get('hand_size')
    print(f"Result page for file: {filename}, hand size: {hand_size}")  # Debug

    # Get the absolute path to the processed file
    output_path = os.path.join(OUTPUT_FOLDER, filename) if filename else None
    print(f"Checking output file at: {output_path}")  # Debug

    # Check if the file exists
    file_exists = os.path.isfile(output_path) if output_path else False
    print(f"File exists: {file_exists}")  # Debug

    return render_template(
        'result.html',
        filename=filename,
        hand_size=hand_size,
        file_exists=file_exists,
        output_path=output_path
    )

@app.route('/download/<filename>')
def download_file(filename):
    from flask import send_from_directory
    print(f"Attempting to download file: {filename} from {OUTPUT_FOLDER}")  # Debug
    return send_from_directory(OUTPUT_FOLDER, filename, as_attachment=True)