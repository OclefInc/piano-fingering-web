# Piano Fingering Web Application

This project is a Flask web application that allows users to upload musical files and select a hand size for fingering processing. The application processes the uploaded files and provides results based on the selected hand size.

# Acknowledgments

pianoplayer is a hard fork of Marco Musy [pianoplayer](https://github.com/marcomusy/pianoplayer)
We use [opensheetmusicdisplay](https://opensheetmusicdisplay.org) for rendering musicxml


## Project Structure

```
piano-fingering
├── pianoplayer                     # Core library for piano fingering
│   ├── __init__.py                 # Package initialization
│   ├── core.py                     # Main functions for fingering annotation
│   ├── hand.py                     # Hand model and fingering algorithms
│   ├── scorereader.py              # MusicXML and PIG file parsing
│   └── utils.py                    # Utility functions
│
├── app                             # Flask web application
│   ├── __init__.py                 # Flask app initialization
│   ├── routes.py                   # Web routes and API endpoints
│   ├── static
│   │   ├── css                     # Stylesheets
│   │   ├── js                      # JavaScript files
│   │   │   └── osmd                # OpenSheetMusicDisplay library
│   │   └── uploads                 # Temporary storage for uploads
│   └── templates                   # HTML templates
│       ├── base.html               # Base template with common elements
│       ├── index.html              # Upload form page
│       └── result.html             # Results display page
│
├── tests                           # Test suite
│   ├── __init__.py
│   └── test_fingering.py           # Tests for fingering algorithm
│
├── requirements.txt                # Project dependencies
├── Procfile                        # Heroku deployment configuration
├── config.py                       # Application configuration
├── run.py                          # Application entry point
└── README.md                       # Project documentation
```

## Setup Instructions

1. **Clone the repository:**
   ```
   git clone https://github.com/OclefInc/piano-fingering-web.git
   cd piano-fingering-web
   ```

2. **Create a virtual environment:**
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install dependencies:**
   ```
   pip install -r requirements.txt
   ```

4. **Run the application:**
   ```
   python run.py
   ```

5. **Access the application:**
   Open your web browser and go to `http://127.0.0.1:5000`.

## Usage

- On the main page, users can upload a musical file and select a hand size for fingering processing.
- After submission, the application processes the file and displays the results on a new page.

## Contributing

Contributions are welcome! Please submit a pull request or open an issue for any suggestions or improvements.