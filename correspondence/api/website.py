"""
Website API endpoints for the Correspondence app
"""

import frappe
from frappe import _

@frappe.whitelist(allow_guest=True)
def submit_contact_form(name, email, company=None, message=None):
    """
    Handle contact form submission from the website
    
    Args:
        name: Contact name
        email: Contact email
        company: Company name (optional)
        message: Message content (optional)
    
    Returns:
        dict: Success response
    """
    try:
        # Validate required fields
        if not name or not email:
            frappe.throw(_("Name and Email are required"))
        
        # Validate email format
        if not frappe.utils.validate_email_address(email):
            frappe.throw(_("Invalid email address"))
        
        # Create a Lead or Communication record
        # You can customize this based on your needs
        
        # Option 1: Create a Lead (if CRM module is installed)
        try:
            lead = frappe.get_doc({
                "doctype": "Lead",
                "lead_name": name,
                "email_id": email,
                "company_name": company or "",
                "source": "Website Contact Form",
                "notes": message or ""
            })
            lead.insert(ignore_permissions=True)
            
            # Send notification email to admin
            send_notification_email(name, email, company, message)
            
            return {
                "success": True,
                "message": _("Thank you for contacting us! We'll get back to you soon."),
                "lead_id": lead.name
            }
        except Exception as e:
            # If Lead creation fails, create a Communication instead
            comm = frappe.get_doc({
                "doctype": "Communication",
                "communication_type": "Communication",
                "communication_medium": "Email",
                "sent_or_received": "Received",
                "subject": f"Website Contact Form - {name}",
                "sender": email,
                "content": f"""
                    <p><strong>Name:</strong> {name}</p>
                    <p><strong>Email:</strong> {email}</p>
                    <p><strong>Company:</strong> {company or 'Not provided'}</p>
                    <p><strong>Message:</strong></p>
                    <p>{message or 'No message provided'}</p>
                """
            })
            comm.insert(ignore_permissions=True)
            
            # Send notification email
            send_notification_email(name, email, company, message)
            
            return {
                "success": True,
                "message": _("Thank you for contacting us! We'll get back to you soon."),
                "communication_id": comm.name
            }
            
    except Exception as e:
        frappe.log_error(f"Contact form submission error: {str(e)}")
        return {
            "success": False,
            "message": _("An error occurred. Please try again later.")
        }


def send_notification_email(name, email, company, message):
    """
    Send notification email to admin when contact form is submitted
    
    Args:
        name: Contact name
        email: Contact email
        company: Company name
        message: Message content
    """
    try:
        # Get admin email from system settings
        admin_email = frappe.db.get_single_value("System Settings", "email_footer_address")
        
        if not admin_email:
            # Fallback to first System Manager
            admin_email = frappe.db.get_value("User", {"role": "System Manager"}, "email")
        
        if admin_email:
            frappe.sendmail(
                recipients=[admin_email],
                subject=f"New Website Contact Form Submission - {name}",
                message=f"""
                    <h3>New Contact Form Submission</h3>
                    <p><strong>Name:</strong> {name}</p>
                    <p><strong>Email:</strong> {email}</p>
                    <p><strong>Company:</strong> {company or 'Not provided'}</p>
                    <p><strong>Message:</strong></p>
                    <p>{message or 'No message provided'}</p>
                    <hr>
                    <p><small>Submitted from website contact form</small></p>
                """,
                now=True
            )
    except Exception as e:
        frappe.log_error(f"Failed to send notification email: {str(e)}")


@frappe.whitelist(allow_guest=True)
def get_website_stats():
    """
    Get website statistics for display
    
    Returns:
        dict: Website statistics
    """
    try:
        # You can customize these stats based on your actual data
        stats = {
            "uptime": "99.9%",
            "modules": "50+",
            "support": "24/7",
            "users": frappe.db.count("User", {"enabled": 1}),
            "companies": frappe.db.count("Company")
        }
        
        return {
            "success": True,
            "stats": stats
        }
    except Exception as e:
        frappe.log_error(f"Failed to get website stats: {str(e)}")
        return {
            "success": False,
            "message": str(e)
        }
