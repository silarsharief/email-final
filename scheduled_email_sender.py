import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from datetime import datetime
import os
from dotenv import load_dotenv
import sys
import traceback
import threading
import tkinter as tk
from tkinter import ttk

# Add the parent directory to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

# Import render_email functions
from render_email import get_market_data, get_index_change, get_nifty_movers, get_news_for_tickers, summarize_news

# Global Tkinter root window
root = None

def init_tkinter():
    global root
    if root is None:
        root = tk.Tk()
        root.withdraw()  # Hide the window
    return root

def cleanup_tkinter():
    global root
    if root is not None:
        root.quit()
        root.destroy()
        root = None

def send_email():
    try:
        # Initialize Tkinter
        init_tkinter()
        
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
    finally:
        # Cleanup Tkinter
        cleanup_tkinter()

def generate_and_send():
    try:
        print("Starting email generation process...")
        
        # Initialize Tkinter
        init_tkinter()
        
        # Generate market data and graphs
        print("Generating market data...")
        get_market_data()
        
        # Get market changes
        print("Fetching market changes...")
        nifty_change = get_index_change("^NSEI", "Nifty 50")
        sensex_change = get_index_change("^BSESN", "Sensex")
        
        # Get movers
        print("Getting market movers...")
        gainers, losers = get_nifty_movers()
        
        # Get news
        print("Fetching news...")
        all_tickers = [f"{symbol}.NS" for symbol in gainers.keys()] + [f"{symbol}.NS" for symbol in losers.keys()]
        news_for_tickers = get_news_for_tickers(all_tickers)
        news_summary = summarize_news(news_for_tickers)
        
        # Send email
        print("Sending email...")
        send_email()
        
        print("Email process completed successfully!")
        return True
    except Exception as e:
        print(f"Error in generate_and_send: {str(e)}")
        print(traceback.format_exc())
        return False
    finally:
        # Cleanup Tkinter
        cleanup_tkinter()

if __name__ == '__main__':
    try:
        print(f"Starting email generation at {datetime.now()}")
        generate_and_send()
        print("Process completed")
    finally:
        # Ensure Tkinter is cleaned up even if there's an error
        cleanup_tkinter() 