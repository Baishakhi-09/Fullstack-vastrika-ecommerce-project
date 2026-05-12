import hashlib
import secrets
import re

def generate_otp() -> str:
    return str(secrets.randbelow(900000) + 100000)

def hash_otp(otp: str) -> str:
    return hashlib.sha256(otp.encode("utf-8")).hexdigest()

def mask_phone(phone: str) -> str:
    if len(phone) < 6:
        return phone
    return f"{phone[:3]}****{phone[-3:]}"

def normalize_phone(phone: str) -> str:
    phone = (phone or "").strip()
    phone = re.sub(r"[^\d+]", "", phone)

    if not phone.startswith("+"):
        raise ValueError("Phone number must include country code, like +91.")
    
    if len(phone) < 10 or len(phone) > 16:
        raise ValueError("Invalid phone number length.")
    
    if not re.fullmatch(r"^\+\d{10,15}$", phone):
        raise ValueError("Invalid phone number format.")

    return phone