# ميزة عرض وتعيين الرسائل
## View and Assign Letters Feature

### نظرة عامة | Overview

تم إضافة ميزة جديدة لنظام المراسلات تسمح بعرض تفاصيل الرسالة وتعيينها لمستخدم معين من خلال نافذة حوار واحدة.

A new feature has been added to the correspondence system that allows viewing letter details and assigning them to a user through a single dialog window.

---

## المميزات | Features

### 1. زر "عرض وتعيين" | "View and Assign" Button

- **الموقع | Location**: يظهر الزر في قائمة "الإجراءات" (Actions) في نموذج الرسالة
- **متاح لـ | Available for**: 
  - الرسائل الواردة (Incoming Letters)
  - الرسائل الصادرة (Outgoing Letters)

### 2. نافذة العرض | Display Dialog

تعرض النافذة المعلومات التالية:

**للرسائل الواردة | For Incoming Letters:**
- رقم الرسالة (Letter Number)
- المرسل (Sender)
- منظمة المرسل (Sender Organization)
- تاريخ الاستلام (Date Received)
- الحالة (Status) مع ألوان مميزة
- الأولوية (Priority) مع ألوان مميزة
- القسم المستلم (Department)
- المعين حالياً (Currently Assigned To)
- الموضوع (Subject)
- الملخص (Summary)
- المرفقات (Attachments) مع روابط للتحميل

**للرسائل الصادرة | For Outgoing Letters:**
- رقم الرسالة (Letter Number)
- المستلم (Recipient)
- منظمة المستلم (Recipient Organization)
- تاريخ الإنشاء (Date Created)
- تاريخ الإرسال (Date Sent)
- الحالة (Status)
- الأولوية (Priority)
- القسم (Department)
- المعين حالياً (Currently Assigned To)
- الرسالة الواردة ذات الصلة (Related Incoming Letter)
- الموضوع (Subject)
- نص الرسالة (Body Text)
- المرفقات (Attachments)

### 3. قسم التعيين | Assignment Section

يتيح للمستخدم:
- **تعيين المستخدم | Assign User**: اختيار المستخدم المراد تعيين الرسالة له
- **تاريخ الاستحقاق | Due Date**: تحديد الموعد النهائي للمهمة
- **ملاحظة التعيين | Assignment Note**: إضافة ملاحظة اختيارية للمستخدم المعين

### 4. الإشعارات | Notifications

- يتم إنشاء إشعار تلقائي للمستخدم المعين
- يظهر التعيين في قائمة المهام الخاصة بالمستخدم
- رسالة تأكيد عند نجاح التعيين

---

## كيفية الاستخدام | How to Use

### الخطوات | Steps:

1. **فتح الرسالة | Open the Letter**
   - افتح رسالة واردة أو صادرة موجودة

2. **النقر على زر "عرض وتعيين" | Click "View and Assign" Button**
   - انقر على زر "عرض وتعيين" من قائمة "الإجراءات"

3. **مراجعة التفاصيل | Review Details**
   - راجع تفاصيل الرسالة المعروضة في النافذة

4. **تعيين الرسالة | Assign the Letter**
   - اختر المستخدم من حقل "معين إلى" (Assigned To)
   - حدد تاريخ الاستحقاق (اختياري)
   - أضف ملاحظة للمستخدم المعين (اختياري)

5. **حفظ التعيين | Save Assignment**
   - انقر على زر "تعيين" (Assign)
   - سيتم حفظ التعيين وإرسال إشعار للمستخدم

---

## التحديثات التقنية | Technical Updates

### الملفات المعدلة | Modified Files:

1. **incoming_letter.js**
   - إضافة زر "عرض وتعيين"
   - دالة `show_view_and_assign_dialog()`
   - دالة `get_letter_details_html()`

2. **outgoing_letter.js**
   - إضافة زر "عرض وتعيين"
   - دالة `show_view_and_assign_dialog_outgoing()`
   - دالة `get_letter_details_html_outgoing()`

3. **outgoing_letter.json**
   - إضافة حقول التعيين:
     - `assigned_to` (Link to User)
     - `due_date` (Date)
     - `sla_status` (Select)

4. **ar.csv** (الترجمات العربية)
   - إضافة ترجمات للنصوص الجديدة

### الحقول الجديدة | New Fields:

تم إضافة الحقول التالية للرسائل الصادرة:
- **Assigned To**: ربط بمستخدم
- **Due Date**: تاريخ الاستحقاق
- **SLA Status**: حالة اتفاقية مستوى الخدمة (للقراءة فقط)

---

## الألوان المستخدمة | Color Coding

### حالات الرسائل الواردة | Incoming Letter Status:
- **جديد (New)**: أزرق
- **قيد المعالجة (Under Process)**: برتقالي
- **في الانتظار (Waiting)**: أصفر
- **مكتمل (Completed)**: أخضر
- **مؤرشف (Archived)**: رمادي

### حالات الرسائل الصادرة | Outgoing Letter Status:
- **مسودة (Draft)**: رمادي
- **قيد المراجعة (Under Review)**: أزرق
- **موافق عليه (Approved)**: أخضر
- **مرسل (Sent)**: أخضر
- **تم التسليم (Delivered)**: أخضر
- **مؤرشف (Archived)**: رمادي

### الأولويات | Priority:
- **منخفض (Low)**: رمادي
- **متوسط (Medium)**: أزرق
- **عالي (High)**: برتقالي
- **عاجل (Urgent)**: أحمر

---

## ملاحظات | Notes

- الميزة متاحة فقط للرسائل المحفوظة (غير الجديدة)
- يتطلب صلاحيات مناسبة لتعيين الرسائل
- يتم تحديث حالة SLA تلقائياً بناءً على تاريخ الاستحقاق
- يمكن إعادة تعيين الرسالة لمستخدم آخر في أي وقت

---

## الدعم | Support

للمزيد من المعلومات أو الإبلاغ عن مشاكل، يرجى التواصل مع فريق الدعم.

For more information or to report issues, please contact the support team.
