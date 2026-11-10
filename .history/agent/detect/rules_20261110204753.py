import re

# 1. Copy the D and P tables and verhoeff_ok() from generate_fake_data.py
#    (later we'll share one copy; for now copying is fine)


# 2. Regex patterns
AADHAAR_RE = re.compile(r"TODO")   # 12 digits, first is 2-9, optional single spaces after digit 4 and 8
PAN_RE     = re.compile(r"TODO")   # 3 letters + holder letter (P C H F A T B L J G) + 1 letter + 4 digits + 1 letter
MOBILE_RE  = re.compile(r"TODO")   # optional "+91 ", then 10 digits starting 6-9
EMAIL_RE   = re.compile(r"TODO")

D = [[0,1,2,3,4,5,6,7,8,9],[1,2,3,4,0,6,7,8,9,5],[2,3,4,0,1,7,8,9,5,6],[3,4,0,1,2,8,9,5,6,7],
     [4,0,1,2,3,9,5,6,7,8],[5,9,8,7,6,0,4,3,2,1],[6,5,9,8,7,1,0,4,3,2],[7,6,5,9,8,2,1,0,4,3],
     [8,7,6,5,9,3,2,1,0,4],[9,8,7,6,5,4,3,2,1,0]]
P = [[0,1,2,3,4,5,6,7,8,9],[1,5,7,6,2,8,3,0,9,4],[5,8,0,3,7,9,6,1,4,2],[8,9,1,6,0,4,3,5,2,7],
     [9,4,5,3,1,2,6,8,7,0],[4,2,8,6,5,7,3,9,0,1],[2,7,9,3,8,0,6,4,1,5],[7,0,4,6,9,1,3,2,5,8]]

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