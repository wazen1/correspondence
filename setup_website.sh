#!/bin/bash

# ERPNext Modern Website Setup Script
# This script sets up the modern website for your ERPNext instance

echo "=========================================="
echo "ERPNext Modern Website Setup"
echo "=========================================="
echo ""

# Navigate to bench directory
cd /home/erp/frappe-bench

echo "Step 1: Building assets..."
bench build --app correspondence

echo ""
echo "Step 2: Clearing cache..."
bench clear-cache

echo ""
echo "Step 3: Restarting bench (if needed)..."
# Uncomment the line below if you want to restart bench automatically
# bench restart

echo ""
echo "=========================================="
echo "✅ Setup Complete!"
echo "=========================================="
echo ""
echo "Your modern website is now ready!"
echo ""
echo "📍 Access your website at:"
echo "   http://localhost:8000/index"
echo "   OR"
echo "   http://site1.local:8000/index"
echo ""
echo "🎨 Features:"
echo "   ✓ Modern, premium design"
echo "   ✓ Dark mode toggle"
echo "   ✓ English/Arabic language support"
echo "   ✓ Fully responsive"
echo "   ✓ Smooth animations"
echo ""
echo "🔧 Customization:"
echo "   - HTML: apps/correspondence/correspondence/www/index.html"
echo "   - CSS:  apps/correspondence/correspondence/public/css/style.css"
echo "   - JS:   apps/correspondence/correspondence/public/js/main.js"
echo ""
echo "📚 Documentation: apps/correspondence/WEBSITE_README.md"
echo ""
echo "After making changes, run:"
echo "   bench build --app correspondence"
echo "   bench clear-cache"
echo ""
echo "=========================================="
