import os

print("🔍 جاري البحث عن ملفات الـ HTML وتطبيق تنسيق الطباعة لصفحة واحدة A4...")

css_patch = """
<style id="a4-override">
@media print {
  @page {
    size: A4 portrait !important;
    margin: 3mm 5mm !important;
  }
  html, body {
    background: #ffffff !important;
    color: #10211e !important;
    font-size: 11px !important;
    line-height: 1.4 !important;
    margin: 0 !important;
    padding: 0 !important;
    height: auto !important;
  }
  /* إخفاء العناصر غير المطلوبة في الطباعة */
  header, nav, footer, .sidebar, button, .report-actions, .login-help, .nav-tabs {
    display: none !important;
  }
  /* منع انقسام كارت المحضر على صفحتين */
  #reportDoc, .report-card {
    width: 100% !important;
    max-width: 100% !important;
    margin: 0 !important;
    padding: 0 !important;
    border: none !important;
    box-shadow: none !important;
    page-break-inside: avoid !important;
    break-inside: avoid !important;
  }
  /* ضبط حقل النص لمنع تداخله */
  textarea, #reportText {
    width: 100% !important;
    height: auto !important;
    min-height: 70px !important;
    max-height: 130px !important;
    font-size: 11px !important;
    line-height: 1.5 !important;
    white-space: pre-wrap !important;
    word-break: break-word !important;
    resize: none !important;
    border: 1px solid #ccc !important;
  }
  /* تصغير التوقيع ليناسب الصفحة الأولى */
  #signatureCanvas, canvas, .signature-canvas {
    max-height: 55px !important;
    width: auto !important;
    object-fit: contain !important;
    display: block !important;
    margin: 4px auto !important;
  }
}
</style>
"""

updated = []

for root, dirs, files in os.walk('.'):
    for file in files:
        if file.endswith('.html'):
            path = os.path.join(root, file)
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                if 'reportDoc' in content or 'reportText' in content:
                    if '<style id="a4-override">' in content:
                        content = content.replace(content[content.find('<style id="a4-override">'):content.find('</style>', content.find('<style id="a4-override">'))+8], css_patch)
                    elif '</head>' in content:
                        content = content.replace('</head>', css_patch + '\n</head>')
                    else:
                        content = content + css_patch
                    
                    with open(path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    updated.append(path)
            except Exception as e:
                print(f"خطأ في قراءة {path}: {e}")

if updated:
    print("✅ تم التحديث بنجاح في الملفات التالية:")
    for u in updated:
        print(f"  - {u}")
else:
    print("⚠️ لم يتم العثور على ملفات HTML تحتوي على reportDoc.")
