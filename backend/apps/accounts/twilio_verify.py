import logging
from types import MappingProxyType

from django.conf import settings

from twilio.rest import Client
from twilio.base.exceptions import (
    TwilioRestException,
)


logger = logging.getLogger(__name__)


# =========================================================
# TWILIO CHANNELS
# =========================================================

TWILIO_CHANNEL_SMS = "sms"


# =========================================================
# TWILIO SETTINGS
# =========================================================

TWILIO_SETTINGS = MappingProxyType({
    "ACCOUNT_SID": getattr(
        settings,
        "TWILIO_ACCOUNT_SID",
        None,
    ),

    "AUTH_TOKEN": getattr(
        settings,
        "TWILIO_AUTH_TOKEN",
        None,
    ),

    "VERIFY_SERVICE_SID": getattr(
        settings,
        "TWILIO_VERIFY_SERVICE_SID",
        None,
    ),
})


# =========================================================
# HELPERS
# =========================================================

def get_twilio_setting(
    key: str,
) -> str:
    """
    Retrieve required Twilio setting.
    """

    value = TWILIO_SETTINGS.get(key)

    if not value:
        raise ValueError(
            f"Missing Twilio setting: {key}"
        )

    return value


def get_twilio_client() -> Client:
    """
    Build and return Twilio client.
    """

    return Client(
        get_twilio_setting(
            "ACCOUNT_SID",
        ),

        get_twilio_setting(
            "AUTH_TOKEN",
        ),
    )


def normalize_phone_number(
    phone_number: str,
) -> str:
    """
    Normalize phone number.
    """

    return phone_number.strip()


# =========================================================
# SEND VERIFICATION CODE
# =========================================================

def send_verification_code(
    phone_number: str,
) -> tuple[bool, dict]:
    """
    Send Twilio verification OTP.
    """

    try:
        normalized_phone = (
            normalize_phone_number(
                phone_number,
            )
        )

        client = get_twilio_client()

        verification = (
            client.verify.v2.services(
                get_twilio_setting(
                    "VERIFY_SERVICE_SID",
                )
            )
            .verifications
            .create(
                to=normalized_phone,
                channel=TWILIO_CHANNEL_SMS,
            )
        )

        return True, {
            "sid": verification.sid,
            "status": verification.status,
            "to": normalized_phone,
        }

    except (
        TwilioRestException,
        ValueError,
    ) as exc:

        logger.exception(
            "Failed to send "
            "Twilio verification OTP."
        )

        return False, {
            "success": False,
            "error": str(exc),
        }


# =========================================================
# CHECK VERIFICATION CODE
# =========================================================

def check_verification_code(
    phone_number: str,
    code: str,
) -> tuple[bool, dict]:
    """
    Verify Twilio OTP code.
    """

    try:
        normalized_phone = (
            normalize_phone_number(
                phone_number,
            )
        )

        normalized_code = code.strip()

        client = get_twilio_client()

        verification_check = (
            client.verify.v2.services(
                get_twilio_setting(
                    "VERIFY_SERVICE_SID",
                )
            )
            .verification_checks
            .create(
                to=normalized_phone,
                code=normalized_code,
            )
        )

        is_verified = (
            verification_check.status
            == "approved"
        )

        return True, {
            "sid": verification_check.sid,
            "status": (
                verification_check.status
            ),
            "valid": is_verified,
            "to": normalized_phone,
        }

    except (
        TwilioRestException,
        ValueError,
    ) as exc:

        logger.exception(
            "Failed to verify "
            "Twilio OTP code."
        )

        return False, {
            "success": False,
            "error": str(exc),
        }