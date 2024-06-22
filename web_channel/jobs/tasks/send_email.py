import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders


def send_email_with_multiple_attachments(recipient_email, path):
    # Email server settings
    smtp_host = 'mail.privateemail.com'  # Replace with your SMTP server address
    smtp_port = 587  # This is the typical port for SMTP submission

    # Email account credentials
    sender_email = 'support@taxbotke.com'  # Replace with your email address
    password = 'TaxB0tK3SupP0rT'  # Replace with your email account password

    # Email content
    subject = "Your tax has been filed successfully!!!."
    body = 'Thanks_for_filing your taxes with TaxbotKE. Attached is a picture evidence of filing.'

    # Create MIME object
    message = MIMEMultipart()
    message['From'] = sender_email
    message['To'] = recipient_email
    message['Subject'] = subject

    # Attach body to the email
    message.attach(MIMEText(body, 'plain'))

    # Attach files
    attachment = open(path, 'rb')
    part = MIMEBase('application', 'octet-stream')
    part.set_payload(attachment.read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', f'attachment; filename=screenshot.png')
    message.attach(part)

    # Connect to SMTP server
    try:
        smtp_server = smtplib.SMTP(smtp_host, smtp_port)
        smtp_server.starttls()  # Secure the connection
        smtp_server.login(sender_email, password)

        # Send email
        smtp_server.sendmail(sender_email, recipient_email, message.as_string())
        print('Email with multiple attachments sent successfully!')

    except Exception as e:
        print(f'Error sending email: {e}')

    finally:
        smtp_server.quit()
