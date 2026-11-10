import re

# ---------- Verhoeff checksum (Aadhaar) ----------
D = [[0,1,2,3,4,5,6,7,8,9],[1,2,3,4,0,6,7,8,9,5],[2,3,4,0,1,7,8,9,5,6],[3,4,0,1,2,8,9,5,6,7],
     [4,0,1,2,3,9,5,6,7,8],[5,9,8,7,6,0,4,3,2,1],[6,5,9,8,7,1,0,4,3,2],[7,6,5,9,8,2,1,0,4,3],
     [8,7,6,5,9,3,2,1,0,4],[9,8,7,6,5,4,3,2,1,0]]
P = [[0,1,2,3,4,5,6,7,8,9],[1,5,7,6,2,8,3,0,9,4],[5,8,0,3,7,9,6,1,4,2],[8,9,1,6,0,4,3,5,2,7],
     [9,4,5,3,1,2,6,8,7,0],[4,2,8,6,5,7,3,9,0,1],[2,7,9,3,8,0,6,4,1,5],[7,0,4,6,9,1,3,2,5,8]]


def verhoeff_ok(num: str) -> bool:
    """True if the number has a valid Verhoeff checksum (used by Aadhaar)."""
    c = 0
    for i, ch in enumerate(reversed(num)):
        c = D[c][P[i % 8][int(ch)]]
    return c == 0


# ---------- Regex patterns ----------
AADHAAR_RE = re.compile(r"(?<!\d)[2-9]\d{3} ?\d{4} ?\d{4}(?!\d)")
# PAN: 3 letters + holder type + 1 letter + 4 digits + 1 letter (strict check)
PAN_RE     = re.compile(r"[A-Z]{3}[PCHFATBLJG][A-Z]\d{4}[A-Z]")
# Loose candidate: any 10 characters that MIGHT be a PAN damaged by OCR
PAN_CANDIDATE_RE = re.compile(r"(?<![A-Za-z0-9])[A-Z0-9]{5}[0-9OIlSBZ]{4}[A-Z0-9\]](?![A-Za-z0-9])")
MOBILE_RE  = re.compile(r"(?<!\d)(?:\+91[ -]?)?[6-9]\d{9}(?!\d)")
EMAIL_RE   = re.compile(r"\b[\w.+-]+@[\w-]+(?:\.[\w-]+)+\b")

MAX_OCR_REPAIRS = 2

# OCR look-alikes, both directions
OCR_DIGIT_FIX  = str.maketrans({"O": "0", "I": "1", "l": "1", "S": "5", "B": "8", "Z": "2"})   # where a digit belongs
OCR_LETTER_FIX = str.maketrans({"0": "O", "1": "I", "5": "S", "8": "B", "2": "Z", "]": "J"})   # where a letter belongs


# ---------- Finder functions ----------
def find_aadhaar(text: str) -> list[str]:
    """Aadhaar numbers without spaces, only those with a valid checksum."""
    results = []
    for match in AADHAAR_RE.findall(text):
        number = match.replace(" ", "")
        if verhoeff_ok(number):
            results.append(number)
    return results


def fix_pan_ocr(candidate: str) -> str:
    """Repair OCR look-alikes by position.
    Letters belong in positions 1-5 and 10, digits in 6-9:
    'VHJPJO529R' -> 'VHJPJ0529R',  'ZCPPM45780' -> 'ZCPPM4578O'."""
    return (candidate[:5].translate(OCR_LETTER_FIX)
            + candidate[5:9].translate(OCR_DIGIT_FIX)
            + candidate[9].translate(OCR_LETTER_FIX))


def find_pan(text: str) -> list[str]:
    """Find loose candidates, repair OCR mistakes, then keep only strictly valid PANs."""
    results = []
    for candidate in PAN_CANDIDATE_RE.findall(text):
        fixed = fix_pan_ocr(candidate)
        repairs = sum(a != b for a, b in zip(candidate, fixed))
        # OCR damages one or two characters, not half the number.
        # More repairs than that = probably not a PAN at all (e.g. a phone number).
        if repairs <= MAX_OCR_REPAIRS and PAN_RE.fullmatch(fixed):
            results.append(fixed)
    return results


def find_mobile(text: str) -> list[str]:
    """10-digit mobile numbers (the +91 is dropped)."""
    return [match[-10:] for match in MOBILE_RE.findall(text)]


def find_email(text: str) -> list[str]:
    return EMAIL_RE.findall(text)


# ---------- Helpers ----------
def mask(value: str) -> str:
    """'234567890124' -> 'XXXXXXXX0124'"""
    return "X" * (len(value) - 4) + value[-4:]


def scan_text(text: str) -> dict[str, list[str]]:
    """Run every detector on one piece of text."""
    return {
        "AADHAAR": find_aadhaar(text),
        "PAN": find_pan(text),
        "MOBILE": find_mobile(text),
        "EMAIL": find_email(text),
    }
