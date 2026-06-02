"""
Salesforce Tools — Uses simple-salesforce library.
Requires credentials to be configured via the Settings page.
"""
import json
from database import get_credentials

def _get_sf_client():
    """Build a Salesforce client using stored credentials."""
    creds = get_credentials("salesforce")
    if not creds or not creds.get("instance_url"):
        raise Exception("Salesforce is not configured. Please add credentials in Settings.")
    try:
        from simple_salesforce import Salesforce
        sf = Salesforce(
            username=creds.get("username"),
            password=creds.get("password"),
            security_token=creds.get("security_token"),
            domain=creds.get("domain", "login")
        )
        return sf
    except ImportError:
        raise Exception("simple-salesforce package not installed. Run: pip install simple-salesforce")

def query_salesforce(query: str) -> str:
    """Run a SOQL query against Salesforce."""
    sf = _get_sf_client()
    result = sf.query(query)
    records = result.get("records", [])
    if not records:
        return "No records found."
    output = []
    for rec in records[:20]:
        clean = {k: v for k, v in rec.items() if k != "attributes"}
        output.append(json.dumps(clean))
    return f"Found {result['totalSize']} records:\n" + "\n".join(output)

def create_salesforce_record(object_type: str, data: str) -> str:
    """Create a record in Salesforce."""
    sf = _get_sf_client()
    fields = json.loads(data)
    sf_object = getattr(sf, object_type)
    result = sf_object.create(fields)
    return f"Created {object_type} record with ID: {result['id']}"
