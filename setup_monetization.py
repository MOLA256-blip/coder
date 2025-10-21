#!/usr/bin/env python
"""
Setup script to create sample monetization data
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'videostream.settings')
django.setup()

from videos.monetization_models import AdCampaign, Ad, SubscriptionPlan
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

def create_sample_data():
    print("Setting up VideoStream monetization...")
    
    # Create sample ad campaign
    campaign, created = AdCampaign.objects.get_or_create(
        name="Tech Products Campaign",
        defaults={
            'advertiser': 'TechCorp Inc.',
            'budget': 10000.00,
            'cost_per_view': 0.01,
            'cost_per_click': 0.05,
            'is_active': True,
            'end_date': timezone.now() + timedelta(days=30),
        }
    )
    print(f"Ad Campaign: {campaign.name}")
    
    # Create sample ads
    ads_data = [
        {
            'title': 'New Smartphone - Pre-roll',
            'ad_type': 'video_pre',
            'click_url': 'https://example.com/smartphone',
            'duration': 15,
        },
        {
            'title': 'Laptop Sale - Mid-roll',
            'ad_type': 'video_mid',
            'click_url': 'https://example.com/laptop',
            'duration': 20,
        },
        {
            'title': 'Tech Newsletter - Banner',
            'ad_type': 'banner',
            'click_url': 'https://example.com/newsletter',
            'duration': 0,
        },
    ]
    
    for ad_data in ads_data:
        ad, created = Ad.objects.get_or_create(
            campaign=campaign,
            title=ad_data['title'],
            defaults={
                'ad_type': ad_data['ad_type'],
                'click_url': ad_data['click_url'],
                'duration': ad_data['duration'],
                'is_active': True,
            }
        )
        print(f"Ad: {ad.title}")
    
    # Create subscription plans
    plans_data = [
        {
            'name': 'Basic',
            'description': 'Perfect for casual viewers',
            'price_monthly': 4.99,
            'price_yearly': 49.99,
            'features': ['Ad-free viewing', 'HD quality', 'Download videos'],
        },
        {
            'name': 'Pro',
            'description': 'For content creators',
            'price_monthly': 9.99,
            'price_yearly': 99.99,
            'features': ['Everything in Basic', 'Upload up to 10GB', 'Analytics dashboard', 'Priority support'],
        },
        {
            'name': 'Premium',
            'description': 'For professional creators',
            'price_monthly': 19.99,
            'price_yearly': 199.99,
            'features': ['Everything in Pro', 'Unlimited uploads', 'Advanced analytics', 'Custom branding', 'API access'],
        },
    ]
    
    for plan_data in plans_data:
        plan, created = SubscriptionPlan.objects.get_or_create(
            name=plan_data['name'],
            defaults=plan_data
        )
        print(f"Subscription Plan: {plan.name}")
    
    print("\nMonetization setup complete!")
    print("\nAvailable features:")
    print("- Video ads (pre-roll, mid-roll, post-roll)")
    print("- Banner ads")
    print("- Subscription plans")
    print("- Tip system")
    print("- Revenue tracking")
    print("- Creator earnings dashboard")
    
    print("\nAccess your monetization dashboard:")
    print("- Main app: http://192.168.1.4:8000")
    print("- Earnings: http://192.168.1.4:8000/monetization/")
    print("- Ad settings: http://192.168.1.4:8000/ad-settings/")

if __name__ == '__main__':
    create_sample_data()
