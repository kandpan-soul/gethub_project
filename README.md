# Holy Spirit Flask Web Application

This project is a Flask web application focused on the Holy Spirit, featuring:
- Homepage with explanation and verses
- Scripture explorer for verses mentioning the Holy Spirit
- Daily devotion page with verse, reflection, and journal input
- Fruits of the Spirit tracker (Galatians 5:22-23)
- Prayer request system and prayer wall
- Testimony sharing board
- User authentication (login, signup, dashboard)
- Bootstrap for styling
- SQLite for the database

## Getting Started

1. Create and activate the virtual environment:
   ```powershell
   python -m venv .venv
   .venv\Scripts\activate
   ```
2. Install dependencies:
   ```powershell
   pip install flask flask_sqlalchemy flask_login
   ```
3. Run the application:
   ```powershell
   flask run
   ```

## Project Structure
- `app.py`: Main Flask application
- `templates/`: HTML templates
- `static/`: Static files (CSS, JS)
- `.github/copilot-instructions.md`: Copilot instructions

## Notes
- Ensure you have Python 3.8+ installed.
- For development, use the provided VS Code tasks.
