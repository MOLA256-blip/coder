from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from .models import Video


class AdCampaign(models.Model):
    """Ad campaigns for video monetization"""
    name = models.CharField(max_length=200)
    advertiser = models.CharField(max_length=200)
    budget = models.DecimalField(max_digits=10, decimal_places=2)
    cost_per_view = models.DecimalField(max_digits=6, decimal_places=4, default=0.01)
    cost_per_click = models.DecimalField(max_digits=6, decimal_places=4, default=0.05)
    is_active = models.BooleanField(default=True)
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField()
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name


class Ad(models.Model):
    """Individual ads"""
    AD_TYPES = [
        ('banner', 'Banner Ad'),
        ('video_pre', 'Pre-roll Video Ad'),
        ('video_mid', 'Mid-roll Video Ad'),
        ('video_post', 'Post-roll Video Ad'),
        ('overlay', 'Overlay Ad'),
    ]
    
    campaign = models.ForeignKey(AdCampaign, on_delete=models.CASCADE, related_name='ads')
    title = models.CharField(max_length=200)
    ad_type = models.CharField(max_length=20, choices=AD_TYPES)
    image_url = models.URLField(blank=True, null=True)
    video_url = models.URLField(blank=True, null=True)
    click_url = models.URLField()
    duration = models.PositiveIntegerField(default=30, help_text="Duration in seconds")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.title} ({self.get_ad_type_display()})"


class VideoAd(models.Model):
    """Ads associated with specific videos"""
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name='video_ads')
    ad = models.ForeignKey(Ad, on_delete=models.CASCADE)
    position = models.PositiveIntegerField(help_text="Position in video (seconds)")
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ('video', 'ad', 'position')

    def __str__(self):
        return f"{self.video.title} - {self.ad.title} at {self.position}s"


class AdView(models.Model):
    """Track ad views for revenue calculation"""
    ad = models.ForeignKey(Ad, on_delete=models.CASCADE, related_name='views')
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name='ad_views')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    ip_address = models.GenericIPAddressField()
    viewed_at = models.DateTimeField(default=timezone.now)
    duration_watched = models.PositiveIntegerField(default=0, help_text="Seconds watched")
    was_clicked = models.BooleanField(default=False)
    revenue_earned = models.DecimalField(max_digits=8, decimal_places=4, default=0)

    def __str__(self):
        return f"{self.ad.title} viewed by {self.user or 'Anonymous'}"


class SubscriptionPlan(models.Model):
    """Subscription plans for premium features"""
    name = models.CharField(max_length=100)
    description = models.TextField()
    price_monthly = models.DecimalField(max_digits=8, decimal_places=2)
    price_yearly = models.DecimalField(max_digits=8, decimal_places=2)
    features = models.JSONField(default=list, help_text="List of features included")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name


class UserSubscription(models.Model):
    """User subscription to premium plans"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscriptions')
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    started_at = models.DateTimeField(default=timezone.now)
    expires_at = models.DateTimeField()
    payment_method = models.CharField(max_length=50, default='stripe')
    stripe_subscription_id = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} - {self.plan.name}"

    @property
    def is_expired(self):
        return timezone.now() > self.expires_at


class Payment(models.Model):
    """Payment records"""
    PAYMENT_STATUS = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    subscription = models.ForeignKey(UserSubscription, on_delete=models.CASCADE, null=True, blank=True)
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='pending')
    payment_method = models.CharField(max_length=50)
    stripe_payment_intent_id = models.CharField(max_length=200, blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    completed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - ${self.amount} ({self.status})"


class Revenue(models.Model):
    """Revenue tracking for content creators"""
    REVENUE_TYPES = [
        ('ad_views', 'Ad Views'),
        ('ad_clicks', 'Ad Clicks'),
        ('subscriptions', 'Subscriptions'),
        ('tips', 'Tips'),
        ('sponsorships', 'Sponsorships'),
    ]
    
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name='revenues', null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='revenues')
    revenue_type = models.CharField(max_length=20, choices=REVENUE_TYPES)
    amount = models.DecimalField(max_digits=8, decimal_places=4)
    description = models.CharField(max_length=200)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user.username} - ${self.amount} ({self.get_revenue_type_display()})"


class CreatorEarnings(models.Model):
    """Track total earnings for content creators"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='earnings')
    total_earned = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    pending_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    last_payment_date = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - ${self.total_earned} earned"

    @property
    def available_for_payout(self):
        return self.total_earned - self.total_paid


class Tip(models.Model):
    """Tips from viewers to content creators"""
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name='tips')
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tips_sent')
    to_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tips_received')
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    message = models.TextField(blank=True)
    is_anonymous = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"${self.amount} tip from {self.from_user.username} to {self.to_user.username}"
