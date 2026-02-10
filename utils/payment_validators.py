from __future__ import annotations
from datetime import datetime


def is_valid_card_number(card_number: str) -> bool:
    """
    Validates a 16-digit numeric card number.
    """
    return card_number.isdigit() and len(card_number) == 16


def is_valid_cvv(cvv: str) -> bool:
    """
    Validates a 3-digit CVV.
    """
    return cvv.isdigit() and len(cvv) == 3


def is_valid_expiry(expiry: str) -> bool:
    """
    Validates expiry in MM/YY format and checks not expired.
    """
    try:
        if len(expiry) != 5 or expiry[2] != "/":
            return False

        month, year = expiry.split("/")
        month = int(month)
        year = int("20" + year)

        if month < 1 or month > 12:
            return False

        now = datetime.now()
        expiry_date = datetime(year, month, 1)

        # card valid till end of expiry month
        return expiry_date.replace(day=28) >= now

    except Exception:
        return False


def is_valid_otp(otp: str) -> bool:
    """
    Validates a 6-digit OTP.
    """
    return otp.isdigit() and len(otp) == 6
