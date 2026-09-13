from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import secrets
import time

User = get_user_model()

reset_codes = {}
login_otps = {}

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

    try:
        send_mail(
            "رمز استعادة كلمة المرور - SERA",
            f"رمز استعادة كلمة المرور الخاص بك هو: {code}\n\nصلاحية الرمز 10 دقائق.",
            None,
            [email],
            fail_silently=False,
        )
    except Exception as e:
        print(f"RESET EMAIL ERROR: {e}")

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

    email_body = (
        "مرحباً بك في منصة SERA لإدارة المخالفات.\n\n"
        f"رمز التحقق الخاص بك لتسجيل الدخول هو: {code}\n\n"
        "صلاحية الرمز 10 دقائق.\n"
        "إذا لم تطلب هذا الرمز، يرجى تجاهل هذه الرسالة."
    )

    email_sent = False
    try:
        send_mail(
            "رمز التحقق لمنصة المخالفات - SERA",
            email_body,
            None,
            [email],
            fail_silently=False,
        )
        email_sent = True
    except Exception as e:
        print(f"EMAIL SMTP ERROR: {e}")

    return JsonResponse({
        "ok": True,
        "email_sent": email_sent,
        "message": "تم إرسال رمز التحقق إلى بريدك الإلكتروني بنجاح."
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
