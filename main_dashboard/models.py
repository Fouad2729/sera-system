from django.db import models


class Violation(models.Model):
    # الحقول الأصلية من Excel
    violation_number = models.CharField("رقم المحضر", max_length=100, blank=True, default="")
    attributed_person = models.CharField("المنسوب له المخالفة", max_length=255, blank=True, default="")
    violation_location = models.TextField("موقع المخالفة", blank=True, default="")
    regulation = models.TextField(
        "اسم النظام أو اللائحة المستند عليها",
        blank=True,
        default="",
    )
    referral_repetition = models.CharField("تكرار الإحالة", max_length=100, blank=True, default="")
    report_editor = models.CharField("محرر المحضر", max_length=255, blank=True, default="")
    branch = models.CharField("الفرع", max_length=255, blank=True, default="")
    report_date = models.CharField("تاريخ تحرير المحضر", max_length=50, blank=True, default="")
    violation_type = models.CharField("نوع المخالفة", max_length=255, blank=True, default="")
    notified_date = models.CharField("تاريخ إشعار المنسوب له المخالفة", max_length=50, blank=True, default="")
    person_response_date = models.CharField("تاريخ رد المنسوب له المخالفة", max_length=50, blank=True, default="")
    sector_referral_date = models.CharField("تاريخ إحالتها إلى القطاع المختص", max_length=50, blank=True, default="")
    sector_response_date = models.CharField("تاريخ رد القطاع المختص", max_length=50, blank=True, default="")
    secretariat_referral_date = models.CharField("تاريخ إحالتها الى الأمانة", max_length=50, blank=True, default="")
    secretariat_response_date = models.CharField("تاريخ رد الأمانة", max_length=50, blank=True, default="")
    violation_status = models.CharField("حالة المخالفة", max_length=255, blank=True, default="")
    transaction_status = models.CharField("حالة المعاملة", max_length=255, blank=True, default="")
    committee_decision_date = models.CharField("تاريخ إصدار قرار المخالفة من اللجنة", max_length=50, blank=True, default="")
    notes = models.TextField("ملاحظات", blank=True, default="")

    # الموقع الجغرافي
    latitude = models.CharField("خط العرض", max_length=50, blank=True, default="")
    longitude = models.CharField("خط الطول", max_length=50, blank=True, default="")

    # التتبع والصلاحيات
    created_by = models.CharField("منشئ المخالفة", max_length=255, blank=True, default="")
    created_at = models.DateTimeField("تاريخ إنشاء السجل", auto_now_add=True)
    updated_by = models.CharField("آخر تعديل بواسطة", max_length=255, blank=True, default="")
    updated_at = models.DateTimeField("تاريخ آخر تعديل", null=True, blank=True)

    # المحضر
    report_data = models.JSONField("بيانات المحضر", null=True, blank=True)

    def __str__(self):
        return self.violation_number or self.attributed_person or f"مخالفة {self.pk}"
