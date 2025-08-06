 # First-Aid AI Assistant

A web-based AI assistant that provides first aid advice and guidance using Google's Generative AI.

## Setup

1. Create a virtual environment and activate it:
```bash
python3 -m venv venv
source venv/bin/activate
```

2. Install the required packages:
```bash
pip install -r requirements.txt
```

3. Set up your environment variables:
   - Copy the contents of `.env` to a new file called `.env`
   - Replace `YOUR_API_KEY_HERE` with your Google AI Studio API key

## Running the Application

1. Activate the virtual environment (if not already activated):
```bash
source venv/bin/activate
```

2. Run the Flask application:
```bash
python app.py
```

3. Open your browser and navigate to `http://localhost:5001`

## Project Structure

```
/first-aid-assistant
|-- /static
|   |-- /css
|   |   `-- style.css      # Main stylesheet
|   |-- /js
|   |   `-- script.js      # Client-side JavaScript
|   |-- /images            # Directory for images (if needed)
|-- /templates
|   `-- index.html         # Main HTML template
|-- app.py                 # Flask application
|-- requirements.txt       # Python dependencies
|-- .env                   # Environment variables
```

## Features

- Interactive chat interface
- Real-time responses using Google's Generative AI
- Mobile-responsive design
- Simple and intuitive user interface

## Security Note

Never commit your `.env` file with real API keys to version control. The `.env` file in this repository contains only a placeholder value.
