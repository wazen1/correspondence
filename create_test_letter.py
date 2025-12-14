#!/usr/bin/env python3
"""
Script to create a test Incoming Letter for demonstrating the View and Assign feature
"""

import frappe
from frappe.utils import today

def create_test_incoming_letter():
    """Create a test incoming letter with sample data"""
    
    # Create new Incoming Letter
    doc = frappe.new_doc("Incoming Letter")
    
    # Set basic details
    doc.date_received = today()
    doc.priority = "High"
    doc.status = "New"
    doc.sender = "وزارة التعليم العالي"
    doc.sender_organization = "Ministry of Higher Education"
    
    # Get first available department
    departments = frappe.get_all("Department", limit=1)
    if departments:
        doc.recipient_department = departments[0].name
        doc.department = departments[0].name
    
    # Set content
    doc.subject = "طلب معلومات عن البرامج الأكاديمية للعام الدراسي القادم"
    doc.summary = """
    <p>السلام عليكم ورحمة الله وبركاته،</p>
    
    <p>نتقدم إليكم بطلب الحصول على معلومات تفصيلية عن البرامج الأكاديمية المتاحة للعام الدراسي القادم 2025-2026.</p>
    
    <p>نرجو منكم تزويدنا بالمعلومات التالية:</p>
    <ul>
        <li>قائمة بجميع البرامج الأكاديمية المتاحة</li>
        <li>شروط القبول لكل برنامج</li>
        <li>الرسوم الدراسية</li>
        <li>مواعيد التسجيل</li>
    </ul>
    
    <p>نأمل الرد في أقرب وقت ممكن.</p>
    
    <p>وتفضلوا بقبول فائق الاحترام والتقدير.</p>
    """
    
    # Save the document
    doc.insert(ignore_permissions=True)
    
    print(f"\n✅ تم إنشاء رسالة واردة تجريبية بنجاح!")
    print(f"📧 رقم الرسالة: {doc.name}")
    print(f"📅 تاريخ الاستلام: {doc.date_received}")
    print(f"👤 المرسل: {doc.sender}")
    print(f"📝 الموضوع: {doc.subject}")
    print(f"⚡ الأولوية: {doc.priority}")
    print(f"📊 الحالة: {doc.status}")
    print(f"\n🔗 رابط الرسالة: http://localhost:8000/app/incoming-letter/{doc.name}")
    print(f"\n💡 الآن يمكنك:")
    print(f"   1. فتح الرسالة من الرابط أعلاه")
    print(f"   2. النقر على زر 'عرض وتعيين' من قائمة 'الإجراءات'")
    print(f"   3. تجربة تعيين الرسالة لمستخدم")
    
    return doc.name

if __name__ == "__main__":
    frappe.init(site="site1.local")
    frappe.connect()
    
    try:
        letter_name = create_test_incoming_letter()
        frappe.db.commit()
    except Exception as e:
        print(f"\n❌ حدث خطأ: {str(e)}")
        frappe.db.rollback()
    finally:
        frappe.destroy()
