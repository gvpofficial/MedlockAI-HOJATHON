import base64
import hashlib
import io
import json
import random
import string
import qrcode
from datetime import datetime


def generate_prescription_code() -> str:
    year = datetime.now().year
    suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
    return f"RX-{year}-{suffix}"


def generate_digital_signature(doctor_id: str, patient_id: str, items: list, issue_date: str) -> str:
    raw = f"{doctor_id}|{patient_id}|{json.dumps(items, sort_keys=True)}|{issue_date}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def generate_qr_code_base64(data: str) -> str:
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=8,
        border=2,
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
    return f"data:image/png;base64,{img_str}"
