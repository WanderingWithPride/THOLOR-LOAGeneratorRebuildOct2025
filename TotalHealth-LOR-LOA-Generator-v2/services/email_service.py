"""
Email Service - Total Health Conferencing
SMTP email sending for LOA/LOR delivery with tracking
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from typing import List, Optional, Tuple
from io import BytesIO
from datetime import datetime
import streamlit as st


# ============================================================================
# EMAIL CONFIGURATION
# ============================================================================

class EmailConfig:
    """Email configuration from Streamlit secrets"""

    @staticmethod
    def get_smtp_config() -> dict:
        """
        Get SMTP configuration from secrets

        Returns:
            Dictionary with SMTP settings
        """
        try:
            return {
                'server': st.secrets.get('smtp_server', 'smtp.gmail.com'),
                'port': st.secrets.get('smtp_port', 587),
                'username': st.secrets.get('smtp_username', ''),
                'password': st.secrets.get('smtp_password', ''),
                'from_email': st.secrets.get('smtp_from_email', ''),
                'from_name': st.secrets.get('smtp_from_name', 'Total Health Conferencing'),
            }
        except Exception:
            # Return defaults if secrets not configured
            return {
                'server': 'smtp.gmail.com',
                'port': 587,
                'username': '',
                'password': '',
                'from_email': '',
                'from_name': 'Total Health Conferencing',
            }

    @staticmethod
    def is_configured() -> bool:
        """Check if email is configured"""
        config = EmailConfig.get_smtp_config()
        return bool(config['username'] and config['password'] and config['from_email'])


# ============================================================================
# EMAIL TEMPLATES
# ============================================================================

class EmailTemplates:
    """Professional email templates for document delivery"""

    @staticmethod
    def get_lor_template(company_name: str, event_name: str) -> Tuple[str, str]:
        """
        Get email template for LOR delivery

        Args:
            company_name: Company name
            event_name: Event name

        Returns:
            Tuple of (subject, body_html)
        """
        subject = f"Letter of Recognition - {event_name}"

        body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #013955;">Letter of Recognition</h2>

                <p>Dear {company_name} Team,</p>

                <p>
                    Thank you for your interest in <strong>{event_name}</strong>.
                    We are pleased to provide you with our Letter of Recognition (LOR).
                </p>

                <p>
                    Please find attached:
                </p>
                <ul>
                    <li>Letter of Recognition (PDF)</li>
                    <li>Letter of Recognition (DOCX - editable)</li>
                </ul>

                <p>
                    If you have any questions or need additional information, please don't hesitate to contact us.
                </p>

                <p style="margin-top: 30px;">
                    Best regards,<br>
                    <strong>Total Health Conferencing</strong><br>
                    <a href="mailto:sarah@totalhealthconferencing.com">sarah@totalhealthconferencing.com</a><br>
                    Phone: (561) 237-2845
                </p>

                <hr style="margin-top: 40px; border: none; border-top: 1px solid #ddd;">
                <p style="font-size: 12px; color: #666;">
                    Total Health Information Services, LLC.<br>
                    20423 State Road 7, F6-496, Boca Raton FL 33498
                </p>
            </div>
        </body>
        </html>
        """

        return subject, body

    @staticmethod
    def get_loa_template(company_name: str, event_name: str) -> Tuple[str, str]:
        """
        Get email template for LOA delivery

        Args:
            company_name: Company name
            event_name: Event name

        Returns:
            Tuple of (subject, body_html)
        """
        subject = f"Letter of Agreement - {event_name}"

        body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #013955;">Letter of Agreement</h2>

                <p>Dear {company_name} Team,</p>

                <p>
                    Thank you for choosing to participate in <strong>{event_name}</strong>.
                    We are pleased to provide you with our Letter of Agreement (LOA).
                </p>

                <p>
                    Please find attached:
                </p>
                <ul>
                    <li>Letter of Agreement (PDF)</li>
                    <li>Letter of Agreement (DOCX - editable)</li>
                </ul>

                <p>
                    <strong>Next Steps:</strong>
                </p>
                <ol>
                    <li>Review the attached Letter of Agreement</li>
                    <li>Sign and return a copy for our records</li>
                    <li>We will send payment instructions once the signed agreement is received</li>
                </ol>

                <p>
                    If you have any questions or need modifications, please contact us immediately.
                </p>

                <p style="margin-top: 30px;">
                    Best regards,<br>
                    <strong>Total Health Conferencing</strong><br>
                    <a href="mailto:sarah@totalhealthconferencing.com">sarah@totalhealthconferencing.com</a><br>
                    Phone: (561) 237-2845
                </p>

                <hr style="margin-top: 40px; border: none; border-top: 1px solid #ddd;">
                <p style="font-size: 12px; color: #666;">
                    Total Health Information Services, LLC.<br>
                    20423 State Road 7, F6-496, Boca Raton FL 33498
                </p>
            </div>
        </body>
        </html>
        """

        return subject, body


# ============================================================================
# EMAIL SENDER
# ============================================================================

class EmailSender:
    """
    Handles email sending with SMTP

    Supports:
    - HTML emails
    - Attachments (PDF, DOCX)
    - CC/BCC
    - Error handling
    """

    @staticmethod
    def send_document(
        to_email: str,
        company_name: str,
        event_name: str,
        document_type: str,
        docx_buffer: BytesIO,
        pdf_buffer: BytesIO,
        cc: Optional[List[str]] = None,
        bcc: Optional[List[str]] = None,
    ) -> Tuple[bool, str]:
        """
        Send LOA or LOR via email with attachments

        Args:
            to_email: Recipient email
            company_name: Company name
            event_name: Event name
            document_type: "LOR" or "LOA"
            docx_buffer: DOCX file buffer
            pdf_buffer: PDF file buffer
            cc: List of CC emails
            bcc: List of BCC emails

        Returns:
            Tuple of (success, message)
        """
        # Check if email is configured
        if not EmailConfig.is_configured():
            return False, "Email is not configured. Please add SMTP settings to secrets.toml"

        config = EmailConfig.get_smtp_config()

        try:
            # Get email template
            if document_type == "LOA":
                subject, body_html = EmailTemplates.get_loa_template(company_name, event_name)
            else:
                subject, body_html = EmailTemplates.get_lor_template(company_name, event_name)

            # Create message
            msg = MIMEMultipart('mixed')
            msg['Subject'] = subject
            msg['From'] = f"{config['from_name']} <{config['from_email']}>"
            msg['To'] = to_email

            if cc:
                msg['Cc'] = ', '.join(cc)
            if bcc:
                msg['Bcc'] = ', '.join(bcc)

            # Add HTML body
            html_part = MIMEText(body_html, 'html')
            msg.attach(html_part)

            # Add PDF attachment
            pdf_buffer.seek(0)
            pdf_attachment = MIMEApplication(pdf_buffer.read(), _subtype='pdf')
            pdf_attachment.add_header('Content-Disposition', 'attachment',
                                     filename=f'{document_type}_{company_name.replace(" ", "_")}.pdf')
            msg.attach(pdf_attachment)

            # Add DOCX attachment
            docx_buffer.seek(0)
            docx_attachment = MIMEApplication(docx_buffer.read(),
                                            _subtype='vnd.openxmlformats-officedocument.wordprocessingml.document')
            docx_attachment.add_header('Content-Disposition', 'attachment',
                                      filename=f'{document_type}_{company_name.replace(" ", "_")}.docx')
            msg.attach(docx_attachment)

            # Build recipient list
            recipients = [to_email]
            if cc:
                recipients.extend(cc)
            if bcc:
                recipients.extend(bcc)

            # Send email
            with smtplib.SMTP(config['server'], config['port']) as server:
                server.starttls()
                server.login(config['username'], config['password'])
                server.send_message(msg)

            return True, f"Email sent successfully to {to_email}"

        except smtplib.SMTPAuthenticationError:
            return False, "SMTP authentication failed. Please check username/password."
        except smtplib.SMTPException as e:
            return False, f"SMTP error: {str(e)}"
        except Exception as e:
            return False, f"Failed to send email: {str(e)}"

    @staticmethod
    def send_bulk_emails(
        recipients: List[dict],
        document_type: str,
    ) -> Tuple[int, int, List[str]]:
        """
        Send emails to multiple recipients

        Args:
            recipients: List of dicts with keys: email, company_name, event_name, docx_buffer, pdf_buffer
            document_type: "LOR" or "LOA"

        Returns:
            Tuple of (success_count, error_count, error_messages)
        """
        success_count = 0
        error_count = 0
        errors = []

        for recipient in recipients:
            success, message = EmailSender.send_document(
                to_email=recipient['email'],
                company_name=recipient['company_name'],
                event_name=recipient['event_name'],
                document_type=document_type,
                docx_buffer=recipient['docx_buffer'],
                pdf_buffer=recipient['pdf_buffer'],
            )

            if success:
                success_count += 1
            else:
                error_count += 1
                errors.append(f"{recipient['email']}: {message}")

        return success_count, error_count, errors


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def is_email_enabled() -> bool:
    """Check if email functionality is available"""
    return EmailConfig.is_configured()


def get_email_status() -> str:
    """Get email configuration status message"""
    if EmailConfig.is_configured():
        config = EmailConfig.get_smtp_config()
        return f"✅ Email configured ({config['from_email']})"
    else:
        return "⚠️ Email not configured (add SMTP settings to secrets.toml)"
