"""
Gmail Tools — Connects using standard SMTP and IMAP with user credentials.
"""
import smtplib
import imaplib
import email
from email.mime.text import MIMEText
from email.header import decode_header
from database import get_credentials

def read_gmail_inbox(limit: int = 10) -> str:
    """Read recent emails from Gmail inbox using IMAP."""
    creds = get_credentials(None, "gmail")
    if not creds:
        return "Gmail is not configured in Settings."
        
    username = creds.get("username")
    password = creds.get("password")
    
    if not username or not password:
        return "Gmail is missing email or App Password."
        
    try:
        # Connect to Gmail IMAP
        mail = imaplib.IMAP4_SSL("imap.gmail.com", 993, timeout=10)
        mail.login(username, password)
        mail.select("inbox")
        
        status, messages = mail.search(None, "ALL")
        if status != "OK":
            return "Failed to query inbox."
            
        mail_ids = messages[0].split()
        if not mail_ids:
            return "Gmail inbox is empty."
            
        mail_ids = mail_ids[-limit:]
        mail_ids.reverse()
        
        result = []
        for index, m_id in enumerate(mail_ids):
            status, msg_data = mail.fetch(m_id, "(RFC822)")
            if status != "OK":
                continue
                
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])
                    
                    subject, encoding = decode_header(msg["Subject"] or "")[0]
                    if isinstance(subject, bytes):
                        subject = subject.decode(encoding or "utf-8", errors="ignore")
                        
                    from_, encoding = decode_header(msg["From"] or "")[0]
                    if isinstance(from_, bytes):
                        from_ = from_.decode(encoding or "utf-8", errors="ignore")
                        
                    body = ""
                    if msg.is_multipart():
                        for part in msg.walk():
                            content_type = part.get_content_type()
                            content_disposition = str(part.get("Content-Disposition"))
                            if content_type == "text/plain" and "attachment" not in content_disposition:
                                body_bytes = part.get_payload(decode=True)
                                body = body_bytes.decode(errors="ignore") if body_bytes else ""
                                break
                    else:
                        body_bytes = msg.get_payload(decode=True)
                        body = body_bytes.decode(errors="ignore") if body_bytes else ""
                        
                    snippet = body[:120].strip().replace("\n", " ") + ("..." if len(body) > 120 else "")
                    result.append(f"[{index+1}] From: {from_}\nSubject: {subject}\nSnippet: {snippet}\n")
                    
        mail.logout()
        if not result:
            return "No readable emails found."
        return "\n---\n".join(result)
    except Exception as e:
        return f"IMAP Read Error: {str(e)}"

def send_gmail(to: str, subject: str, body: str) -> str:
    """Send an email via Gmail SMTP using credentials configured in Settings."""
    creds = get_credentials(None, "gmail")
    if not creds:
        return "Gmail is not configured in Settings."
        
    username = creds.get("username")
    password = creds.get("password")
    
    if not username or not password:
        return "Gmail is missing email or App Password."
        
    try:
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = username
        msg['To'] = to
        
        server = smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=10)
        server.login(username, password)
        server.sendmail(username, [to], msg.as_string())
        server.quit()
        return f"Successfully sent email to {to}."
    except Exception as e:
        return f"SMTP Send Error: {str(e)}"
