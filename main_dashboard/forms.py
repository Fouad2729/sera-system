from django import forms
from .models import Violation


class ViolationForm(forms.ModelForm):
    class Meta:
        model = Violation
        fields = [
            "violation_number",
            "attributed_person",
            "violation_location",
            "regulation",
            "referral_repetition",
            "report_editor",
            "branch",
            "report_date",
            "violation_type",
            "notified_date",
            "person_response_date",
            "sector_referral_date",
            "sector_response_date",
            "secretariat_referral_date",
            "secretariat_response_date",
            "violation_status",
            "transaction_status",
            "committee_decision_date",
            "notes",
            "latitude",
            "longitude",
            "created_by",
            "updated_by",
            "report_data",
        ]
