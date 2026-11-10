import re

# ---------- Verhoeff checksum (Aadhaar) ----------
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


# ---------- Regex patterns ----------
AADHAAR_RE = re.compile(r"(?<!\d)[2-9]\d{3} ?\d{4} ?\d{4}(?!\d)")       # done

# BLANK 1: after [PCHFATBLJG] add: one capital letter, 4 digits, one capital letter
PAN_RE = re.compile(r"\b[A-Z]{3}[PCHFATBLJG]___\b")

# BLANK 2: first digit 6-9, then exactly 9 more digits
MOBILE_RE = re.compile(r"(?<!\d)(?:\+91[ -]?)?___(?!\d)")

EMAIL_RE = re.compile(r"\b[\w.+-]+@[\w-]+(?:\.[\w-]+)+\b")              # done


# ---------- Finder functions ----------
def find_aadhaar(text):
    """Return Aadhaar numbers WITHOUT spaces, only if the checksum is valid."""
    results = []
    for match in AADHAAR_RE.findall(text):
        number = match.replace(" ", "")
        if verhoeff_ok(number):
            results.append(number)
    return results


def find_pan(text):
    return PAN_RE.findall(text)


def find_mobile(text):
    """Return 10-digit numbers only (drop the +91)."""
    results = []
    for match in MOBILE_RE.findall(text):
        results.append(___)          # BLANK 3: keep only the last 10 characters of match
    return results


def find_email(text):
    return ___                       # BLANK 4: same idea as find_pan, but with EMAIL_RE


def mask(value):
    """'234567890124' -> 'XXXXXXXX0124'"""
    return "X" * (len(value) - 4) + value[-4:]


def scan_text(text):
    return {
        "AADHAAR": find_aadhaar(text),
        "PAN": find_pan(text),
        "MOBILE": ___,               # BLANK 5
        "EMAIL": find_email(text),
    }