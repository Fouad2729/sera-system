import io
import os
import traceback
import pymupdf as fitz  # PyMuPDF
import arabic_reshaper
from bidi.algorithm import get_display
from django.conf import settings
from django.http import HttpResponse

def reshape_ar(text):
    if not text:
        return ""
    reshaped_text = arabic_reshaper.reshape(str(text))
    return get_display(reshaped_text)

def build_sera_violation_pdf(request, context_data=None):
    """
    توليد محضر ضبط المخالفة الرسمي بجودة أصلية 100%
    """
    try:
        template_path = os.path.join(settings.BASE_DIR, 'assets', 'pdf_templates', 'sera_template.pdf')
        font_path = os.path.join(settings.BASE_DIR, 'assets', 'fonts', 'Amiri-Regular.ttf')

        if not os.path.exists(template_path):
            return HttpResponse(f"<div dir='rtl'><h3>خطأ: ملف القالب غير موجود</h3><p>المسار المتوقع: <code>{template_path}</code></p></div>", status=500)

        if not os.path.exists(font_path):
            return HttpResponse(f"<div dir='rtl'><h3>خطأ: ملف الخط العربي غير موجود</h3><p>المسار المتوقع: <code>{font_path}</code></p></div>", status=500)

        doc = fitz.open(template_path)
        page_1 = doc[0]
        page_1.insert_font(fontname="amiri", fontfile=font_path)

        # استخراج البيانات إما من context_data أو قيم تجريبية
        data = context_data or {}
        unified_num = data.get('unified_num', '7036280696')
        company_name = data.get('company_name', 'شركة أمالا المستدامة للطاقة (ASCE)')
        violation_date = data.get('violation_date', 'الخميس 16 أبريل 2026م الساعة 11:15 ص')

        # إسقاط النصوص فوق القالب الأصلي بدقة
        page_1.insert_text(fitz.Point(340, 275), reshape_ar(unified_num), fontname="amiri", fontsize=10, color=(0, 0, 0))
        page_1.insert_text(fitz.Point(390, 275), reshape_ar(company_name), fontname="amiri", fontsize=9.5, color=(0, 0, 0))
        page_1.insert_text(fitz.Point(320, 390), reshape_ar(violation_date), fontname="amiri", fontsize=9.5, color=(0, 0, 0))

        # الصفحة الثانية
        if len(doc) > 1:
            page_2 = doc[1]
            page_2.insert_font(fontname="amiri", fontfile=font_path)
            inspector_name = data.get('inspector_name', 'حمدان وصل الله الجهني')
            page_2.insert_text(fitz.Point(430, 840), reshape_ar(inspector_name), fontname="amiri", fontsize=10.5, color=(0, 0, 0))

        buffer = io.BytesIO()
        doc.save(buffer)
        doc.close()
        buffer.seek(0)

        response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = 'inline; filename="sera_violation_report.pdf"'
        return response

    except Exception:
        err = traceback.format_exc()
        return HttpResponse(f"<div dir='rtl'><h3>تفاصيل الخطأ أثناء معالجة الـ PDF:</h3><pre>{err}</pre></div>", status=500)
