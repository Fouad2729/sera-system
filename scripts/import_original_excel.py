import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sera.settings")

import django
import openpyxl

django.setup()

from main_dashboard.models import Violation


EXCEL_FILE = os.path.join(BASE_DIR, "backup_original.xlsx")
SHEET_NAME = "متابعة المحاضر"


def clean(value):
    if value is None:
        return ""
    return str(value).strip()


FIELD_MAP = {
    "رقم المحضر": "violation_number",
    "المنسوب له المخالفة": "attributed_person",
    "موقع المخالفة (المنطقة، المدينة)": "violation_location",
    "اسم النظام أو اللائحة المستند عليها (وفق محضر ضبط المخالفة)": "regulation",
    "تكرار الإحالة": "referral_repetition",
    "محرر المحضر": "report_editor",
    "الفرع": "branch",
    "تاريخ تحرير المحضر (MM/DD/YYYY)": "report_date",
    "نوع المخالفة": "violation_type",
    "تاريخ إشعار المنسوب له المخالفة (MM/DD/YYYY)": "notified_date",
    "تاريخ رد المنسوب له المخالفة (MM/DD/YYYY)": "person_response_date",
    "تاريخ إحالتها إلى القطاع المختص  (MM/DD/YYYY)": "sector_referral_date",
    "تاريخ رد القطاع المختص (MM/DD/YYYY)": "sector_response_date",
    "تاريخ إحالتها الى الأمانة (MM/DD/YYYY)": "secretariat_referral_date",
    "تاريخ رد الأمانة (MM/DD/YYYY)": "secretariat_response_date",
    "حالة المخالفة (MM/DD/YYYY)": "violation_status",
    "حالة المعاملة (MM/DD/YYYY)": "transaction_status",
    "تاريخ إصدار قرار المخالفة من اللجنة (MM/DD/YYYY)": "committee_decision_date",
    "ملاحظات": "notes",
}


def main():
    print("Opening Excel:", EXCEL_FILE)

    wb = openpyxl.load_workbook(
        EXCEL_FILE,
        read_only=True,
        data_only=True,
    )

    ws = wb[SHEET_NAME]

    rows = ws.iter_rows(values_only=True)
    headers = [clean(x) for x in next(rows)]

    missing = [column for column in FIELD_MAP if column not in headers]

    if missing:
        raise RuntimeError(
            "Missing Excel columns:\n" + "\n".join(missing)
        )

    header_index = {name: i for i, name in enumerate(headers)}

    imported = 0
    skipped = 0

    for row in rows:
        if not row or not any(clean(x) for x in row):
            skipped += 1
            continue

        data = {}

        for excel_name, model_name in FIELD_MAP.items():
            index = header_index[excel_name]
            value = row[index] if index < len(row) else ""
            data[model_name] = clean(value)

        data["created_by"] = data["report_editor"]

        Violation.objects.create(**data)

        imported += 1

        if imported % 250 == 0:
            print(f"Imported: {imported}")

    print("----- IMPORT COMPLETE -----")
    print(f"Imported: {imported}")
    print(f"Skipped: {skipped}")
    print(f"Database total: {Violation.objects.count()}")


if __name__ == "__main__":
    main()
