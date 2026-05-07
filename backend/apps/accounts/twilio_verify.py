from django.conf import settings
from twilio.rest import Client


def get_twilio_client():
    account_sid = getattr(settings, "TWILIO_ACCOUNT_SID", None)
    auth_token = getattr(settings, "TWILIO_AUTH_TOKEN", None)

    if not account_sid:
        raise ValueError("Missing TWILIO_ACCOUNT_SID")
    if not auth_token:
        raise ValueError("Missing TWILIO_AUTH_TOKEN")
    
    return Client(account_sid, auth_token)


def send_verification_code(phone_number: str):
    try:
        service_sid = getattr(settings, "TWILIO_VERIFY_SERVICE_SID", None)

        if not service_sid:
            return False, {"error": "Missing TWILIO_VERIFY_SERVICE_SID"}

        client = get_twilio_client()

        verification = client.verify.v2.services(
            service_sid
        ).verifications.create(
            to=phone_number,
            channel="sms",
        )

        return True, {
            "sid": verification.sid,
            "status": verification.status,
            "to": phone_number,
        }

    except Exception as exc:
        return False, {"error": str(exc)}


def check_verification_code(phone_number: str, code: str):
    try:
        service_sid = getattr(settings, "TWILIO_VERIFY_SERVICE_SID", None)

        if not service_sid:
            return False, {"error": "Missing TWILIO_VERIFY_SERVICE_SID"}

        client = get_twilio_client()

        check = client.verify.v2.services(
            service_sid
        ).verification_checks.create(
            to=phone_number,
            code=code,
        )

        return True, {
            "sid": check.sid,
            "status": check.status,
            "valid": check.status == "approved",
            "to": phone_number,
        }

    except Exception as exc:
        return False, {"error": str(exc)}