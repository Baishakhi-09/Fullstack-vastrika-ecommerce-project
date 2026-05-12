import hashlib
import hmac
import re
import secrets

from types import MappingProxyType


# =========================================================
# OTP CONSTANTS
# =========================================================

OTP_LENGTH = 6

OTP_MIN_VALUE = (
    10 ** (OTP_LENGTH - 1)
)

OTP_MAX_VALUE = (
    (10 ** OTP_LENGTH) - 1
)


# =========================================================
# PHONE CONSTANTS
# =========================================================

PHONE_MIN_LENGTH = 10
PHONE_MAX_LENGTH = 15

PHONE_VISIBLE_PREFIX = 3
PHONE_VISIBLE_SUFFIX = 3

PHONE_MASK = "****"


# =========================================================
# REGEX PATTERNS
# =========================================================

PHONE_SANITIZE_REGEX = re.compile(
    r"[^\d+]"
)

PHONE_VALIDATION_REGEX = re.compile(
    r"^\+\d{10,15}$"
)


# =========================================================
# IMMUTABLE SETTINGS
# =========================================================

PHONE_CONFIG = MappingProxyType({
    "MIN_LENGTH": PHONE_MIN_LENGTH,
    "MAX_LENGTH": PHONE_MAX_LENGTH,
})


# =========================================================
# OTP HELPERS
# =========================================================

def generate_otp() -> str:
    """
    Generate secure numeric OTP.
    """

    return str(
        secrets.randbelow(
            OTP_MAX_VALUE
            - OTP_MIN_VALUE
            + 1
        ) + OTP_MIN_VALUE
    )


def hash_otp(
    otp: str,
) -> str:
    """
    Hash OTP using SHA256.
    """

    return hashlib.sha256(
        otp.encode("utf-8")
    ).hexdigest()


def verify_hashed_otp(
    otp: str,
    stored_hash: str,
) -> bool:
    """
    Verify OTP securely using
    timing-safe comparison.
    """

    return hmac.compare_digest(
        hash_otp(otp),
        stored_hash,
    )


# =========================================================
# PHONE HELPERS
# =========================================================

def mask_phone(
    phone: str,
) -> str:
    """
    Safely mask phone number.
    """

    normalized_phone = (
        normalize_phone(phone)
    )

    visible_length = (
        PHONE_VISIBLE_PREFIX
        + PHONE_VISIBLE_SUFFIX
    )

    if len(normalized_phone) <= visible_length:
        return PHONE_MASK

    return (
        f"{normalized_phone[:PHONE_VISIBLE_PREFIX]}"
        f"{PHONE_MASK}"
        f"{normalized_phone[-PHONE_VISIBLE_SUFFIX:]}"
    )


def normalize_phone(
    phone: str,
) -> str:
    """
    Normalize and validate
    international phone number.
    """

    normalized_phone = (
        (phone or "")
        .strip()
    )

    normalized_phone = (
        PHONE_SANITIZE_REGEX.sub(
            "",
            normalized_phone,
        )
    )

    if not normalized_phone.startswith("+"):
        raise ValueError(
            "Phone number must include "
            "country code, like +91."
        )

    phone_length = len(
        normalized_phone
    ) - 1

    if (
        phone_length
        < PHONE_CONFIG["MIN_LENGTH"]
    ):
        raise ValueError(
            "Phone number is too short."
        )

    if (
        phone_length
        > PHONE_CONFIG["MAX_LENGTH"]
    ):
        raise ValueError(
            "Phone number is too long."
        )

    if not PHONE_VALIDATION_REGEX.fullmatch(
        normalized_phone
    ):
        raise ValueError(
            "Invalid phone number format."
        )

    return normalized_phone