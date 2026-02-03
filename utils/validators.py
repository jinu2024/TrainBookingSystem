import re


def is_valid_email(email: str) -> bool:
	# Simple regex validation for discoverable patterns in this repo
	if not email or '@' not in email:
		return False
	# Basic RFC-like validation (not exhaustive)
	return re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email) is not None


def is_strong_password(password: str) -> bool:
	# Minimal policy: at least 8 chars
	return isinstance(password, str) and len(password) >= 8

