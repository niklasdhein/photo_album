# Photo Album Web App

This is a photo album application where you can upload your favourite images into albums and invite other users to these albums. You can upload and manage these together, also by tagging and grouping images.

---

## Architecture

- **Frontend**: React (SPA with `react-router-dom`) – runs on `http://localhost:3000`
- **Backend**: Python Flask REST API (`backend/api.py`) – runs on `http://localhost:5000`
- **Database**: SQLite (`backend/app.db`)

---

## Quick Start Guide

To run the application, you need **two terminal windows** (one for the backend, one for the frontend).

### 1. Start Backend (Python / Flask)

In your first terminal, navigate to the `backend/` directory:

```bash
cd backend
```

Create and activate a Python virtual environment:

```bash
# Linux / macOS
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

Install the required Python packages:

```bash
pip install -r requirements.txt
```

Initialize the SQLite database (only needed the first time or to reset):

```bash
python3 create_database.py
```

Start the Flask server:

```bash
python3 api.py
```

The backend server is now running on **`http://localhost:5000`**.

---

### 2. Start Frontend (React / Node.js)

In your second terminal, navigate to the project root directory:

```bash
cd photo_album
```

Install the Node dependencies (only needed the first time):

```bash
npm install
```

Start the React development server:

```bash
npm start
```

The application will open in your browser at **`http://localhost:3000`**.

Note that this project exists only for learning the fundamentals of web applications and simple API calls and therefore is yet unfinished and will probably remain so. Because of that there is no guarantee it will run on your system, feel free to try out and experiment with it anyway.
