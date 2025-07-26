#!/usr/bin/env python3
"""
Test script for email functionality with Amazon SES
"""

import asyncio
import os
from all_workflows import (
    send_email_draft, 
    EmailDraft,
    AutomationLevel
)

async def test_email_functionality():
    """Test the email functionality"""
    
    print("🧪 Testing Email Functionality")
    print("=" * 50)
    
    # Check if AWS credentials are available
    if not os.getenv('AWS_ACCESS_KEY_ID') and not os.getenv('AWS_PROFILE'):
        print("❌ AWS credentials not found")
        print("   Set AWS credentials or use AWS_PROFILE")
        return
    
    print("✅ AWS credentials found")
    
    # Create test email draft
    email_draft = EmailDraft(
        subject="Test Email from Upsell Workflow",
        body="""
Dear Customer,

This is a test email from the upsell workflow system.

We've detected increased usage in your account and would like to discuss upgrade opportunities.

Best regards,
Your Account Team
        """.strip(),
        recipient="test@example.com",  # Replace with a real email for testing
        cc_list=[],
        attachments=[],
        send_date=None
    )
    
    print(f"📧 Test Email Draft:")
    print(f"   To: {email_draft.recipient}")
    print(f"   Subject: {email_draft.subject}")
    print(f"   Body: {email_draft.body[:100]}...")
    
    try:
        print("\n📤 Sending email via SES...")
        
        # Send email
        success = await send_email_draft(
            email_draft=email_draft,
            automation_level=AutomationLevel.HYBRID
        )
        
        if success:
            print("✅ Email sent successfully!")
        else:
            print("❌ Email sending failed")
            
    except Exception as e:
        print(f"❌ Error sending email: {e}")
        print("   This might be due to:")
        print("   - SES not configured in the region")
        print("   - Email address not verified")
        print("   - SES sandbox mode restrictions")

if __name__ == "__main__":
    asyncio.run(test_email_functionality()) 