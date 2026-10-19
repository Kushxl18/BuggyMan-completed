import json
import logging
import urllib.request
import urllib.error
from django.conf import settings

logger = logging.getLogger(__name__)

def send_verification_email(to_email: str, otp: str) -> bool:
    """
    Sends a 6-digit verification code email.
    Primary: Resend HTTPS API (runs over Port 443, allowed on all cloud hosts).
    Secondary fallback: Django SMTP backend.
    """
    resend_key = getattr(settings, 'RESEND_API_KEY', '').strip()
    from_email = getattr(settings, 'RESEND_FROM_EMAIL', 'BuggyMan <onboarding@resend.dev>').strip()

    subject = 'BuggyMan - Your 6-Digit Email Verification Code'
    html_content = f"""
    <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; max-width: 540px; margin: 0 auto; padding: 32px 24px; background-color: #0b1120; color: #f8fafc; border-radius: 16px; border: 1px solid #1e293b;">
        <div style="margin-bottom: 24px; text-align: center;">
            <h1 style="color: #38bdf8; font-size: 26px; margin: 0; font-weight: 800; letter-spacing: -0.5px;">BuggyMan</h1>
            <p style="color: #94a3b8; font-size: 13px; margin-top: 4px;">Developer Debugging & Challenge Arena</p>
        </div>
        <div style="background-color: #020617; border: 1px solid #1e293b; border-radius: 12px; padding: 24px; text-align: center;">
            <p style="color: #cbd5e1; font-size: 14px; margin-top: 0;">Here is your 6-digit verification code to complete your registration:</p>
            <div style="display: inline-block; padding: 14px 28px; background-color: #0e1726; border: 1px solid #06b6d4; border-radius: 10px; margin: 16px 0;">
                <span style="font-family: monospace; font-size: 32px; font-weight: 800; letter-spacing: 8px; color: #22d3ee;">{otp}</span>
            </div>
            <p style="color: #64748b; font-size: 12px; margin-bottom: 0;">This code will expire in <strong>10 minutes</strong>. Do not share this code with anyone.</p>
        </div>
        <p style="color: #475569; font-size: 11px; text-align: center; margin-top: 24px;">If you did not request this verification, please safely ignore this email.<br>&copy; BuggyMan Platform</p>
    </div>
    """

    if resend_key:
        try:
            req = urllib.request.Request(
                'https://api.resend.com/emails',
                data=json.dumps({
                    'from': from_email,
                    'to': [to_email],
                    'subject': subject,
                    'html': html_content,
                }).encode('utf-8'),
                headers={
                    'Authorization': f'Bearer {resend_key}',
                    'Content-Type': 'application/json',
                    'User-Agent': 'BuggyMan-Email/1.0'
                }
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                if resp.status in (200, 201):
                    logger.info(f"Verification email delivered to {to_email} via Resend HTTPS API")
                    return True
        except urllib.error.HTTPError as http_err:
            body = http_err.read().decode('utf-8', errors='ignore')
            logger.error(f"Resend API error ({http_err.code}): {body}")
            try:
                err_json = json.loads(body)
                err_msg = err_json.get('message', body)
            except Exception:
                err_msg = body
            raise Exception(f"Email service error: {err_msg}")
        except Exception as resend_err:
            logger.warning(f"Resend API call failed: {resend_err}")

    # Fallback to standard Django SMTP
    try:
        from django.core.mail import send_mail
        email_user = getattr(settings, 'EMAIL_HOST_USER', '')
        send_mail(
            subject,
            f"Your BuggyMan verification code is: {otp}\n\nThis code will expire in 10 minutes.\n\n- The BuggyMan Team",
            settings.DEFAULT_FROM_EMAIL or email_user,
            [to_email],
            fail_silently=False
        )
        logger.info(f"Verification email delivered to {to_email} via SMTP")
        return True
    except Exception as smtp_err:
        logger.error(f"SMTP delivery failed: {smtp_err}")
        raise Exception(f"Failed to deliver verification code: {smtp_err}")
