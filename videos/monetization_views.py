from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.db.models import Sum, Count
from django.utils import timezone
from datetime import timedelta
import json

from .models import Video
from .monetization_models import Ad, VideoAd, AdCampaign, AdView, Revenue, CreatorEarnings, Tip, SubscriptionPlan, UserSubscription, Payment


@login_required
def monetization_dashboard(request):
    """Creator's monetization dashboard"""
    # Get user's earnings
    earnings, created = CreatorEarnings.objects.get_or_create(user=request.user)
    
    # Get recent revenues
    recent_revenues = Revenue.objects.filter(user=request.user).order_by('-created_at')[:10]
    
    # Get video performance
    videos = Video.objects.filter(uploader=request.user).annotate(
        total_views=Count('ad_views'),
        total_revenue=Sum('revenues__amount')
    ).order_by('-uploaded_at')[:10]
    
    # Get monthly earnings
    thirty_days_ago = timezone.now() - timedelta(days=30)
    monthly_earnings = Revenue.objects.filter(
        user=request.user,
        created_at__gte=thirty_days_ago
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    context = {
        'earnings': earnings,
        'recent_revenues': recent_revenues,
        'videos': videos,
        'monthly_earnings': monthly_earnings,
    }
    return render(request, 'videos/monetization_dashboard.html', context)


@login_required
def ad_settings(request):
    """Configure ad settings for videos"""
    if request.method == 'POST':
        video_id = request.POST.get('video_id')
        ad_positions = request.POST.getlist('ad_positions')
        
        video = get_object_or_404(Video, id=video_id, uploader=request.user)
        
        # Clear existing ads
        VideoAd.objects.filter(video=video).delete()
        
        # Add new ads
        for position in ad_positions:
            if position:
                # Get a random ad for this position
                ad = Ad.objects.filter(is_active=True).order_by('?').first()
                if ad:
                    VideoAd.objects.create(
                        video=video,
                        ad=ad,
                        position=int(position)
                    )
        
        messages.success(request, 'Ad settings updated successfully!')
        return redirect('ad_settings')
    
    # Get user's videos with ad information
    videos = Video.objects.filter(uploader=request.user).prefetch_related('video_ads__ad')
    
    context = {
        'videos': videos,
    }
    return render(request, 'videos/ad_settings.html', context)


@csrf_exempt
@require_http_methods(["POST"])
def track_ad_view(request, ad_id):
    """Track ad view for revenue calculation"""
    try:
        data = json.loads(request.body)
        video_id = data.get('video_id')
        duration_watched = data.get('duration_watched', 0)
        was_clicked = data.get('was_clicked', False)
        
        ad = get_object_or_404(Ad, id=ad_id)
        video = get_object_or_404(Video, id=video_id)
        
        # Calculate revenue based on ad type and engagement
        revenue_earned = 0
        if was_clicked:
            revenue_earned = float(ad.campaign.cost_per_click)
        else:
            # Revenue based on view duration
            if duration_watched >= ad.duration * 0.5:  # Watched at least 50%
                revenue_earned = float(ad.campaign.cost_per_view)
        
        # Create ad view record
        ad_view = AdView.objects.create(
            ad=ad,
            video=video,
            user=request.user if request.user.is_authenticated else None,
            ip_address=request.META.get('REMOTE_ADDR'),
            duration_watched=duration_watched,
            was_clicked=was_clicked,
            revenue_earned=revenue_earned
        )
        
        # Update creator earnings
        if video.uploader != request.user:  # Don't count own views
            Revenue.objects.create(
                video=video,
                user=video.uploader,
                revenue_type='ad_views',
                amount=revenue_earned,
                description=f'Ad view: {ad.title}'
            )
            
            # Update creator earnings
            earnings, created = CreatorEarnings.objects.get_or_create(user=video.uploader)
            earnings.total_earned += revenue_earned
            earnings.pending_amount += revenue_earned
            earnings.save()
        
        return JsonResponse({'success': True, 'revenue': float(revenue_earned)})
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
def send_tip(request, video_id):
    """Send tip to video creator"""
    if request.method == 'POST':
        video = get_object_or_404(Video, id=video_id)
        amount = float(request.POST.get('amount', 0))
        message = request.POST.get('message', '')
        is_anonymous = request.POST.get('is_anonymous') == 'on'
        
        if amount <= 0:
            messages.error(request, 'Please enter a valid tip amount.')
            return redirect('video_detail', video_id=video_id)
        
        # Create tip record
        tip = Tip.objects.create(
            video=video,
            from_user=request.user,
            to_user=video.uploader,
            amount=amount,
            message=message,
            is_anonymous=is_anonymous
        )
        
        # Update creator earnings
        Revenue.objects.create(
            video=video,
            user=video.uploader,
            revenue_type='tips',
            amount=amount,
            description=f'Tip from {request.user.username if not is_anonymous else "Anonymous"}'
        )
        
        earnings, created = CreatorEarnings.objects.get_or_create(user=video.uploader)
        earnings.total_earned += amount
        earnings.pending_amount += amount
        earnings.save()
        
        messages.success(request, f'Tip of ${amount} sent successfully!')
        return redirect('video_detail', video_id=video_id)
    
    return redirect('video_detail', video_id=video_id)


@login_required
def subscription_plans(request):
    """View available subscription plans"""
    plans = SubscriptionPlan.objects.filter(is_active=True)
    user_subscription = None
    
    if request.user.is_authenticated:
        user_subscription = UserSubscription.objects.filter(
            user=request.user,
            is_active=True
        ).first()
    
    context = {
        'plans': plans,
        'user_subscription': user_subscription,
    }
    return render(request, 'videos/subscription_plans.html', context)


@login_required
def subscribe(request, plan_id):
    """Subscribe to a plan"""
    plan = get_object_or_404(SubscriptionPlan, id=plan_id)
    
    # Check if user already has an active subscription
    existing_subscription = UserSubscription.objects.filter(
        user=request.user,
        is_active=True
    ).first()
    
    if existing_subscription:
        messages.warning(request, 'You already have an active subscription.')
        return redirect('subscription_plans')
    
    # Create subscription (in real implementation, integrate with Stripe)
    subscription = UserSubscription.objects.create(
        user=request.user,
        plan=plan,
        expires_at=timezone.now() + timedelta(days=30)  # Monthly
    )
    
    # Create payment record
    from .monetization_models import Payment
    Payment.objects.create(
        user=request.user,
        subscription=subscription,
        amount=plan.price_monthly,
        status='completed',
        payment_method='stripe',
        completed_at=timezone.now()
    )
    
    messages.success(request, f'Successfully subscribed to {plan.name}!')
    return redirect('subscription_plans')


@login_required
def earnings_report(request):
    """Detailed earnings report"""
    earnings, created = CreatorEarnings.objects.get_or_create(user=request.user)
    
    # Get earnings by type
    earnings_by_type = Revenue.objects.filter(user=request.user).values('revenue_type').annotate(
        total=Sum('amount'),
        count=Count('id')
    ).order_by('-total')
    
    # Get monthly earnings for the last 12 months
    monthly_earnings = []
    for i in range(12):
        month_start = timezone.now() - timedelta(days=30*i)
        month_end = month_start + timedelta(days=30)
        
        month_total = Revenue.objects.filter(
            user=request.user,
            created_at__gte=month_start,
            created_at__lt=month_end
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        monthly_earnings.append({
            'month': month_start.strftime('%B %Y'),
            'amount': month_total
        })
    
    context = {
        'earnings': earnings,
        'earnings_by_type': earnings_by_type,
        'monthly_earnings': monthly_earnings,
    }
    return render(request, 'videos/earnings_report.html', context)
