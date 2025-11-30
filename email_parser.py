import re

def parse_lead_email(email_text):
    """
    Extracts customer name and phone number from email text.
    """
    # Extract phone number
    phone_regex = r'(\+?1?\s*\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4})'
    phone_match = re.search(phone_regex, email_text)

    # Extract name (simple version)
    name_regex = r"Name[:\- ]+([A-Za-z ]+)"
    name_match = re.search(name_regex, email_text)

    customer_name = name_match.group(1).strip() if name_match else "New Lead"
    customer_phone = phone_match.group(1).strip() if phone_match else None

    return customer_name, customer_phone