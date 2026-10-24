"""
create_test_invoice.py

Milestone 1: create and send ONE test invoice in the PayPal *sandbox*.
The sandbox is PayPal's practice environment - no real money moves.

Steps:
  1. Load your PayPal keys from the .env file.
  2. Trade those keys for a short-lived "access token".
  3. Create a draft invoice with some sample IT line items.
  4. Send the invoice to a (fake) customer.
"""

import os
import sys

import requests
from dotenv import load_dotenv

# All sandbox API calls go to this address.
BASE_URL = "https://api-m.sandbox.paypal.com"

# Who the invoice goes to. Change this to your sandbox "personal" account
# email (Developer Dashboard > Testing Tools > Sandbox Accounts) if you like.
BUYER_EMAIL = "buyer@example.com"


def show_error(response):
    """Print PayPal's error message in a readable way, then stop the script."""
    print(f"PayPal returned an error (HTTP {response.status_code}):")
    try:
        data = response.json()
        print(" ", data.get("message") or data.get("error_description") or data)
        for detail in data.get("details", []):
            print("   -", detail.get("issue"), ":", detail.get("description"))
    except ValueError:
        print(" ", response.text)
    sys.exit(1)


def get_access_token(client_id, client_secret):
    """Log in to PayPal with our keys and get back an access token."""
    response = requests.post(
        f"{BASE_URL}/v1/oauth2/token",
        auth=(client_id, client_secret),          # keys are sent as Basic Auth
        data={"grant_type": "client_credentials"},
        timeout=30,
    )
    if response.status_code != 200:
        show_error(response)
    return response.json()["access_token"]


def create_invoice(token):
    """Create a DRAFT invoice and return its ID."""
    invoice = {
        "detail": {
            "currency_code": "USD",
            "note": "Thanks for your business!",
            "payment_term": {"term_type": "DUE_ON_RECEIPT"},
        },
        "invoicer": {"name": {"given_name": "Reep", "surname": "IT Services"}},
        "primary_recipients": [
            {"billing_info": {"email_address": BUYER_EMAIL}}
        ],
        # Each item: name, how many, and price per unit.
        "items": [
            {
                "name": "On-site troubleshooting",
                "quantity": "2",
                "unit_amount": {"currency_code": "USD", "value": "75.00"},
                "unit_of_measure": "HOURS",
            },
            {
                "name": "Samsung 1TB SSD",
                "quantity": "1",
                "unit_amount": {"currency_code": "USD", "value": "80.00"},
                "unit_of_measure": "QUANTITY",
            },
        ],
    }
    response = requests.post(
        f"{BASE_URL}/v2/invoicing/invoices",
        headers={"Authorization": f"Bearer {token}"},
        json=invoice,
        timeout=30,
    )
    if response.status_code not in (200, 201):
        show_error(response)
    # PayPal replies with a link to the new invoice; its ID is the last part.
    href = response.json()["href"]
    return href.rstrip("/").split("/")[-1]


def send_invoice(token, invoice_id):
    """Send the draft invoice to the customer. Returns the payer link if any."""
    response = requests.post(
        f"{BASE_URL}/v2/invoicing/invoices/{invoice_id}/send",
        headers={"Authorization": f"Bearer {token}"},
        json={"send_to_invoicer": True},
        timeout=30,
    )
    if response.status_code not in (200, 202):
        show_error(response)
    # The reply usually contains a "payer-view" link the customer pays from.
    return response.json().get("href") if response.text else None


def get_invoice(token, invoice_id):
    """Look up the invoice so we can show its current status."""
    response = requests.get(
        f"{BASE_URL}/v2/invoicing/invoices/{invoice_id}",
        headers={"Authorization": f"Bearer {token}"},
        timeout=30,
    )
    if response.status_code != 200:
        show_error(response)
    return response.json()


def main():
    load_dotenv()  # reads the .env file (if there is one) into env variables
    client_id = os.getenv("PAYPAL_CLIENT_ID")
    client_secret = os.getenv("PAYPAL_CLIENT_SECRET")
    if not client_id or not client_secret:
        print("Missing keys! Copy .env.example to .env and fill in your keys.")
        sys.exit(1)

    print("1. Getting access token...")
    token = get_access_token(client_id, client_secret)

    print("2. Creating draft invoice...")
    invoice_id = create_invoice(token)
    print("   Invoice ID:", invoice_id)

    print("3. Sending invoice...")
    payer_link = send_invoice(token, invoice_id)

    invoice = get_invoice(token, invoice_id)
    print("\nDone!")
    print("   Invoice ID:", invoice_id)
    print("   Status:    ", invoice.get("status"))
    print("   Total:     ", invoice.get("amount", {}).get("value"), "USD")
    if payer_link:
        print("   Payer link:", payer_link)


if __name__ == "__main__":
    main()
