import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from datetime import datetime
import os
from dotenv import load_dotenv
from flask import Flask, jsonify, request, send_from_directory
import sys
import traceback
from waitress import serve

# Add the parent directory to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

# Import render_email functions
from render_email import get_market_data, get_index_change, get_nifty_movers, get_news_for_tickers, summarize_news

app = Flask(__name__)

def send_email():
    try:
        # Load environment variables
        load_dotenv()

        # --- CONFIGURATION ---
        sender_email = os.getenv('EMAIL_ADDRESS')
        sender_password = os.getenv('EMAIL_PASSWORD')
        recipient_emails = os.getenv('RECIPIENT_EMAILS', '').split(',')

        if not all([sender_email, sender_password, recipient_emails]):
            raise ValueError("Missing required environment variables: EMAIL_ADDRESS, EMAIL_PASSWORD, or RECIPIENT_EMAILS")

        # Get current date in the format "Month DD, YYYY"
        current_date = datetime.now().strftime("%B %d, %Y")
        subject = f"Tw Market Digest on {current_date}"

        # Get the directory where the script is located
        script_dir = os.path.dirname(os.path.abspath(__file__))

        # Read your rendered HTML
        html_path = os.path.join(script_dir, "rendered_email.html")
        if not os.path.exists(html_path):
            raise FileNotFoundError(f"Email template not found at {html_path}")

        with open(html_path, "r", encoding="utf-8") as f:
            html_content = f.read()

        # Replace the image src in HTML to use CID for both the graph and the logo
        html_content = html_content.replace('src="nifty50_graph.png"', 'src="cid:nifty50graph"')
        html_content = html_content.replace('src="Truwealth logo--full--white.png"', 'src="cid:clublogo"')

        # --- SEND EMAIL ---
        for recipient_email in recipient_emails:
            # Create the email for each recipient
            msg = MIMEMultipart("related")
            msg["Subject"] = subject
            msg["From"] = sender_email
            msg["To"] = recipient_email

            # Attach the HTML
            msg_alt = MIMEMultipart("alternative")
            msg.attach(msg_alt)
            msg_alt.attach(MIMEText(html_content, "html"))

            # Attach the image
            nifty_path = os.path.join(script_dir, "nifty50_graph.png")
            if os.path.exists(nifty_path):
                with open(nifty_path, "rb") as img:
                    mime_img = MIMEImage(img.read())
                    mime_img.add_header('Content-ID', '<nifty50graph>')
                    mime_img.add_header('Content-Disposition', 'inline', filename="nifty50_graph.png")
                    msg.attach(mime_img)

            # Attach the logo image
            logo_path = os.path.join(script_dir, "Truwealth logo--full--white.png")
            if os.path.exists(logo_path):
                with open(logo_path, "rb") as logo_img:
                    mime_logo = MIMEImage(logo_img.read())
                    mime_logo.add_header('Content-ID', '<clublogo>')
                    mime_logo.add_header('Content-Disposition', 'inline', filename="Truwealth logo--full--white.png")
                    msg.attach(mime_logo)

            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                server.login(sender_email, sender_password)
                server.sendmail(sender_email, recipient_email, msg.as_string())
            print(f"Email sent to {recipient_email}!")
        
        return True
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        raise

@app.route('/generate-and-send', methods=['POST'])
def generate_and_send():
    try:
        # Generate market data and graphs
        get_market_data()
        
        # Get market changes
        nifty_change = get_index_change("^NSEI", "Nifty 50")
        sensex_change = get_index_change("^BSESN", "Sensex")
        
        # Get movers
        gainers, losers = get_nifty_movers()
        
        # Get news
        all_tickers = [f"{symbol}.NS" for symbol in gainers.keys()] + [f"{symbol}.NS" for symbol in losers.keys()]
        news_for_tickers = get_news_for_tickers(all_tickers)
        news_summary = summarize_news(news_for_tickers)
        
        # Send email
        send_email()
        
        return jsonify({
            'status': 'success',
            'message': 'Email generated and sent successfully',
            'data': {
                'nifty_change': nifty_change,
                'sensex_change': sensex_change,
                'gainers': gainers,
                'losers': losers
            }
        })
    except Exception as e:
        error_traceback = traceback.format_exc()
        return jsonify({
            'status': 'error',
            'message': str(e),
            'traceback': error_traceback
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/')
def home():
    return '''
    <html>
        <head>
            <title>Email Bot API</title>
            <style>
                body { font-family: Arial, sans-serif; max-width: 800px; margin: 40px auto; padding: 20px; }
                .endpoint { background: #f5f5f5; padding: 15px; margin: 10px 0; border-radius: 5px; }
                code { background: #e0e0e0; padding: 2px 5px; border-radius: 3px; }
            </style>
        </head>
        <body>
            <h1>Email Bot API</h1>
            <p>Available endpoints:</p>
            <div class="endpoint">
                <h3>GET /health</h3>
                <p>Health check endpoint</p>
                <code>curl http://localhost:5000/health</code>
            </div>
            <div class="endpoint">
                <h3>POST /generate-and-send</h3>
                <p>Generate and send market digest email</p>
                <code>curl -X POST http://localhost:5000/generate-and-send</code>
            </div>
        </body>
    </html>
    '''

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.dirname(os.path.abspath(__file__)), 'twlogo.png', mimetype='image/png')

if __name__ == '__main__':
    if os.getenv('FLASK_ENV') == 'development':
        # Development server
        app.run(host='0.0.0.0', port=5000, debug=True)
    else:
        # Production server
        print("Starting production server on http://0.0.0.0:5000")
        serve(app, host='0.0.0.0', port=5000, threads=4)