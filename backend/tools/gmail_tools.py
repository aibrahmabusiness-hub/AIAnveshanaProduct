"""
Gmail Tools — Connects using standard SMTP and IMAP with user credentials.
"""
import smtplib
import imaplib
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import decode_header
from database import get_credentials
import datetime

def read_gmail_inbox(folder: str = "inbox", status_filter: str = "ALL", sender_email: str = "", days_ago: str = "", limit = 10) -> list:
    """Read recent emails from a specific Gmail folder with advanced filters."""
    try:
        limit = int(limit)
    except (ValueError, TypeError):
        limit = 10
        
    creds = get_credentials(None, "gmail")
    if not creds:
        return [{"error": "Gmail is not configured in Settings."}]
        
    username = creds.get("username")
    password = creds.get("password")
    
    if not username or not password:
        return [{"error": "Gmail is missing email or App Password."}]
        
    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com", 993, timeout=10)
        mail.login(username, password)
        mail.select(f'"{folder}"')
        
        criteria = [status_filter] if status_filter in ["ALL", "UNSEEN", "SEEN"] else ["ALL"]
        if sender_email:
            criteria.append(f'FROM "{sender_email}"')
        
        if days_ago:
            try:
                days = int(days_ago)
                date_since = (datetime.datetime.now() - datetime.timedelta(days=days)).strftime("%d-%b-%Y")
                criteria.append(f'SINCE "{date_since}"')
            except ValueError:
                pass
                
        search_query = f"({' '.join(criteria)})" if len(criteria) > 1 else criteria[0]
        
        status, messages = mail.search(None, search_query)
        if status != "OK":
            return [{"error": f"Failed to query {folder} with criteria {search_query}."}]
            
        mail_ids = messages[0].split()
        if not mail_ids:
            return []
            
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
                        
                    msg_subject = subject or "No Subject"
                    snippet = ""
                    
                    if msg.is_multipart():
                        for part in msg.walk():
                            if part.get_content_type() == "text/plain":
                                body_bytes = part.get_payload(decode=True)
                                if body_bytes:
                                    snippet = body_bytes.decode(errors="ignore")[:250].replace("\n", " ") + "..."
                                break
                    else:
                        body_bytes = msg.get_payload(decode=True)
                        if body_bytes:
                            snippet = body_bytes.decode(errors="ignore")[:250].replace("\n", " ") + "..."
                            
                    result.append({
                        "id": m_id.decode('utf-8'),
                        "from": from_,
                        "subject": msg_subject,
                        "snippet": snippet
                    })
                    
        mail.logout()
        return result
    except Exception as e:
        return [{"error": f"IMAP Search Error: {str(e)}"}]

def mark_gmail_read(message_id: str, folder: str = "inbox") -> str:
    """Mark a specific email ID as read."""
    if not message_id:
        return "Error: Missing message_id parameter."
        
    creds = get_credentials(None, "gmail")
    if not creds:
        return "Gmail is not configured in Settings."
        
    username = creds.get("username")
    password = creds.get("password")
    
    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com", 993, timeout=10)
        mail.login(username, password)
        mail.select(f'"{folder}"')
        
        status, _ = mail.store(message_id, '+FLAGS', '\\Seen')
        mail.logout()
        
        if status == "OK":
            return f"Successfully marked message {message_id} as Read."
        return f"Failed to mark message {message_id} as Read."
    except Exception as e:
        return f"IMAP Mark Read Error: {str(e)}"

def send_gmail(
    to: list, subject: str, body: str, cc: list = None, bcc: list = None,
    body_type: str = "plain_text", reply_to: list = None, sender_name: str = None,
    from_email: str = None
) -> str:
    """Send an email via Gmail SMTP using credentials configured in Settings."""
    creds = get_credentials(None, "gmail")
    if not creds:
        return "Gmail is not configured in Settings."
        
    username = creds.get("username")
    password = creds.get("password")
    
    if not username or not password:
        return "Gmail is missing email or App Password."
        
    try:
        if isinstance(to, str): to = [to]
        if isinstance(cc, str): cc = [cc]
        if isinstance(bcc, str): bcc = [bcc]
        if isinstance(reply_to, str): reply_to = [reply_to]
        
        msg = MIMEMultipart()
        msg['Subject'] = subject
        
        sender = from_email if from_email else username
        if sender_name:
            msg['From'] = f"{sender_name} <{sender}>"
        else:
            msg['From'] = sender
            
        msg['To'] = ", ".join(to) if to else ""
        
        all_recipients = to[:] if to else []
        if cc:
            msg['Cc'] = ", ".join(cc)
            all_recipients.extend(cc)
        if bcc:
            all_recipients.extend(bcc)
            
        if reply_to:
            msg['Reply-To'] = ", ".join(reply_to)
            
        mime_type = 'html' if body_type == 'html' else 'plain'
        msg.attach(MIMEText(body, mime_type))
        
        server = smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=10)
        server.login(username, password)
        server.sendmail(username, all_recipients, msg.as_string())
        server.quit()
        return f"Successfully sent email to {', '.join(to)}."
    except Exception as e:
        return f"SMTP Send Error: {str(e)}"

def search_gmail_inbox(
    from_email=None, to_email=None, subject=None, content=None,
    has_attachment=False, attachment_name=None, label=None,
    category=None, after_date=None, before_date=None,
    include_spam_trash=False, limit=10, query=None
) -> list:
    """Search Gmail using structured properties or a generic IMAP query string."""
    try:
        limit = int(limit)
    except (ValueError, TypeError):
        limit = 10
        
    query_parts = []
    if from_email: query_parts.append(f"FROM \"{from_email}\"")
    if to_email: query_parts.append(f"TO \"{to_email}\"")
    if subject: query_parts.append(f"SUBJECT \"{subject}\"")
    if content: query_parts.append(f"BODY \"{content}\"")
    # Note: IMAP standard search does not easily support has:attachment natively in all servers, 
    # but since this is Gmail, we can use the X-GM-RAW extension.
    # To support all these advanced gmail features efficiently, we should use X-GM-RAW!
    
    gm_raw_parts = []
    if from_email: gm_raw_parts.append(f"from:({from_email})")
    if to_email: gm_raw_parts.append(f"to:({to_email})")
    if subject: gm_raw_parts.append(f"subject:({subject})")
    if content: gm_raw_parts.append(f'"{content}"')
    if has_attachment: gm_raw_parts.append("has:attachment")
    if attachment_name: gm_raw_parts.append(f"filename:({attachment_name})")
    if label: gm_raw_parts.append(f"label:{label}")
    if category: gm_raw_parts.append(f"category:{category}")
    if after_date: gm_raw_parts.append(f"after:{after_date}")
    if before_date: gm_raw_parts.append(f"before:{before_date}")
    if include_spam_trash: gm_raw_parts.append("in:anywhere")
    
    if query:
        # manual override
        gm_raw_parts.append(query)
        
    final_query = "ALL"
    if gm_raw_parts:
        # Use Gmail's specific search syntax which is immensely powerful
        raw_query = " ".join(gm_raw_parts)
        final_query = f'X-GM-RAW "{raw_query}"'
        
    creds = get_credentials(None, "gmail")
    if not creds:
        return "Gmail is not configured in Settings."
        
    username = creds.get("username")
    password = creds.get("password")
    
    if not username or not password:
        return "Gmail is missing email or App Password."
        
    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com", 993, timeout=10)
        mail.login(username, password)
        # Select All Mail to ensure we can search everywhere if needed
        mail.select('"[Gmail]/All Mail"' if include_spam_trash else '"inbox"')
        
        status, messages = mail.search(None, final_query)
        if status != "OK":
            return [{"error": f"Failed to execute search with query: {final_query}."}]
            
        mail_ids = messages[0].split()
        if not mail_ids:
            return []
            
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
                    
                    msg_subject, encoding = decode_header(msg["Subject"] or "")[0]
                    if isinstance(msg_subject, bytes):
                        msg_subject = msg_subject.decode(encoding or "utf-8", errors="ignore")
                        
                    from_, encoding = decode_header(msg["From"] or "")[0]
                    if isinstance(from_, bytes):
                        from_ = from_.decode(encoding or "utf-8", errors="ignore")
                        
                    snippet = "(body preview unavailable)"
                    if msg.is_multipart():
                        for part in msg.walk():
                            if part.get_content_type() == "text/plain":
                                body_bytes = part.get_payload(decode=True)
                                if body_bytes:
                                    snippet = body_bytes.decode(errors="ignore")[:250].replace("\n", " ") + "..."
                                break
                    else:
                        body_bytes = msg.get_payload(decode=True)
                        if body_bytes:
                            snippet = body_bytes.decode(errors="ignore")[:250].replace("\n", " ") + "..."
                            
                    result.append({
                        "id": m_id.decode('utf-8'),
                        "from": from_,
                        "subject": msg_subject,
                        "snippet": snippet
                    })
                    
        mail.logout()
        return result
    except Exception as e:
        return [{"error": f"IMAP Search Error: {str(e)}"}]
