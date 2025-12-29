# 🚀 راهنمای آپلود پروژه به GitHub و بیلد خودکار APK

## مرحله 1️⃣: ایجاد ریپازیتوری در GitHub

1. به سایت [GitHub](https://github.com) بروید و لاگین کنید
2. روی دکمه **"New"** یا **"+"** در بالای صفحه کلیک کنید
3. **Repository name** را وارد کنید (مثلاً: `maya-app`)
4. **Public** یا **Private** را انتخاب کنید
5. **بدون** انتخاب کردن README یا .gitignore کلیک کنید روی **Create repository**

## مرحله 2️⃣: آپلود کد به GitHub

در ترمینال خود این دستورات را اجرا کنید:

```bash
# رفتن به پوشه پروژه
cd /Users/Night/ponisha

# مقداردهی اولیه Git
git init

# افزودن فایل‌ها
git add .

# کامیت اول
git commit -m "Initial commit - Maya Android App"

# اضافه کردن ریموت (آدرس ریپازیتوری خودتان را جایگزین کنید)
git remote add origin https://github.com/YOUR_USERNAME/maya-app.git

# تغییر نام برنچ به main
git branch -M main

# پوش کردن به GitHub
git push -u origin main
```

**نکته**: در خط `git remote add origin` آدرس ریپازیتوری خودتان را جایگزین کنید.

## مرحله 3️⃣: فعال‌سازی GitHub Actions

بعد از پوش کردن کد:

1. به ریپازیتوری خود در GitHub بروید
2. روی تب **"Actions"** کلیک کنید
3. اگر پیامی برای فعال‌سازی workflows دیدید، روی **"I understand my workflows, go ahead and enable them"** کلیک کنید
4. Workflow به صورت خودکار شروع به اجرا می‌کند

## مرحله 4️⃣: دانلود APK ساخته شده

### روش A: از بخش Actions
1. به تب **"Actions"** بروید
2. روی آخرین workflow اجرا شده کلیک کنید
3. در بخش **"Artifacts"** فایل `maya-apk-X` را دانلود کنید
4. فایل ZIP را باز کنید - APK شما آنجاست!

### روش B: اجرای دستی Workflow
1. به تب **"Actions"** بروید
2. از سمت چپ روی **"Build Android APK"** کلیک کنید
3. روی **"Run workflow"** کلیک کنید
4. **Branch** را انتخاب کنید (معمولاً `main`)
5. روی **"Run workflow"** سبز رنگ کلیک کنید
6. بعد از اتمام، APK را از Artifacts دانلود کنید

## مرحله 5️⃣: ایجاد Release (اختیاری)

برای ایجاد نسخه رسمی با لینک دانلود مستقیم:

```bash
# ایجاد tag
git tag v1.0.0

# پوش کردن tag
git push origin v1.0.0
```

این کار به صورت خودکار یک Release با فایل APK ایجاد می‌کند.

## ⏱️ زمان Build

- **اولین بار**: 30-45 دقیقه (دانلود SDK/NDK)
- **دفعات بعدی**: 10-20 دقیقه (با استفاده از cache)

## 🔍 مشاهده لاگ‌های Build

اگر build با خطا مواجه شد:

1. به تب **Actions** بروید
2. روی workflow شکست خورده کلیک کنید
3. روی **"build"** job کلیک کنید
4. لاگ‌ها را بررسی کنید

## 📱 نصب APK روی گوشی

1. فایل APK را روی گوشی اندروید منتقل کنید
2. در تنظیمات، **"نصب از منابع نامشخص"** را فعال کنید
3. روی فایل APK کلیک کنید و نصب را تایید کنید

## 🔐 تنظیمات امنیتی (برای Private Repository)

اگر ریپازیتوری شما Private است و می‌خواهید توکن و Chat ID را مخفی کنید:

1. به **Settings** → **Secrets and variables** → **Actions** بروید
2. روی **"New repository secret"** کلیک کنید
3. سکرت‌های زیر را اضافه کنید:
   - `BOT_TOKEN`: توکن تلگرام
   - `CHAT_ID`: آیدی عددی

سپس در `main.py` از متغیرهای محیطی استفاده کنید (نیاز به تغییر کد).

## 🆘 عیب‌یابی

### خطا: "Permission denied"
```bash
git config --global user.email "your-email@example.com"
git config --global user.name "Your Name"
```

### خطا: "Authentication failed"
از Personal Access Token استفاده کنید:
1. GitHub → Settings → Developer settings → Personal access tokens
2. Generate new token (classic)
3. مجوزهای `repo` را انتخاب کنید
4. Token را کپی کنید
5. هنگام پوش، به جای پسورد از token استفاده کنید

### Workflow اجرا نمی‌شود
- مطمئن شوید فایل در مسیر `.github/workflows/build-apk.yml` قرار دارد
- در Settings → Actions → General بررسی کنید که Actions فعال باشد

## 📋 دستورات مفید Git

```bash
# مشاهده وضعیت
git status

# افزودن تغییرات جدید
git add .
git commit -m "توضیحات تغییرات"
git push

# مشاهده لاگ
git log --oneline

# بازگشت به کامیت قبلی
git reset --hard HEAD~1
```

## ✅ چک‌لیست نهایی

- [ ] ریپازیتوری در GitHub ساخته شد
- [ ] کد به GitHub پوش شد
- [ ] Workflow در Actions فعال است
- [ ] Build با موفقیت تکمیل شد
- [ ] APK دانلود و تست شد
- [ ] مجوزها روی گوشی داده شد

---

**نکته مهم**: اولین build ممکن است تا 45 دقیقه طول بکشد. صبور باشید!

برای هر مشکل، لاگ‌های Actions را بررسی کنید یا سوال بپرسید.
