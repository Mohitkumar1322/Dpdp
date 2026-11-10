"""Phase 1 tests. Run with:  python -m pytest -v
All tests pass = your rules.py is correct."""
from agent.detect.rules import (verhoeff_ok, find_aadhaar, find_pan,
                                find_mobile, find_email, mask, scan_text)

VALID_AADHAAR = "234567890124"      # correct Verhoeff checksum
INVALID_AADHAAR = "234567890125"    # last digit changed -> wrong checksum


# ---------- Verhoeff ----------
def test_verhoeff_accepts_valid():
    assert verhoeff_ok(VALID_AADHAAR)

def test_verhoeff_rejects_invalid():
    assert not verhoeff_ok(INVALID_AADHAAR)


# ---------- Aadhaar ----------
def test_aadhaar_with_spaces():
    assert find_aadhaar("Aadhaar No: 2345 6789 0124") == [VALID_AADHAAR]

def test_aadhaar_without_spaces():
    assert find_aadhaar("UID 234567890124 issued") == [VALID_AADHAAR]

def test_aadhaar_wrong_checksum_ignored():
    assert find_aadhaar("Invoice No: 234567890125") == []

def test_aadhaar_cannot_start_with_0_or_1():
    assert find_aadhaar("ref 1234 5678 9012 and 0234 5678 9012") == []

def test_aadhaar_not_part_of_longer_number():
    assert find_aadhaar("txn 92345678901245") == []


# ---------- PAN ----------
def test_pan_valid():
    assert find_pan("PAN: ABCPE1234F") == ["ABCPE1234F"]

def test_pan_wrong_holder_type_ignored():
    # 4th letter must be one of P C H F A T B L J G
    assert find_pan("code ABCZE1234F") == []

def test_pan_lowercase_ignored():
    assert find_pan("abcpe1234f") == []


# ---------- Mobile ----------
def test_mobile_plain():
    assert find_mobile("Phone: 9876543210") == ["9876543210"]

def test_mobile_with_country_code():
    assert find_mobile("Mobile: +91 9876543210") == ["9876543210"]

def test_mobile_must_start_6_to_9():
    assert find_mobile("call 5876543210") == []

def test_mobile_not_part_of_aadhaar():
    assert find_mobile("Aadhaar 234567890124") == []


# ---------- Email ----------
def test_email():
    assert find_email("Email: rahul.sharma@example.in") == ["rahul.sharma@example.in"]


# ---------- Masking ----------
def test_mask_keeps_last_four():
    assert mask("234567890124") == "XXXXXXXX0124"


# ---------- Whole document ----------
def test_scan_text_kyc_form():
    text = ("KYC FORM\nName: Priya Nair\nAadhaar: 2345 6789 0124\n"
            "PAN Card: ABCPE1234F\nPhone: 9876543210\nEmail: priya@example.in\n")
    result = scan_text(text)
    assert result["AADHAAR"] == [VALID_AADHAAR]
    assert result["PAN"] == ["ABCPE1234F"]
    assert result["MOBILE"] == ["9876543210"]
    assert result["EMAIL"] == ["priya@example.in"]


# ---------- OCR repair (Phase 2) ----------
def test_pan_ocr_letter_o_read_as_zero():
    assert find_pan("PAN Card: VHJPJO529R") == ["VHJPJ0529R"]

def test_pan_ocr_several_mistakes():
    assert find_pan("PAN: ABCPEI2S4F") == ["ABCPE1254F"]

def test_pan_ocr_does_not_touch_letters_part():
    # letters in positions 1-5 and 10 must stay as they are
    assert find_pan("PAN: OBCPE1234O") == ["OBCPE1234O"]

def test_pan_still_rejects_wrong_holder_type():
    assert find_pan("code ABCZEO234F") == []

def test_pan_ocr_last_letter_read_as_digit():
    assert find_pan("PAN: ZCPPM45780") == ["ZCPPM4578O"]

def test_pan_ocr_j_read_as_bracket():
    assert find_pan("PAN Card: PFXPR3246]") == ["PFXPR3246J"]

def test_ten_digit_number_is_not_a_pan():
    assert find_pan("Phone 9876543210 and 1258012580") == []
