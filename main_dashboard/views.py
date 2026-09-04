from django.shortcuts import get_object_or_404, render
from django.db import connection
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
import json

from .models import Violation


# أسماء الحقول التي يمكن تعديلها، مع دعم أسماء الواجهة العربية أيضًا.
FIELD_MAP = {
    "رقم المحضر": "violation_number",
    "المنسوب له المخالفة": "attributed_person",
    "موقع المخالفة": "violation_location",
    "موقع المخالفة (المنطقة، المدينة)": "violation_location",
    "اسم النظام أو اللائحة المستند عليها": "regulation",
    "اسم النظام أو اللائحة المستند عليها (وفق محضر ضبط المخالفة)": "regulation",
    "تكرار الإحالة": "referral_repetition",
    "محرر المحضر": "report_editor",
    "الفرع": "branch",
    "تاريخ تحرير المحضر": "report_date",
    "تاريخ تحرير المحضر (MM/DD/YYYY)": "report_date",
    "نوع المخالفة": "violation_type",
    "تاريخ إشعار المنسوب له المخالفة": "notified_date",
    "تاريخ رد المنسوب له المخالفة": "person_response_date",
    "تاريخ إحالتها إلى القطاع المختص": "sector_referral_date",
    "تاريخ رد القطاع المختص": "sector_response_date",
    "تاريخ إحالتها الى الأمانة": "secretariat_referral_date",
    "تاريخ رد الأمانة": "secretariat_response_date",
    "حالة المخالفة": "violation_status",
    "حالة المخالفة (MM/DD/YYYY)": "violation_status",
    "حالة المعاملة": "transaction_status",
    "حالة المعاملة (MM/DD/YYYY)": "transaction_status",
    "تاريخ إصدار قرار المخالفة من اللجنة": "committee_decision_date",
    "تاريخ إصدار قرار المخالفة من اللجنة (MM/DD/YYYY)": "committee_decision_date",
    "ملاحظات": "notes",
    "خط العرض": "latitude",
    "خط الطول": "longitude",
    "منشئ المخالفة": "created_by",
    "آخر تعديل بواسطة": "updated_by",
    "بيانات المحضر": "report_data",
    "المحضر": "report_data",
}

MODEL_FIELDS = {f.name for f in Violation._meta.fields}
CREATE_FIELDS = MODEL_FIELDS - {"id", "created_at", "updated_at"}
UPDATE_FIELDS = CREATE_FIELDS - {"created_by"}


def home(request):
    return render(request, "main_dashboard/alex.html", {"violations": Violation.objects.all()})


def add_violation(request):
    return render(request, "main_dashboard/alex.html")


def edit_violation(request, pk):
    return render(request, "main_dashboard/alex.html")


def geocode_search(request):
    return JsonResponse({})


def serialize_violation(v):
    return {
        f.name: getattr(v, f.name)
        for f in Violation._meta.fields
    }


def translate_payload(data, allowed_fields):
    translated = {}
    unknown = []
    for key, value in data.items():
        if key == "id":
            continue
        field = FIELD_MAP.get(key, key)
        if field not in allowed_fields:
            unknown.append(key)
            continue
        translated[field] = value
    if unknown:
        raise ValueError("حقول غير مسموح بها: " + ", ".join(map(str, unknown)))
    return translated


def api_violations(request):
    # SERA_DB_CONNECTION_DIAGNOSTIC_V1
    import logging
    _sera_logger = logging.getLogger("django.request")
    _sera_logger.warning(
        "SERA_DB_DIAGNOSTIC vendor=%s engine=%s host=%s",
        connection.vendor,
        connection.settings_dict.get("ENGINE"),
        connection.settings_dict.get("HOST") or "(local)",
    )
    if request.method != "GET":
        return JsonResponse({"ok": False, "error": "Method not allowed"}, status=405)
    results = list(Violation.objects.values())
    return JsonResponse({"ok": True, "count": len(results), "results": results})


@csrf_exempt
def api_violation_create(request):
    if request.method != "POST":
        return JsonResponse({"ok": False, "error": "Method not allowed"}, status=405)
    try:
        data = json.loads(request.body or "{}")
        payload = translate_payload(data, CREATE_FIELDS)
        violation = Violation.objects.create(**payload)
        return JsonResponse({
            "ok": True,
            "result": serialize_violation(violation),
        }, status=201)
    except (json.JSONDecodeError, TypeError, ValueError) as exc:
        return JsonResponse({"ok": False, "error": str(exc)}, status=400)
    except Exception as exc:
        return JsonResponse({"ok": False, "error": str(exc)}, status=500)


@csrf_exempt
def api_violation_update(request, pk=None):
    if request.method not in {"PATCH", "PUT", "POST"}:
        return JsonResponse({"ok": False, "error": "Method not allowed"}, status=405)
    try:
        data = json.loads(request.body or "{}")
        v_id = pk or data.get("id")
        if not v_id:
            return JsonResponse({"ok": False, "error": "Missing violation id"}, status=400)

        violation = get_object_or_404(Violation, pk=v_id)
        payload = translate_payload(data, UPDATE_FIELDS)

        # آخر تعديل يُحفظ من الخادم حتى لا يعتمد على وقت الجهاز.
        payload["updated_at"] = timezone.now()
        if not payload.get("updated_by"):
            payload["updated_by"] = ""

        for field, value in payload.items():
            setattr(violation, field, value)
        violation.save()

        return JsonResponse({
            "ok": True,
            "result": serialize_violation(violation),
        })
    except (json.JSONDecodeError, TypeError, ValueError) as exc:
        return JsonResponse({"ok": False, "error": str(exc)}, status=400)
    except Exception as exc:
        return JsonResponse({"ok": False, "error": str(exc)}, status=500)
