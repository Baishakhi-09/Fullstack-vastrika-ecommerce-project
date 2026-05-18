from __future__ import annotations

import hashlib
import re
import secrets


# =========================================================
# CONSTANTS
# =========================================================
OTP_DIGITS = 6

OTP_MIN_VALUE = 100000

OTP_MAX_RANGE = 900000

PHONE_MIN_DIGITS = 10

PHONE_MAX_DIGITS = 15

PHONE_MASK_PREFIX = 3

PHONE_MASK_SUFFIX = 3


# =========================================================
# REGEX
# =========================================================
PHONE_REGEX = re.compile(
    r"^\+\d{10,15}$"
)

PHONE_SANITIZE_REGEX = re.compile(
    r"[^\d+]"
)


# =========================================================
# OTP UTILITIES
# =========================================================
def generate_otp() -> str:
    """
    Generate a secure numeric OTP.

    Returns:
        str: Random 6-digit OTP.
    """

    return str(
        secrets.randbelow(
            OTP_MAX_RANGE
        ) + OTP_MIN_VALUE
    )


def hash_otp(
    otp: str,
) -> str:
    """
    Generate SHA256 hash for OTP.

    Args:
        otp (str): Raw OTP value.

    Returns:
        str: Hashed OTP string.
    """

    return hashlib.sha256(
        otp.encode("utf-8")
    ).hexdigest()


# =========================================================
# PHONE UTILITIES
# =========================================================
def mask_phone(
    phone: str | None,
) -> str:
    """
    Mask phone number for secure display.

    Example:
        +919876543210
        -> +91****210

    Args:
        phone (str | None): Raw phone number.

    Returns:
        str: Masked phone number.
    """

    phone = str(phone or "").strip()

    if len(phone) < (
        PHONE_MASK_PREFIX
        + PHONE_MASK_SUFFIX
    ):
        return phone

    return (
        f"{phone[:PHONE_MASK_PREFIX]}"
        f"****"
        f"{phone[-PHONE_MASK_SUFFIX:]}"
    )


def normalize_phone(
    phone: str | None,
) -> str:
    """
    Normalize and validate phone number.

    Rules:
    - Must include country code
    - Must start with '+'
    - Only digits allowed after '+'
    - Length must be between 10-15 digits

    Example:
        +91 98765-43210
        -> +919876543210

    Args:
        phone (str | None): Raw phone number.

    Returns:
        str: Normalized phone number.

    Raises:
        ValueError: If phone format is invalid.
    """

    phone = str(phone or "").strip()

    phone = PHONE_SANITIZE_REGEX.sub(
        "",
        phone,
    )

    if not phone.startswith("+"):
        raise ValueError(
            "Phone number must include "
            "country code like +91."
        )

    digit_count = len(
        phone.replace("+", "")
    )

    if (
        digit_count < PHONE_MIN_DIGITS
        or digit_count > PHONE_MAX_DIGITS
    ):
        raise ValueError(
            "Invalid phone number length."
        )

    if not PHONE_REGEX.fullmatch(phone):
        raise ValueError(
            "Invalid phone number format."
        )

    return phone