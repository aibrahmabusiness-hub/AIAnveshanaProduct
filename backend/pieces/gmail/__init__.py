from tools.gmail_tools import read_gmail_inbox, mark_gmail_read, send_gmail

PIECE_MANIFEST = {
    "name": "Gmail",
    "description": "Send, search, and manage emails in your Gmail account.",
    "version": "1.0.0",
    "icon": "✉️",
    "actions": {
        "gmail_read": {
            "name": "Gmail (Search & Read)",
            "description": "Search and read emails from Gmail inbox",
            "callable": read_gmail_inbox
        },
        "gmail_mark_read": {
            "name": "Gmail (Mark Read)",
            "description": "Mark a specific email as read",
            "callable": mark_gmail_read
        },
        "gmail_send": {
            "name": "Gmail (Send)",
            "description": "Send emails via Gmail",
            "callable": send_gmail
        }
    }
}
