"""Generate FAKE Indian documents for testing the scanner.
Writes text files to testdata/ and the ground truth (what is in each file) to testdata/labels.json.
"""
import json
import random
import string
from pathlib import Path

from faker import Faker

fake = Faker("en_IN")
OUT = Path("testdata")

# ---- Verhoeff checksum (used by real Aadhaar numbers) ----
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

def fake_aadhaar(valid: bool = True) -> str:
    """12 digits, first digit 2-9. valid=False gives a WRONG checksum (to test false positives)."""
    base = str(random.randint(2, 9)) + "".join(random.choices(string.digits, k=10))
    for d in string.digits:
        if verhoeff_ok(base + d) == valid:
            n = base + d
            return f"{n[:4]} {n[4:8]} {n[8:]}"

def fake_pan() -> str:
    return ("".join(random.choices(string.ascii_uppercase, k=3)) + "P"
            + random.choice(string.ascii_uppercase)
            + "".join(random.choices(string.digits, k=4))
            + random.choice(string.ascii_uppercase))

def fake_mobile() -> str:
    return random.choice("6789") + "".join(random.choices(string.digits, k=9))

# ---- Document templates ----
def salary_slip():
    name, aad, pan, mob = fake.name(), fake_aadhaar(), fake_pan(), fake_mobile()
    text = (f"SALARY SLIP - {fake.month_name()} 2026\n{fake.company()}\n"
            f"Employee Name: {name}\nPAN: {pan}\nAadhaar No: {aad}\nMobile: +91 {mob}\n"
            f"Address: {fake.address().replace(chr(10), ', ')}\n"
            f"Basic: Rs {random.randint(20, 90)},000  HRA: Rs {random.randint(5, 30)},000\n")
    return "salary_slip", text, {"AADHAAR": 1, "PAN": 1, "MOBILE": 1, "EMAIL": 0}

def kyc_form():
    name, aad, pan, mob, email = fake.name(), fake_aadhaar(), fake_pan(), fake_mobile(), fake.email()
    text = (f"KYC APPLICATION FORM\nFull Name: {name}\nDate of Birth: {fake.date_of_birth(minimum_age=18)}\n"
            f"Aadhaar: {aad}\nPAN Card: {pan}\nPhone: {mob}\nEmail: {email}\n"
            f"Permanent Address: {fake.address().replace(chr(10), ', ')}\n")
    return "kyc_form", text, {"AADHAAR": 1, "PAN": 1, "MOBILE": 1, "EMAIL": 1}

def invoice():
    # Contains a 12-digit invoice number with a WRONG checksum: a good false-positive test.
    inv = fake_aadhaar(valid=False).replace(" ", "")
    text = (f"TAX INVOICE\nInvoice No: {inv}\nBill To: {fake.company()}\n"
            f"Contact: {fake.email()}\nAmount: Rs {random.randint(1000, 99999)}\n")
    return "invoice", text, {"AADHAAR": 0, "PAN": 0, "MOBILE": 0, "EMAIL": 1}

def clean_doc():
    return "other", fake.paragraph(nb_sentences=8) + "\n", {"AADHAAR": 0, "PAN": 0, "MOBILE": 0, "EMAIL": 0}

def main(n: int = 200):
    OUT.mkdir(exist_ok=True)
    labels = {}
    makers = [salary_slip, kyc_form, invoice, clean_doc]
    for i in range(n):
        doc_type, text, expected = random.choice(makers)()
        fname = f"doc_{i:04d}.txt"
        (OUT / fname).write_text(text, encoding="utf-8")
        labels[fname] = {"doc_type": doc_type, "expected": expected}
    (OUT / "labels.json").write_text(json.dumps(labels, indent=2))
    print(f"Created {n} fake documents in {OUT}/ (ground truth in labels.json)")

if __name__ == "__main__":
    random.seed(42)
    Faker.seed(42)
    main()
