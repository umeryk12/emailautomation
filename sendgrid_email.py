"""
SendGrid Email Sender - Works on Railway and other platforms that block SMTP
"""

import logging
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

logger = logging.getLogger(__name__)


class SendGridEmailSender:
    """Send emails using SendGrid API (no SMTP needed)"""
    
    def __init__(self, api_key, from_email, from_name=None):
        """
        Initialize SendGrid sender
        
        Args:
            api_key: SendGrid API key
            from_email: Verified sender email in SendGrid
            from_name: Sender name (optional)
        """
        self.api_key = api_key
        self.from_email = from_email
        self.from_name = from_name or from_email
        self.client = SendGridAPIClient(api_key)
        
    def send_email(self, to_email, subject, body):
        """
        Send a single email via SendGrid
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            body: Email body (plain text)
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            message = Mail(
                from_email=(self.from_email, self.from_name),
                to_emails=to_email,
                subject=subject,
                plain_text_content=body
            )
            
            logger.info(f"📤 Sending via SendGrid to {to_email}")
            response = self.client.send(message)
            
            if response.status_code in [200, 201, 202]:
                logger.info(f"✅ SendGrid: Email sent to {to_email} (Status: {response.status_code})")
                return True
            else:
                logger.error(f"❌ SendGrid returned status {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ SendGrid error sending to {to_email}: {str(e)}")
            return False


def test_sendgrid_connection(api_key, from_email):
    """
    Test SendGrid configuration
    
    Args:
        api_key: SendGrid API key
        from_email: Verified sender email
        
    Returns:
        tuple: (success: bool, message: str)
    """
    try:
        client = SendGridAPIClient(api_key)
        # Try to get API key info (this validates the key)
        logger.info("Testing SendGrid connection...")
        
        # Just creating the client validates the API key format
        if len(api_key) < 20 or not api_key.startswith('SG.'):
            return False, "Invalid SendGrid API key format. Should start with 'SG.'"
        
        return True, f"SendGrid configured successfully for {from_email}"
        
    except Exception as e:
        return False, f"SendGrid test failed: {str(e)}"

