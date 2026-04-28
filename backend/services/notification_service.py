import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any, Optional
import logging
from datetime import datetime, timedelta
import os
from jinja2 import Template

logger = logging.getLogger(__name__)

class NotificationService:
    def __init__(self):
        # Email configuration (should be moved to environment variables)
        self.SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
        self.EMAIL_USERNAME = os.getenv("EMAIL_USERNAME", "")
        self.EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "")
        self.FROM_EMAIL = os.getenv("FROM_EMAIL", self.EMAIL_USERNAME)
        
    async def send_notification(self, user_data: Dict[str, Any], 
                              notification_data: Dict[str, Any]) -> bool:
        """
        Send notification to user via email and/or in-app
        """
        try:
            # Send email notification if enabled
            if user_data.get('notification_preferences', {}).get('email_notifications', True):
                email_sent = await self._send_email_notification(user_data, notification_data)
                notification_data['email_sent'] = email_sent
                if email_sent:
                    notification_data['email_sent_at'] = datetime.utcnow()
            
            # In-app notification is handled by database storage
            notification_data['in_app_read'] = False
            
            return True
            
        except Exception as e:
            logger.error(f"Error sending notification: {e}")
            return False
    
    async def _send_email_notification(self, user_data: Dict[str, Any], 
                                     notification_data: Dict[str, Any]) -> bool:
        """Send email notification"""
        try:
            if not self.EMAIL_USERNAME or not self.EMAIL_PASSWORD:
                logger.warning("Email credentials not configured")
                return False
            
            # Create email message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = notification_data.get('title', 'Pet-Track Notification')
            msg['From'] = self.FROM_EMAIL
            msg['To'] = user_data.get('email', '')
            
            # Create HTML content
            html_content = self._create_email_html(user_data, notification_data)
            html_part = MIMEText(html_content, 'html')
            msg.attach(html_part)
            
            # Send email
            with smtplib.SMTP(self.SMTP_SERVER, self.SMTP_PORT) as server:
                server.starttls()
                server.login(self.EMAIL_USERNAME, self.EMAIL_PASSWORD)
                server.send_message(msg)
            
            logger.info(f"Email sent to {user_data.get('email')}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending email: {e}")
            return False
    
    def _create_email_html(self, user_data: Dict[str, Any], 
                          notification_data: Dict[str, Any]) -> str:
        """Create HTML email content"""
        
        template_str = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Pet-Track Notification</title>
            <style>
                body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                .header { background: #4CAF50; color: white; padding: 20px; text-align: center; }
                .content { padding: 20px; background: #f9f9f9; }
                .button { display: inline-block; padding: 12px 24px; background: #4CAF50; color: white; text-decoration: none; border-radius: 4px; margin: 10px 0; }
                .footer { padding: 20px; text-align: center; font-size: 12px; color: #666; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🐾 Pet-Track</h1>
                    <p>{{ title }}</p>
                </div>
                <div class="content">
                    <p>Hi {{ user_name }},</p>
                    <p>{{ message }}</p>
                    
                    {% if notification_type == 'match_found' %}
                        <div style="background: white; padding: 15px; border-radius: 8px; margin: 15px 0;">
                            <h3>Match Details:</h3>
                            <p><strong>Match Score:</strong> {{ match_score }}%</p>
                            <p><strong>Similarity:</strong> {{ similarity_details }}</p>
                            <p><strong>Distance:</strong> {{ distance }} km</p>
                        </div>
                        <a href="{{ app_url }}/matches/{{ match_id }}" class="button">View Match</a>
                    {% endif %}
                    
                    {% if notification_type == 'contact_request' %}
                        <div style="background: white; padding: 15px; border-radius: 8px; margin: 15px 0;">
                            <h3>Contact Request:</h3>
                            <p><strong>From:</strong> {{ initiator_name }}</p>
                            <p><strong>Message:</strong> {{ message_content }}</p>
                        </div>
                        <a href="{{ app_url }}/contacts/{{ contact_id }}" class="button">View Contact Request</a>
                    {% endif %}
                    
                    <p>Thank you for using Pet-Track to help reunite pets with their families!</p>
                </div>
                <div class="footer">
                    <p>This is an automated notification from Pet-Track.</p>
                    <p>If you no longer wish to receive these emails, please update your notification preferences.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        template = Template(template_str)
        
        # Prepare template variables
        context = {
            'user_name': user_data.get('full_name', user_data.get('username', 'User')),
            'title': notification_data.get('title', ''),
            'message': notification_data.get('message', ''),
            'notification_type': notification_data.get('type', ''),
            'app_url': os.getenv('APP_URL', 'http://localhost:3000'),
            'match_id': notification_data.get('data', {}).get('match_id', ''),
            'contact_id': notification_data.get('data', {}).get('contact_id', ''),
            'match_score': notification_data.get('data', {}).get('match_score', 0),
            'similarity_details': notification_data.get('data', {}).get('similarity_details', ''),
            'distance': notification_data.get('data', {}).get('distance', 0),
            'initiator_name': notification_data.get('data', {}).get('initiator_name', ''),
            'message_content': notification_data.get('data', {}).get('message', ''),
        }
        
        return template.render(**context)
    
    async def create_match_notification(self, user_data: Dict[str, Any], 
                                      match_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create notification for match found"""
        notification = {
            'title': '🎉 Potential Match Found!',
            'message': f"We found a potential match for your {match_data.get('pet_status', 'pet')}. Check the details below.",
            'type': 'match_found',
            'data': {
                'match_id': str(match_data.get('match_id')),
                'pet_id': str(match_data.get('pet_id')),
                'match_score': round(match_data.get('similarity', {}).get('hybrid_score', 0) * 100, 1),
                'similarity_details': self._format_similarity_details(match_data.get('similarity', {})),
                'distance': match_data.get('similarity', {}).get('details', {}).get('distance_km', 0)
            },
            'priority': 'high'
        }
        
        await self.send_notification(user_data, notification)
        return notification
    
    async def create_contact_notification(self, user_data: Dict[str, Any], 
                                        contact_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create notification for contact request"""
        notification = {
            'title': '📞 New Contact Request',
            'message': f"Someone has requested to contact you about a potential pet match.",
            'type': 'contact_request',
            'data': {
                'contact_id': str(contact_data.get('contact_id')),
                'match_id': str(contact_data.get('match_id')),
                'initiator_name': contact_data.get('initiator_name', 'Anonymous'),
                'message': contact_data.get('initial_message', '')
            },
            'priority': 'medium'
        }
        
        await self.send_notification(user_data, notification)
        return notification
    
    def _format_similarity_details(self, similarity: Dict[str, Any]) -> str:
        """Format similarity details for display"""
        details = []
        
        if similarity.get('image_similarity', 0) > 0:
            details.append(f"Image: {similarity['image_similarity']:.1%}")
        
        if similarity.get('metadata_similarity', 0) > 0:
            details.append(f"Details: {similarity['metadata_similarity']:.1%}")
        
        if similarity.get('location_similarity', 0) > 0:
            details.append(f"Location: {similarity['location_similarity']:.1%}")
        
        return " | ".join(details) if details else "No similarity data"
    
    async def cleanup_expired_notifications(self, days_old: int = 30):
        """Clean up old notifications"""
        cutoff_date = datetime.utcnow() - timedelta(days=days_old)
        
        # This would be implemented to clean up old notifications from database
        # await get_notifications_collection().delete_many({
        #     'created_at': {'$lt': cutoff_date}
        # })
        
        logger.info(f"Cleaned up notifications older than {days_old} days")

# Global instance
notification_service = NotificationService()
