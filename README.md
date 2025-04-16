# Piano Fingering Web Application

This project is a Flask web application that allows users to upload musical files and select a hand size for fingering processing. The application processes the uploaded files and provides results based on the selected hand size.

# Acknowledgments

pianoplayer is a hard fork of Marco Musy [pianoplayer](https://github.com/marcomusy/pianoplayer)


## Project Structure

```
piano-player-web
├── app
│   ├── __init__.py        # Initializes the Flask application
│   ├── routes.py          # Defines the application routes
│   ├── forms.py           # Contains form classes for user input
│   ├── models.py          # Defines data models for database interactions
│   ├── static
│   │   ├── css
│   │   │   └── style.css   # CSS styles for the web application
│   │   └── js
│   │       └── script.js    # JavaScript code for client-side functionality
│   └── templates
│       ├── base.html       # Base HTML template
│       ├── index.html      # Main page for file upload and hand size selection
│       └── result.html     # Displays results after processing
├── config.py               # Configuration settings for the Flask application
├── requirements.txt         # Lists project dependencies
├── run.py                  # Entry point to run the Flask application
└── README.md               # Documentation for the project
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