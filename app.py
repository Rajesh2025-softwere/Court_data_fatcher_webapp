import os
import json
import random
import time
from datetime import datetime, date

# Flask and SQLAlchemy imports
from flask import Flask, render_template, request, jsonify, send_file
from sqlalchemy.exc import SQLAlchemyError

# Database utility from local file
from database import db, CaseQueryLog

# --- Flask App Initialization ---
app = Flask(__name__)

# Configure SQLAlchemy (using SQLite for simplicity and portability)
# NOTE: Replace 'sqlite:///site.db' with your Postgres connection string for production.
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'a_very_secret_key_for_session_management'

# Initialize the database with the Flask app
db.init_app(app)

# --- Mock Data and Utilities ---

# Mock data mimicking eCourts responses for demonstration
MOCK_CASE_DATA = {
    # Success Case 1: Active case
    'HMA/133/2025': {
        'caseType': 'Hindu Marriage Act',
        'parties': {'petitioner': 'Ramesh Kumar', 'respondent': 'Sapna Devi'},
        'filingDate': '07-07-2025',
        'nextHearingDate': date.today().strftime('%d-%m-%Y'), # Listed today
        'caseStatus': 'Pending',
        'court': 'District and Sessions Judge, Chamba',
        'judge': 'Sh. J.S. Thakur',
        'causeListToday': True,
        'orders': [{'date': '22-07-2025', 'details': 'Notice issued to Respondent.', 'url': 'order_1.pdf'}],
    },
    # Success Case 2: Disposed case
    'CS/99/2024': {
        'caseType': 'Civil Suit',
        'parties': {'petitioner': 'Ganesh Builders', 'respondent': 'MC Shimla'},
        'filingDate': '10-01-2024',
        'nextHearingDate': 'N/A',
        'caseStatus': 'Disposed',
        'court': 'Civil Judge Sr. Div., Shimla',
        'judge': 'Ms. A. Sharma',
        'causeListToday': False,
        'orders': [{'date': '05-12-2024', 'details': 'Final Judgment passed.', 'url': 'judgment_final.pdf'}],
    },
}

# Generate a random 4-char CAPTCHA
def generate_captcha():
    """Generates a random alphanumeric CAPTCHA."""
    chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    return ''.join(random.choice(chars) for _ in range(4))

# --- Core Scraper Simulation Function ---

def scrape_case_data(case_key: str):
    """
    Simulates the scraping of eCourts data.

    In a real application, this function would handle:
    1. HTTP session initialization (using requests.Session).
    2. Fetching the initial page to get cookies/state information.
    3. Sending the search query (Case Type/Number/Year).
    4. Solving the CAPTCHA (requires external service or local model).
    5. Parsing the results using BeautifulSoup or similar library.
    6. Extracting specific fields (parties, dates, status, orders).
    """
    app.logger.info(f"Simulating scrape for key: {case_key}")
    
    # Simulate network delay
    time.sleep(random.uniform(1.0, 2.5))
    
    if case_key in MOCK_CASE_DATA:
        # Success scenario
        data = MOCK_CASE_DATA[case_key]
        return {
            'status': 'success',
            'data': data,
            'raw_response': json.dumps(data)
        }
    else:
        # Failure scenario: Case Not Found / Invalid Input
        error_msg = f"Case {case_key} not found on the portal or invalid input format."
        return {
            'status': 'error',
            'message': error_msg,
            'raw_response': f"ERROR: {error_msg}"
        }

# --- Database Storage Function ---

def log_query(case_type, case_number, year, status, raw_response):
    """Stores the query details and raw response in the database."""
    try:
        new_log = CaseQueryLog(
            case_type=case_type,
            case_number=case_number,
            filing_year=year,
            status=status,
            raw_response=raw_response[:1000] # Truncate large responses
        )
        db.session.add(new_log)
        db.session.commit()
        app.logger.info(f"Query logged successfully: {case_type} {case_number}/{year}")
    except SQLAlchemyError as e:
        db.session.rollback()
        app.logger.error(f"Database Error: Failed to log query: {e}")

# --- Flask Routes ---

@app.route('/', methods=['GET'])
def index():
    """Renders the main application interface."""
    return render_template('index.html')

@app.route('/api/search_case', methods=['POST'])
def search_case():
    """API endpoint to handle the case search request."""
    data = request.json
    case_type = data.get('caseType')
    case_number = data.get('caseNumber')
    year = data.get('year')
    captcha_solution = data.get('captchaSolution')
    generated_captcha = data.get('generatedCaptcha')

    if not all([case_type, case_number, year, captcha_solution, generated_captcha]):
        return jsonify({'status': 'error', 'message': 'Missing required search parameters.'}), 400

    # 1. CAPTCHA Validation
    if captcha_solution.upper() != generated_captcha.upper():
        log_query(case_type, case_number, year, 'Failed (CAPTCHA)', 'CAPTCHA mismatch')
        return jsonify({'status': 'error', 'message': 'Invalid CAPTCHA solution. Please try again.'})

    # 2. Case Search Simulation
    case_key = f"{case_type}/{case_number}/{year}"
    result = scrape_case_data(case_key)
    
    # 3. Log the query result
    log_query(case_type, case_number, year, result['status'], result['raw_response'])

    # 4. Return results to the frontend
    if result['status'] == 'success':
        return jsonify({'status': 'success', 'data': result['data']})
    else:
        return jsonify({'status': 'error', 'message': result['message']})

@app.route('/api/generate_captcha', methods=['GET'])
def generate_new_captcha():
    """API endpoint to get a new CAPTCHA image/text."""
    # In a real app, this would fetch the CAPTCHA image and return its text/ID
    captcha = generate_captcha()
    return jsonify({'status': 'success', 'captcha': captcha})

@app.route('/api/download/<filename>', methods=['GET'])
def download_file(filename):
    """
    Simulates downloading a judgment or cause list.

    NOTE: In a real scraper, you would use requests to download the PDF
    from the eCourts server and return that file.
    """
    if 'order' in filename or 'judgment' in filename:
        content = f"--- MOCK JUDGMENT/ORDER for {filename} ---\n\n"
        content += "This is a simulated PDF content based on the request URL. "
        content += "The original file would be a PDF downloaded from the eCourts portal."
        mime_type = 'text/plain' # Change to 'application/pdf' for real PDFs
    elif 'causelist' in filename:
        content = f"--- MOCK CAUSE LIST for {date.today().strftime('%d-%m-%Y')} ---\n\n"
        content += "1. Case HMA/133/2025: Ramesh Kumar vs. Sapna Devi (For Hearing)\n"
        content += "2. Case XYZ/12/2024: (New Filing)\n"
        mime_type = 'text/plain'
    else:
        return jsonify({'status': 'error', 'message': 'File not found'}), 404

    # Create a temporary file to serve the content
    temp_path = os.path.join('/tmp', filename)
    with open(temp_path, 'w') as f:
        f.write(content)

    return send_file(temp_path, as_attachment=True, download_name=filename.replace('.pdf', '.txt'), mimetype=mime_type)

@app.route('/api/logs', methods=['GET'])
def get_logs():
    """API endpoint to fetch recent query logs for the admin/status dashboard."""
    logs = CaseQueryLog.query.order_by(CaseQueryLog.timestamp.desc()).limit(10).all()
    
    logs_data = []
    for log in logs:
        logs_data.append({
            'timestamp': log.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'case_type': log.case_type,
            'case_number': log.case_number,
            'filing_year': log.filing_year,
            'status': log.status,
            'raw_response_snippet': log.raw_response[:50] + '...'
        })
    return jsonify(logs_data)


# --- Application Setup ---

# Create database tables upon first run
@app.before_request
def create_tables():
    """Creates all database tables defined in the models."""
    db.create_all()

if __name__ == '__main__':
    # Ensure tables are created before running
    with app.app_context():
        create_tables()
    app.run(debug=True)