from django.urls import path
from .views import VideoList

urlpatterns = [
    path('videos/', VideoList.as_view(), name='video-list'),
]
