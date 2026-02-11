import re
from datetime import datetime, date


def is_valid_email(email: str) -> bool:
    # Simple regex validation for discoverable patterns in this repo
    if not email or "@" not in email:
        return False
    # Basic RFC-like validation (not exhaustive)
    return re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email) is not None


def is_strong_password(password: str) -> bool:
    """
    Password policy:
    - At least 8 characters
    - At least 1 uppercase letter
    - At least 1 lowercase letter
    - At least 1 digit
    - At least 1 special character
    """
    if not isinstance(password, str) or len(password) < 8:
        return False

    has_upper = re.search(r"[A-Z]", password)
    has_lower = re.search(r"[a-z]", password)
    has_digit = re.search(r"\d", password)
    has_special = re.search(r"[^\w\s]", password)

    return all([has_upper, has_lower, has_digit, has_special])


def is_valid_date_of_birth(dob: str) -> bool:
    """
    Validate date of birth:
    - Must be in YYYY-MM-DD format
    - User must be at least 16 years old
    """
    if not isinstance(dob, str):
        return False

    try:
        birth_date = datetime.strptime(dob, "%Y-%m-%d").date()
    except ValueError:
        return False

    today = date.today()

    # Calculate age
    age = (
        today.year
        - birth_date.year
        - ((today.month, today.day) < (birth_date.month, birth_date.day))
    )

    return age >= 16


def is_valid_schedule_date(travel_date: str) -> bool:
    """
    Validate schedule date:
    - Must be in YYYY-MM-DD format
    - Cannot be in the past
    - Cannot be more than 1 year in the future
    """
    if not isinstance(travel_date, str):
        return False

    try:
        schedule_date = datetime.strptime(travel_date, "%Y-%m-%d").date()
    except ValueError:
        return False

    today = date.today()

    # Not in the past
    if schedule_date < today:
        return False

    # Not more than 1 year ahead
    one_year_later = today.replace(year=today.year + 1)

    return schedule_date <= one_year_later


def is_valid_mobile_number(mobile: str) -> bool:
    """
    Validate Indian mobile number:
    - Must be exactly 10 digits
    - Must start with 6, 7, 8, or 9
    """
    if not isinstance(mobile, str):
        return False

    return re.match(r"^[6-9]\d{9}$", mobile) is not None


def is_valid_aadhaar(aadhaar: str) -> bool:
    """
    Validate Aadhaar number:
    - Must be exactly 12 digits
    - Must contain only digits
    """
    if not isinstance(aadhaar, str):
        return False

    return re.match(r"^\d{12}$", aadhaar) is not None


def is_valid_train_number(train_number: str) -> bool:
    """
    Validate train number:
    - Must be exactly 6 digits
    - Must contain only digits
    """
    if not isinstance(train_number, str):
        return False

    return re.match(r"^\d{6}$", train_number) is not None


def is_valid_station_code(station_code: str) -> bool:
    """
    Validate station code:
    - exactly 6 characters
    - uppercase letters + digits only
    - trims spaces
    - auto converts lowercase to uppercase
    """

    if not isinstance(station_code, str):
        return False

    station_code = station_code.strip().upper()

    return bool(re.fullmatch(r"[A-Z0-9]{6}", station_code))


def is_valid_time(t: str) -> bool:
    try:
        datetime.strptime(t, "%H:%M")
        return True
    except Exception:
        return False


def is_valid_fare(f: str) -> bool:
    try:
        return float(f) > 0
    except Exception:
        return False
