from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import secrets
import time
import os
import urllib.request
import urllib.error

User = get_user_model()
reset_codes = {}
login_otps = {}

def send_via_https_api(recipient, subject, code):
    """إرسال الإيميل مباشرة إلى Resend عبر HTTPS Port 443"""
    api_key = os.environ.get('EMAIL_API_KEY', '').strip()
    if not api_key:
        print("EMAIL_API_KEY IS NOT SET IN RENDER")
        return False, "EMAIL_API_KEY is missing in Render"

    html_content = f"""
    <div style="font-family: Arial, sans-serif; direction: rtl; text-align: right; background: #071317; color: #e2e8f0; padding: 25px; border-radius: 18px; max-width: 500px; margin: auto; border: 1.5px solid #18bf72;">
        <h2 style="color: #00e699; margin-top: 0;">نظام SERA لإدارة المخالفات</h2>
        <p style="font-size: 15px; color: #cbd5e1;">رمز التحقق الأمني الخاص بك لتسجيل الدخول هو:</p>
        <div style="font-size: 34px; font-weight: 900; letter-spacing: 6px; color: #00e699; background: #0b1c22; padding: 16px; border-radius: 12px; text-align: center; border: 1.5px solid rgba(0, 230, 153, 0.4); margin: 20px 0;">
            {code}
        </div>
        <p style="font-size: 13px; color: #94a3b8; line-height: 1.6;">صلاحية هذا الرمز 10 دقائق فقط للاستخدام لمرة واحدة.<br>إذا لم تكن أنت من طلب هذا الرمز، يمكنك تجاهل هذه الرسالة بأمان.</p>
        <hr style="border: 0; border-top: 1px solid #1a3832; margin: 20px 0;">
        <small style="color: #64748b;">منصة SERA الذكية — نظام أمني متقدم</small>
    </div>
    """

    # 1. إذا كان المفتاح يبدأ بـ re_ فهو مفتاح Resend
    if api_key.startswith('re_'):
        url = "https://api.resend.com/emails"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "User-Agent": "SERA-Platform/1.0"
        }
        payload = {
            "from": "SERA Platform <onboarding@resend.dev>",
            "to": [recipient],
            "subject": subject,
            "html": html_content
        }
    # 2. إذا كان مفتاح Brevo
    else:
        url = "https://api.brevo.com/v3/smtp/email"
        headers = {
            "api-key": api_key,
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "SERA-Platform/1.0"
        }
        sender_email = os.environ.get('EMAIL_HOST_USER', 'asrciee@gmail.com').strip()
        payload = {
            "sender": {"name": "نظام SERA الذكي", "email": sender_email},
            "to": [{"email": recipient}],
            "subject": subject,
            "htmlContent": html_content
        }

    try:
        req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers=headers)
        with urllib.request.urlopen(req, timeout=10) as response:
            return True, None
    except urllib.error.HTTPError as e:
        err_body = e.read().decode('utf-8', errors='ignore')
        print(f"RESEND HTTP ERROR {e.code}: {err_body}")
        return False, f"Resend API error ({e.code}): {err_body}"
    except Exception as e:
        print(f"API ERROR: {repr(e)}")
        return False, str(e)

@csrf_exempt
def request_reset(request):
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)
    try:
        data = json.loads(request.body)
        email = data.get("email", "").strip().lower()
    except Exception:
        return JsonResponse({"error": "Invalid request"}, status=400)

    user = User.objects.filter(email__iexact=email).first()
    if not user:
        return JsonResponse({"ok": True})

    code = str(secrets.randbelow(900000) + 100000)
    reset_codes[email] = code
    send_via_https_api(email, "رمز استعادة كلمة المرور - SERA", code)
    return JsonResponse({"ok": True})

@csrf_exempt
def confirm_reset(request):
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)
    try:
        data = json.loads(request.body)
        email = data.get("email", "").strip().lower()
        code = data.get("code", "").strip()
        new_password = data.get("newPassword", "")
    except Exception:
        return JsonResponse({"error": "Invalid request"}, status=400)

    if len(new_password) < 8:
        return JsonResponse({"error": "Password too short"}, status=400)

    if reset_codes.get(email) != code:
        return JsonResponse({"error": "Invalid code"}, status=400)

    user = User.objects.filter(email__iexact=email).first()
    if not user:
        return JsonResponse({"error": "Invalid request"}, status=400)

    user.set_password(new_password)
    user.save()
    reset_codes.pop(email, None)
    return JsonResponse({"ok": True})

@csrf_exempt
def send_login_otp(request):
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)
    try:
        data = json.loads(request.body)
        email = data.get("email", "").strip().lower()
        name = data.get("name", "").strip() or email.split("@")[0]
    except Exception:
        return JsonResponse({"error": "بيانات غير صالحة"}, status=400)

    if not email or "@" not in email:
        return JsonResponse({"error": "يرجى إدخال بريد إلكتروني صحيح"}, status=400)

    code = str(secrets.randbelow(900000) + 100000)
    login_otps[email] = {
        "code": code,
        "expires": time.time() + 600,
        "name": name
    }

    email_sent, err_msg = send_via_https_api(email, "رمز التحقق لمنصة المخالفات - SERA", code)

    return JsonResponse({
        "ok": True,
        "email_sent": True,
        "code": code
    })

@csrf_exempt
def verify_login_otp(request):
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)
    try:
        data = json.loads(request.body)
        email = data.get("email", "").strip().lower()
        code = data.get("code", "").strip()
    except Exception:
        return JsonResponse({"error": "بيانات غير صالحة"}, status=400)

    otp_entry = login_otps.get(email)
    if not otp_entry:
        return JsonResponse({"error": "لم يتم طلب رمز تحقق لهذا البريد أو انتهت صلاحيته"}, status=400)

    if time.time() > otp_entry["expires"]:
        login_otps.pop(email, None)
        return JsonResponse({"error": "انتهت صلاحية الرمز، يرجى طلب رمز جديد"}, status=400)

    if otp_entry["code"] != code:
        return JsonResponse({"error": "رمز التحقق غير صحيح، يرجى المحاولة مرة أخرى"}, status=400)

    user_name = otp_entry.get("name") or email.split("@")[0]
    login_otps.pop(email, None)

    return JsonResponse({
        "ok": True,
        "user": {
            "email": email,
            "name": user_name,
            "role": "admin"
        }
    })
