import logging
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags

logger = logging.getLogger(__name__)


def get_site_url(request=None):
    if request:
        return f"{request.scheme}://{request.get_host()}"
    return getattr(settings, 'SITE_URL', 'https://surronbikesandparts.shop')


def send_order_placed_emails(order, request=None):
    """
    Sends order emails:
    1. User order confirmation -> sent ONLY to user (order.email).
    2. Admin new order alert   -> sent ONLY to admin (settings.ADMIN_EMAIL).
    """
    site_url = get_site_url(request)
    from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'Surron Bikes & Parts Canada <support@surronbikesandparts.shop>')
    admin_email = getattr(settings, 'ADMIN_EMAIL', 'admin@surronbikesandparts.shop')

    # 1. USER ORDER CONFIRMATION EMAIL (Users receive ONLY user emails)
    if order.email:
        try:
            user_subject = f"Order Confirmed: #{order.order_number} - Surron Bikes & Parts Canada"
            user_context = {
                'order': order,
                'site_url': site_url,
            }
            user_html = render_to_string('emails/user_order_confirmation.html', user_context)
            user_plain = strip_tags(user_html)

            user_msg = EmailMultiAlternatives(
                subject=user_subject,
                body=user_plain,
                from_email=from_email,
                to=[order.email],
            )
            user_msg.attach_alternative(user_html, "text/html")
            user_msg.send(fail_silently=False)
            logger.info(f"User confirmation email sent successfully to {order.email} for order {order.order_number}")
        except Exception as e:
            logger.error(f"Failed to send user order confirmation email to {order.email}: {e}")

    # 2. ADMIN NEW ORDER NOTIFICATION (Admin receives ONLY admin emails)
    if admin_email:
        try:
            admin_subject = f"[ADMIN ALERT] New Order Received #{order.order_number} (${order.total} CAD)"
            admin_context = {
                'order': order,
                'site_url': site_url,
            }
            admin_html = render_to_string('emails/admin_order_notification.html', admin_context)
            admin_plain = strip_tags(admin_html)

            admin_msg = EmailMultiAlternatives(
                subject=admin_subject,
                body=admin_plain,
                from_email=from_email,
                to=[admin_email],
            )
            admin_msg.attach_alternative(admin_html, "text/html")
            admin_msg.send(fail_silently=False)
            logger.info(f"Admin new order alert sent successfully to {admin_email} for order {order.order_number}")
        except Exception as e:
            logger.error(f"Failed to send admin order alert to {admin_email}: {e}")


def send_contact_form_emails(contact_message, request=None):
    """
    Sends contact emails:
    1. User auto-acknowledgement -> sent ONLY to user (contact_message.email).
    2. Admin new inquiry alert   -> sent ONLY to admin (settings.ADMIN_EMAIL).
    """
    site_url = get_site_url(request)
    from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'Surron Bikes & Parts Canada <support@surronbikesandparts.shop>')
    admin_email = getattr(settings, 'ADMIN_EMAIL', 'admin@surronbikesandparts.shop')

    # 1. USER CONTACT CONFIRMATION (User receives only user confirmation)
    if contact_message.email:
        try:
            user_subject = f"Inquiry Received: {contact_message.subject} - Surron Canada"
            user_context = {
                'contact_message': contact_message,
                'site_url': site_url,
            }
            user_html = render_to_string('emails/user_contact_confirmation.html', user_context)
            user_plain = strip_tags(user_html)

            user_msg = EmailMultiAlternatives(
                subject=user_subject,
                body=user_plain,
                from_email=from_email,
                to=[contact_message.email],
            )
            user_msg.attach_alternative(user_html, "text/html")
            user_msg.send(fail_silently=False)
            logger.info(f"User contact confirmation sent to {contact_message.email}")
        except Exception as e:
            logger.error(f"Failed to send user contact confirmation to {contact_message.email}: {e}")

    # 2. ADMIN INQUIRY ALERT (Admin receives only admin alert)
    if admin_email:
        try:
            admin_subject = f"[ADMIN INQUIRY] New Message from {contact_message.name}: {contact_message.subject}"
            admin_context = {
                'contact_message': contact_message,
                'site_url': site_url,
            }
            admin_html = render_to_string('emails/admin_contact_notification.html', admin_context)
            admin_plain = strip_tags(admin_html)

            admin_msg = EmailMultiAlternatives(
                subject=admin_subject,
                body=admin_plain,
                from_email=from_email,
                to=[admin_email],
                reply_to=[contact_message.email] if contact_message.email else None
            )
            admin_msg.attach_alternative(admin_html, "text/html")
            admin_msg.send(fail_silently=False)
            logger.info(f"Admin contact notification sent to {admin_email}")
        except Exception as e:
            logger.error(f"Failed to send admin contact notification to {admin_email}: {e}")


def send_user_welcome_email(user, request=None):
    """
    Sends welcome email to user upon registration (User receives ONLY user email).
    """
    if not user.email:
        return

    site_url = get_site_url(request)
    from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'Surron Bikes & Parts Canada <support@surronbikesandparts.shop>')

    try:
        subject = f"Welcome to Surron Bikes & Parts Canada, {user.first_name or user.username}!"
        context = {
            'user': user,
            'site_url': site_url,
        }
        html_content = render_to_string('emails/user_welcome.html', context)
        text_content = strip_tags(html_content)

        msg = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=from_email,
            to=[user.email],
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send(fail_silently=False)
        logger.info(f"User welcome email sent to {user.email}")
    except Exception as e:
        logger.error(f"Failed to send welcome email to {user.email}: {e}")
