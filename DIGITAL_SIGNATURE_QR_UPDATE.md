# تحديثات التوقيع الرقمي ورمز الاستجابة السريعة (QR)
## Digital Signature & QR Code Updates

### 1. التوقيع الرقمي | Digital Signature

#### المشكلة السابقة | Previous Issue:
كان يظهر خطأ "No signature keys found" عند محاولة توقيع المستند.
The error "No signature keys found" was appearing when trying to sign a document.

#### الحل الجديد | New Solution:
تم إضافة زر جديد **"توليد مفاتيح التوقيع" (Generate Signature Keys)**.
A new button **"Generate Signature Keys"** has been added.

#### كيفية الاستخدام | How to Use:
1. افتح أي رسالة (واردة أو صادرة).
   Open any letter (incoming or outgoing).
2. من قائمة "الإجراءات" (Actions)، اضغط على **"توليد مفاتيح التوقيع" (Generate Signature Keys)**.
   From the "Actions" menu, click **"Generate Signature Keys"**.
3. وافق على رسالة التأكيد.
   Confirm the prompt.
4. ستظهر رسالة نجاح باللون الأخضر.
   A green success message will appear.
5. الآن يمكنك استخدام زر **"توقيع المستند" (Sign Document)** بنجاح.
   Now you can use the **"Sign Document"** button successfully.

---

### 2. رمز التتبع | Tracking QR Code

#### التغييرات | Changes:
- تم **إزالة** زر "مسح الباركود" (Scan Barcode) لعدم الحاجة إليه.
  The "Scan Barcode" button has been **removed** as it's not needed.
- تم **تحديث** زر QR Code ليصبح **"توليد QR للتتبع" (Generate Tracking QR)**.
  The QR Code button has been **updated** to **"Generate Tracking QR"**.

#### الوظيفة | Functionality:
- يقوم هذا الزر بتوليد رمز QR خاص يحتوي على بيانات تتبع الرسالة.
  This button generates a specific QR code containing letter tracking data.
- يتم حفظ الرمز تلقائياً في مرفقات الرسالة.
  The code is automatically saved in the letter's attachments.
- يتم عرض الرمز في حقل الصورة المخصص في النموذج.
  The code is displayed in the designated image field on the form.

---

### ملخص الأزرار الجديدة في قائمة الإجراءات:
### New Buttons Summary in Actions Menu:

1. **عرض وتعيين (View and Assign)**: لعرض التفاصيل وتكليف الموظفين.
2. **توليد مفاتيح التوقيع (Generate Signature Keys)**: (جديد ✨) لإنشاء مفاتيح التشفير الخاصة بك.
3. **توقيع المستند (Sign Document)**: لتوقيع الرسالة رقمياً (يتطلب توليد المفاتيح أولاً).
4. **توليد QR للتتبع (Generate Tracking QR)**: (محدث 🔄) لإنشاء رمز تتبع للرسالة.
