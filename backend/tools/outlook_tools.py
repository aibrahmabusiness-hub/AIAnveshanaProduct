"""
Outlook Tools — Windows-only Outlook COM integration.
Gracefully degrades on non-Windows platforms.
"""
from datetime import datetime, timedelta

try:
    import win32com.client
    OUTLOOK_AVAILABLE = True
except ImportError:
    OUTLOOK_AVAILABLE = False

def get_outlook_app():
    """Initializes and returns the Outlook application object."""
    if not OUTLOOK_AVAILABLE:
        return None
    try:
        return win32com.client.Dispatch("Outlook.Application")
    except Exception as e:
        print(f"Error initializing Outlook: {e}")
        return None

def schedule_meeting(subject: str, attendees: str, start_time: str, duration_minutes: int = 30) -> str:
    """
    Schedules a meeting in Outlook.
    
    Args:
        subject (str): The subject of the meeting.
        attendees (str): Semicolon-separated list of email addresses.
        start_time (str): Start time in ISO format (e.g., '2026-06-02T14:00:00').
        duration_minutes (int): Duration of the meeting in minutes.
    """
    if not OUTLOOK_AVAILABLE:
        return "Outlook integration is not available on this platform. It requires a Windows machine with Microsoft Outlook installed."
    try:
        outlook = get_outlook_app()
        if not outlook:
            return "Failed to connect to Outlook."
        
        appt = outlook.CreateItem(1) # 1 = olAppointmentItem
        appt.Subject = subject
        appt.RequiredAttendees = attendees
        
        start_dt = datetime.fromisoformat(start_time)
        appt.Start = start_dt.strftime("%Y-%m-%d %H:%M:%S")
        appt.Duration = duration_minutes
        
        appt.MeetingStatus = 1 # 1 = olMeeting
        appt.Save()
        appt.Send()
        
        return f"Meeting '{subject}' scheduled successfully for {start_time}."
    except Exception as e:
        return f"Error scheduling meeting: {str(e)}"

def get_important_emails(limit: int = 5) -> str:
    """
    Retrieves recent unread or important emails from the Outlook inbox.
    
    Args:
        limit (int): Maximum number of emails to retrieve.
    """
    if not OUTLOOK_AVAILABLE:
        return "Outlook integration is not available on this platform. It requires a Windows machine with Microsoft Outlook installed."
    try:
        outlook = get_outlook_app()
        if not outlook:
            return "Failed to connect to Outlook."
        
        namespace = outlook.GetNamespace("MAPI")
        inbox = namespace.GetDefaultFolder(6) # 6 = olFolderInbox
        
        messages = inbox.Items
        messages.Sort("[ReceivedTime]", True)
        
        # Filter for unread (just as an example of 'important')
        messages = messages.Restrict("[Unread] = True")
        
        results = []
        count = 0
        for msg in messages:
            if count >= limit:
                break
            try:
                sender = msg.SenderEmailAddress
                subject = msg.Subject
                received_time = msg.ReceivedTime
                results.append(f"- From: {sender} | Subject: {subject} | Received: {received_time}")
                count += 1
            except Exception:
                # Some items might not have standard properties (e.g. meeting responses)
                continue
        
        if not results:
            return "No important/unread emails found."
            
        return "Important Emails:\n" + "\n".join(results)
    except Exception as e:
        return f"Error retrieving emails: {str(e)}"
