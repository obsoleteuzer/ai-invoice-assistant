# AI Invoice Assistant

Paste messy IT job notes (like "fixed printer, 2 hrs, new SSD $80") and AI turns them into a clean, itemized PayPal invoice. Built for the PayPal AI Hackathon 2026.

> ⚠️ This project uses the **PayPal sandbox** (test mode). No real money moves.

## Setup

```bash
git clone https://github.com/obsoleteuzer/ai-invoice-assistant.git
cd ai-invoice-assistant
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env             # Windows: copy .env.example .env
```

Open `.env` and paste your sandbox **Client ID** and **Secret** from the
[PayPal Developer Dashboard](https://developer.paypal.com/) (Apps & Credentials > Sandbox).
`.env` is ignored by git, so your keys stay private.

## Run

```bash
python create_test_invoice.py
```

This creates a sample invoice (2 hrs on-site troubleshooting + a 1TB SSD), sends it to a test customer, and prints the invoice ID, status, and payment link.
