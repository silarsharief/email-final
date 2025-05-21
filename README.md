# Truwealth Market Digest Email Bot

This email bot system automatically generates and sends daily market digest emails with market updates, stock information, and news.

## Features

- Daily market updates (Nifty 50 and Sensex)
- Market performance charts
- Pre-IPO stock watchlist
- Top gainers and losers
- Trending market news
- Interactive buttons for various services

## Prerequisites

- Python 3.x
- Required Python packages (install using `pip install -r requirements.txt`):
  - yagmail
  - jinja2
  - pandas
  - numpy
  - matplotlib
  - requests
  - beautifulsoup4

## Setup

1. Clone the repository
2. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```
3. Configure email settings in `send_sample_email.py`:
   - Update sender email and password
   - Update recipient email list

## Files Description

- `test.html`: Email template with placeholders for dynamic content
- `render_email.py`: Generates the email content with market data
- `send_sample_email.py`: Sends the generated email
- `scheduled_email_sender.py`: Script for scheduled email sending
- `run_email_sender.bat`: Windows batch file to run the email sender
- `Truwealth logo--full--white.png`: Logo used in the email
- `nifty50_graph.png`: Generated Nifty 50 chart
- `sensex_graph.png`: Generated Sensex chart

## Project Flow

1. **Data Collection and Processing** (`render_email.py`):
   - Fetches market data (Nifty 50, Sensex)
   - Generates market performance charts
   - Collects Pre-IPO stock information
   - Gathers top gainers and losers
   - Fetches trending market news

2. **Email Generation** (`render_email.py`):
   - Uses Jinja2 template engine with `test.html`
   - Fills in dynamic content:
     - Market indices and changes
     - Generated charts
     - Pre-IPO stock list
     - Gainers and losers
     - Market news
   - Creates a complete HTML email

3. **Email Sending** (`send_sample_email.py`):
   - Configures email settings
   - Attaches required images (logo, charts)
   - Sends email to recipient list
   - Handles email delivery status

4. **Scheduling** (`scheduled_email_sender.py`):
   - Runs the email generation and sending process
   - Can be scheduled to run daily
   - Handles errors and retries
   - Logs execution status

5. **Automation** (`run_email_sender.bat`):
   - Windows batch file for easy execution
   - Can be scheduled using Windows Task Scheduler
   - Runs the scheduled email sender script

## Usage

### Manual Email Sending

1. Run the email sender script:
   ```bash
   python send_sample_email.py
   ```

### Scheduled Email Sending

1. Use the batch file to run the scheduled sender:
   ```bash
   run_email_sender.bat
   ```

### Customizing the Email

1. Modify `test.html` to change the email template
2. Update `render_email.py` to modify the data generation logic
3. Adjust email settings in `send_sample_email.py`

## Email Content

The email includes:
- Market overview (Nifty 50 and Sensex)
- Daily market performance chart
- Pre-IPO stock watchlist
- Top gainers and losers
- Trending market news
- Interactive buttons for:
  - Joining the club
  - Investing in Pre-IPO stocks
  - Free MF Portfolio Review

## Notes

- The system uses yagmail for sending emails
- Market data is fetched and processed automatically
- Charts are generated using matplotlib
- The email template is responsive and mobile-friendly

## Support

For any issues or questions, please contact the development team.

## License

This project is proprietary and confidential. Unauthorized copying, distribution, or use is strictly prohibited.
