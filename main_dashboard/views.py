from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from urllib.parse import urlencode
from urllib.request import Request, urlopen
import json
from .models import Violation
from .forms import ViolationForm

def home(request):
    violations = Violation.objects.all()
    return render(
        request,
        "main_dashboard/alex.html",
        {"violations": violations}
    )

def add_violation(request):
    if request.method == 'POST':
        form = ViolationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = ViolationForm()
    return render(request, 'main_dashboard/add_violation.html', {'form': form})
def edit_violation(request, pk):
    violation = get_object_or_404(Violation, pk=pk)
    if request.method == 'POST':
        form = ViolationForm(request.POST, instance=violation)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = ViolationForm(instance=violation)
    return render(request, 'main_dashboard/add_violation.html', {'form': form})


def geocode_search(request):
    q = request.GET.get("q", "").strip()
    if not q:
        return JsonResponse({"results": []})

    params = urlencode({
        "format": "jsonv2",
        "limit": 5,
        "countrycodes": "sa",
        "accept-language": "ar",
        "q": q,
    })

    url = "https://nominatim.openstreetmap.org/search?" + params

    try:
        req = Request(
            url,
            headers={"User-Agent": "SERA-System/1.0"}
        )
        with urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode("utf-8"))

        results = [
            {
                "name": item.get("display_name", item.get("name", "")),
                "lat": item.get("lat"),
                "lon": item.get("lon"),
            }
            for item in data
        ]

        return JsonResponse({"results": results})

    except Exception as e:
        return JsonResponse(
            {"results": [], "error": "تعذر تنفيذ البحث"},
            status=502
        )
@csrf_exempt
@require_http_methods(["POST"])
def api_violation_create(request):
    try:
        payload = json.loads(request.body.decode("utf-8"))
    except Exception:
        return JsonResponse({"error": "بيانات غير صالحة"}, status=400)

    allowed = {
        f.name for f in Violation._meta.fields
        if f.name not in {"id", "created_at", "updated_at"}
    }

    data = {k: v for k, v in payload.items() if k in allowed}

    violation = Violation.objects.create(**data)

    return JsonResponse({
        "ok": True,
        "result": {
            f.name: getattr(violation, f.name)
            for f in Violation._meta.fields
        }
    }, status=201)


@csrf_exempt
@require_http_methods(["PATCH"])
def api_violation_update(request, pk):
    violation = get_object_or_404(Violation, pk=pk)

    try:
        payload = json.loads(request.body.decode("utf-8"))
    except Exception:
        return JsonResponse({"error": "بيانات غير صالحة"}, status=400)

    blocked = {"id", "created_at"}
    allowed = {
        f.name for f in Violation._meta.fields
        if f.name not in blocked
    }

    for key, value in payload.items():
        if key in allowed:
            setattr(violation, key, value)

    violation.save()

    return JsonResponse({
        "ok": True,
        "result": {
            f.name: getattr(violation, f.name)
            for f in Violation._meta.fields
        }
    })

def api_violations(request):
    from django.core.serializers.json import DjangoJSONEncoder

    rows = []
    for v in Violation.objects.all().order_by("-id"):
        data = {}
        for field in v._meta.fields:
            value = getattr(v, field.name, None)
            data[field.name] = value
        rows.append(data)

    return JsonResponse(
        {"count": len(rows), "results": rows},
        encoder=DjangoJSONEncoder
    )
