from __future__ import annotations
import uuid


def process_payment(
    *,
    amount: float,
    method: str,
) -> dict:
    """
    Mock payment processor (booking-agnostic).

    Always succeeds for now.
    """

    if amount <= 0:
        raise ValueError("Invalid payment amount")

    if method not in ("card", "upi", "netbanking"):
        raise ValueError("Invalid payment method")

    # simulate successful payment
    transaction_id = str(uuid.uuid4())

    return {
        "amount": amount,
        "method": method,
        "transaction_id": transaction_id,
        "status": "success",
    }
