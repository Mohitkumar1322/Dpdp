import re

# 1. Copy the D and P tables and verhoeff_ok() from generate_fake_data.py
#    (later we'll share one copy; for now copying is fine)


# 2. Regex patterns
AADHAAR_RE = re.compile(r"TODO")   # 12 digits, first is 2-9, optional single spaces after digit 4 and 8
PAN_RE     = re.compile(r"TODO")   # 3 letters + holder letter (P C H F A T B L J G) + 1 letter + 4 digits + 1 letter
MOBILE_RE  = re.compile(r"TODO")   # optional "+91 ", then 10 digits starting 6-9
EMAIL_RE   = re.compile(r"TODO")

def verhoeff_ok(num: str) -> bool:
    c = 0
    for i, ch in enumerate(reversed(num)):
        c = D[c][P[i % 8][int(ch)]]
    return c == 0

def find_aadhaar(text):
    """Return a list of Aadhaar numbers WITHOUT spaces, only if the checksum is valid."""
    # TODO: findall, remove spaces, keep only those where verhoeff_ok() is True


def find_pan(text):
    # TODO


def find_mobile(text):
    """Return 10-digit numbers only (drop the +91)."""
    # TODO


def find_email(text):
    # TODO


def mask(value):
    """'234567890124' -> 'XXXXXXXX0124'"""
    # TODO


def scan_text(text):
    """Return {"AADHAAR": [...], "PAN": [...], "MOBILE": [...], "EMAIL": [...]}"""
    # TODO