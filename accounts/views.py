from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import secrets

User = get_user_model()

reset_codes = {}

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

    # لا نكشف هل البريد موجود أم لا
    if not user:
        return JsonResponse({"ok": True})

    code = str(secrets.randbelow(900000) + 100000)
    reset_codes[email] = code

    send_mail(
        "رمز استعادة كلمة المرور - SERA",
        f"رمز استعادة كلمة المرور الخاص بك هو: {code}\n\nصلاحية الرمز 10 دقائق.",
        None,
        [email],
        fail_silently=False,
    )

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
