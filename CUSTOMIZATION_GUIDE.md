# Website Customization Guide

This guide will help you customize your ERPNext website to match your brand and requirements.

## Quick Customization Checklist

### 1. Update Company Information

**File**: `apps/correspondence/correspondence/www/index.html`

**What to change**:
- [ ] Company name (replace "ERPNext" with your company name)
- [ ] Contact email (search for "info@yourcompany.com")
- [ ] Phone number (search for "+1 (555) 123-4567")
- [ ] Location (search for "Your City, Country")
- [ ] Social media links (in footer)

**Example**:
```html
<!-- Find this line -->
<p>info@yourcompany.com</p>

<!-- Change to -->
<p>contact@mycompany.com</p>
```

### 2. Change Colors & Branding

**File**: `apps/correspondence/correspondence/public/css/style.css`

**Lines 6-10** - Update primary colors:
```css
:root {
    /* Change these colors to match your brand */
    --primary: #667eea;        /* Main brand color */
    --primary-dark: #5568d3;   /* Darker shade */
    --secondary: #764ba2;      /* Secondary color */
    --accent: #f093fb;         /* Accent color */
}
```

**Popular color schemes**:

**Blue Theme**:
```css
--primary: #0066ff;
--primary-dark: #0052cc;
--secondary: #00b8d4;
--accent: #00e5ff;
```

**Green Theme**:
```css
--primary: #00c853;
--primary-dark: #00a344;
--secondary: #64dd17;
--accent: #76ff03;
```

**Orange Theme**:
```css
--primary: #ff6d00;
--primary-dark: #e65100;
--secondary: #ff9100;
--accent: #ffab00;
```

### 3. Update Logo

**Option A - Text Logo** (Current):
The logo is currently SVG-based. To change the text:

**File**: `apps/correspondence/correspondence/www/index.html`

**Line 22** - Update logo text:
```html
<span class="logo-text" data-en="Your Company" data-ar="شركتك">Your Company</span>
```

**Option B - Image Logo**:
1. Add your logo image to: `apps/correspondence/correspondence/public/images/logo.png`
2. Replace the SVG logo with:
```html
<div class="logo">
    <img src="/assets/correspondence/images/logo.png" alt="Company Logo" style="height: 40px;">
    <span class="logo-text" data-en="Your Company" data-ar="شركتك">Your Company</span>
</div>
```

### 4. Update Hero Section

**File**: `apps/correspondence/correspondence/www/index.html`

**Lines 75-82** - Update main heading and subtitle:
```html
<h1 class="hero-title" data-en="Your Custom Heading" data-ar="عنوانك المخصص">
    Your Custom Heading
</h1>
<p class="hero-subtitle" data-en="Your custom description" data-ar="وصفك المخصص">
    Your custom description
</p>
```

**Lines 90-102** - Update statistics:
```html
<div class="stat-number">99.9%</div>
<div class="stat-label" data-en="Your Metric" data-ar="مقياسك">Your Metric</div>
```

### 5. Update Features

**File**: `apps/correspondence/correspondence/www/index.html`

**Lines 120-180** - Each feature card follows this structure:
```html
<div class="feature-card">
    <div class="feature-icon">
        <!-- Change icon SVG or use emoji -->
        📊
    </div>
    <h3 class="feature-title" data-en="Feature Name" data-ar="اسم الميزة">Feature Name</h3>
    <p class="feature-description" data-en="Description" data-ar="الوصف">
        Description
    </p>
</div>
```

### 6. Update Modules

**File**: `apps/correspondence/correspondence/www/index.html`

**Lines 200-280** - Each module card:
```html
<div class="module-card">
    <div class="module-header">
        <div class="module-icon" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
            📊  <!-- Change emoji icon -->
        </div>
        <h3 data-en="Module Name" data-ar="اسم الوحدة">Module Name</h3>
    </div>
    <ul class="module-features">
        <li data-en="Feature 1" data-ar="ميزة 1">Feature 1</li>
        <li data-en="Feature 2" data-ar="ميزة 2">Feature 2</li>
    </ul>
</div>
```

### 7. Add Your Own Images

Create the images directory:
```bash
mkdir -p /home/erp/frappe-bench/apps/correspondence/correspondence/public/images
```

Add images and reference them:
```html
<img src="/assets/correspondence/images/your-image.jpg" alt="Description">
```

### 8. Update Fonts

**File**: `apps/correspondence/correspondence/www/index.html`

**Lines 10-12** - Change Google Fonts:
```html
<link href="https://fonts.googleapis.com/css2?family=YourFont:wght@300;400;600;700&display=swap" rel="stylesheet">
```

**File**: `apps/correspondence/correspondence/public/css/style.css`

**Lines 30-31** - Update font variables:
```css
--font-primary: 'YourFont', sans-serif;
--font-arabic: 'YourArabicFont', sans-serif;
```

### 9. Customize Contact Form

**File**: `apps/correspondence/correspondence/public/js/main.js`

**Lines 250-280** - Update form submission handler:

To connect to a real backend:
```javascript
async handleSubmit(e) {
    e.preventDefault();
    const form = e.target;
    const formData = new FormData(form);
    const data = Object.fromEntries(formData);

    try {
        // Send to your ERPNext backend
        const response = await fetch('/api/method/correspondence.api.submit_contact_form', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });
        
        if (response.ok) {
            this.showMessage('success', this.getSuccessMessage());
            form.reset();
        }
    } catch (error) {
        this.showMessage('error', this.getErrorMessage());
    }
}
```

### 10. Add Google Analytics

**File**: `apps/correspondence/correspondence/www/index.html`

Add before closing `</head>` tag:
```html
<!-- Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id=GA_MEASUREMENT_ID"></script>
<script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){dataLayer.push(arguments);}
    gtag('js', new Date());
    gtag('config', 'GA_MEASUREMENT_ID');
</script>
```

## After Making Changes

Always run these commands:

```bash
cd /home/erp/frappe-bench

# Build assets
bench build --app correspondence

# Clear cache
bench clear-cache

# If needed, restart bench
bench restart
```

## Common Customizations

### Remove Dark Mode Toggle

**File**: `apps/correspondence/correspondence/www/index.html`

Remove lines 37-44 (theme toggle button)

### Remove Language Toggle

**File**: `apps/correspondence/correspondence/www/index.html`

Remove lines 46-48 (language toggle button)

### Change Default Language to Arabic

**File**: `apps/correspondence/correspondence/public/js/main.js`

**Line 41** - Change:
```javascript
this.currentLang = localStorage.getItem('language') || 'ar'; // Changed from 'en'
```

### Change Default Theme to Dark

**File**: `apps/correspondence/correspondence/public/js/main.js`

**Line 6** - Change:
```javascript
this.theme = localStorage.getItem('theme') || 'dark'; // Changed from 'light'
```

### Add More Sections

Copy an existing section and modify:
```html
<section id="new-section" class="new-section">
    <div class="container">
        <div class="section-header">
            <h2 class="section-title" data-en="Section Title" data-ar="عنوان القسم">Section Title</h2>
            <p class="section-subtitle" data-en="Subtitle" data-ar="العنوان الفرعي">Subtitle</p>
        </div>
        <!-- Your content here -->
    </div>
</section>
```

Add corresponding CSS:
```css
.new-section {
    padding: var(--spacing-2xl) 0;
    background: var(--bg-secondary);
}
```

## Translation Tips

Every text element should have both English and Arabic:
```html
<element data-en="English Text" data-ar="النص العربي">English Text</element>
```

The JavaScript automatically switches based on selected language.

## Need Help?

- Check the main README: `apps/correspondence/WEBSITE_README.md`
- Review the code comments in each file
- Test changes in developer mode before production

## Backup Before Major Changes

```bash
cd /home/erp/frappe-bench/apps/correspondence
git add .
git commit -m "Backup before customization"
```

---

**Happy Customizing! 🎨**
