from typing import Optional
import requests
from twilio.rest import Client
import os


class SMSService:
    def __init__(self):
        # Initialize Twilio client (you would need to set these environment variables)
        self.account_sid = os.getenv('TWILIO_ACCOUNT_SID', '')
        self.auth_token = os.getenv('TWILIO_AUTH_TOKEN', '')
        self.twilio_phone_number = os.getenv('TWILIO_PHONE_NUMBER', '')
        
        # Fallback to a mock service if Twilio credentials are not available
        if self.account_sid and self.auth_token:
            self.client = Client(self.account_sid, self.auth_token)
            self.use_twilio = True
        else:
            self.use_twilio = False
    
    def send_sms(self, to: str, message: str) -> bool:
        """
        Send SMS to a phone number
        """
        try:
            if self.use_twilio:
                # Use Twilio to send SMS
                self.client.messages.create(
                    body=message,
                    from_=self.twilio_phone_number,
                    to=to
                )
            else:
                # Mock implementation for development
                print(f"MOCK SMS sent to {to}: {message}")
            
            return True
        except Exception as e:
            print(f"Failed to send SMS: {e}")
            return False
    
    def send_ussd(self, phone_number: str, message: str) -> bool:
        """
        Send USSD message (simplified implementation)
        In practice, this would connect to a mobile network operator's USSD gateway
        """
        try:
            # Mock implementation for development
            print(f"MOCK USSD sent to {phone_number}: {message}")
            return True
        except Exception as e:
            print(f"Failed to send USSD: {e}")
            return False
    
    def receive_sms(self, from_number: str, message_body: str) -> dict:
        """
        Process incoming SMS messages
        This would typically be handled by a webhook endpoint
        """
        # Parse the message to extract feedback information
        feedback_data = self._parse_feedback_message(message_body)
        
        return {
            "from": from_number,
            "message": message_body,
            "parsed_feedback": feedback_data,
            "timestamp": "2023-01-01T00:00:00Z"  # In practice, use actual timestamp
        }
    
    def _parse_feedback_message(self, message: str) -> dict:
        """
        Parse feedback message to extract structured data
        This is a simple implementation - in practice, you might use NLP
        """
        # Simple keyword-based parsing
        keywords = {
            "shipment": "shipment_id",
            "delayed": "status",
            "missing": "status",
            "received": "status",
            "not received": "status",
            "damaged": "issue_type",
            "quantity": "quantity_issue"
        }
        
        parsed_data = {
            "keywords_found": [],
            "shipment_id": None,
            "status": None,
            "issue_type": None,
            "quantity_issue": None
        }
        
        message_lower = message.lower()
        
        # Extract potential shipment ID (assuming it's a number)
        import re
        shipment_ids = re.findall(r'\b\d{4,}\b', message)
        if shipment_ids:
            parsed_data["shipment_id"] = shipment_ids[0]
        
        # Check for keywords
        for keyword, field in keywords.items():
            if keyword in message_lower:
                parsed_data["keywords_found"].append(keyword)
                if field == "status":
                    parsed_data["status"] = keyword
                elif field == "issue_type":
                    parsed_data["issue_type"] = keyword
        
        return parsed_data


# Global instance
sms_service = SMSService()