from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('video/<int:video_id>/', views.video_detail, name='video_detail'),
    path('upload/', views.upload_video, name='upload_video'),
    path('my-videos/', views.my_videos, name='my_videos'),
    path('video/<int:video_id>/delete/', views.delete_video, name='delete_video'),
    path('stream/<int:video_id>/', views.VideoStreamView.get, name='stream_video'),
    path('register/', views.register, name='register'),
    
    # Monetization URLs (temporarily disabled)
    # path('monetization/', views.monetization_dashboard, name='monetization_dashboard'),
    # path('ad-settings/', views.ad_settings, name='ad_settings'),
    # path('track-ad/<int:ad_id>/', views.track_ad_view, name='track_ad_view'),
    # path('video/<int:video_id>/tip/', views.send_tip, name='send_tip'),
    # path('subscription-plans/', views.subscription_plans, name='subscription_plans'),
    # path('subscribe/<int:plan_id>/', views.subscribe, name='subscribe'),
    # path('earnings-report/', views.earnings_report, name='earnings_report'),
]
