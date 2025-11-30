# ERPNext Modern Website

A beautiful, modern, and bilingual (English/Arabic) website for your ERPNext system.

## Features

✨ **Modern Design**
- Premium glassmorphism effects
- Smooth gradients and animations
- Dark mode support
- Responsive layout for all devices

🌍 **Bilingual Support**
- Full English and Arabic support
- RTL (Right-to-Left) layout for Arabic
- Seamless language switching
- Localized content

🎨 **Beautiful UI**
- Hero section with animated gradients
- Feature cards with hover effects
- Module showcase
- Contact form
- Smooth scroll animations

## Files Structure

```
correspondence/
├── www/
│   └── index.html          # Main website page
└── public/
    ├── css/
    │   └── style.css       # All styles with dark mode & RTL support
    └── js/
        └── main.js         # Interactive features & language switching
```

## How to Access

The website is accessible at:
- **Root URL**: `http://your-site-url/index`
- **Direct access**: Navigate to your ERPNext site and go to `/index`

## Features Included

### 1. **Navigation**
- Sticky navbar with blur effect
- Theme toggle (Light/Dark mode)
- Language toggle (English/Arabic)
- Mobile-responsive menu

### 2. **Hero Section**
- Animated gradient background
- Call-to-action buttons
- Statistics display
- Smooth fade-in animations

### 3. **Features Section**
- 6 key feature cards
- Icon-based design
- Hover animations
- Responsive grid layout

### 4. **Modules Section**
- Showcase of ERP modules
- Color-coded module cards
- Feature lists for each module
- Covers: Accounting, Stock, Buying, Selling, HR, Manufacturing

### 5. **About Section**
- Company information
- Key benefits
- Dashboard preview mockup
- Feature highlights

### 6. **Contact Section**
- Working contact form
- Contact information cards
- Form validation
- Success/error messages

### 7. **Footer**
- Multi-column layout
- Quick links
- Social links ready
- Copyright information

## Customization

### Update Content

To update the website content, edit `/home/erp/frappe-bench/apps/correspondence/correspondence/www/index.html`

### Update Styles

To modify colors, fonts, or styling, edit `/home/erp/frappe-bench/apps/correspondence/correspondence/public/css/style.css`

### Update Functionality

To add or modify JavaScript features, edit `/home/erp/frappe-bench/apps/correspondence/correspondence/public/js/main.js`

### After Making Changes

Always rebuild assets and clear cache:

```bash
cd /home/erp/frappe-bench
bench build --app correspondence
bench clear-cache
```

## Color Scheme

The website uses a modern purple gradient theme:

- **Primary**: `#667eea` → `#764ba2`
- **Secondary**: `#f093fb` → `#f5576c`
- **Accent**: `#4facfe` → `#00f2fe`

You can customize these in the CSS variables at the top of `style.css`.

## Typography

- **English**: Inter font family
- **Arabic**: Cairo font family
- Both loaded from Google Fonts

## Browser Support

- ✅ Chrome/Edge (latest)
- ✅ Firefox (latest)
- ✅ Safari (latest)
- ✅ Mobile browsers

## Dark Mode

Dark mode is automatically saved in localStorage and persists across sessions. Users can toggle it using the sun/moon icon in the navigation bar.

## Language Switching

Language preference is saved in localStorage. The website automatically applies RTL layout for Arabic and adjusts all text content accordingly.

## Contact Form

The contact form currently logs data to the console. To make it functional:

1. Create a backend API endpoint in your ERPNext app
2. Update the `handleSubmit` method in `main.js` to send data to your endpoint
3. Configure email notifications as needed

## Performance

- Optimized CSS with minimal overhead
- Lazy-loaded animations
- Efficient JavaScript with class-based architecture
- Smooth 60fps animations

## Accessibility

- Semantic HTML5 elements
- ARIA labels for interactive elements
- Keyboard navigation support
- Screen reader friendly

## Mobile Responsive

The website is fully responsive with breakpoints at:
- Mobile: < 768px
- Tablet: 768px - 1024px
- Desktop: > 1024px

## Support

For issues or customization requests, please contact your development team.

---

**Built with ❤️ for ERPNext**
