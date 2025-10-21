import os
import mimetypes
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponse, StreamingHttpResponse, Http404
from django.views.decorators.http import require_http_methods
from .models import Video, Comment
from .forms import VideoUploadForm, CommentForm, UserRegistrationForm
# Temporarily disabled monetization imports
# from .monetization_views import monetization_dashboard, ad_settings, track_ad_view, send_tip, subscription_plans, subscribe, earnings_report


def home(request):
    """Home page with latest videos"""
    videos = Video.objects.filter(is_public=True).select_related('uploader')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        videos = videos.filter(
            Q(title__icontains=search_query) | 
            Q(description__icontains=search_query) |
            Q(uploader__username__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(videos, 12)
    page_number = request.GET.get('page')
    videos = paginator.get_page(page_number)
    
    context = {
        'videos': videos,
        'search_query': search_query,
    }
    return render(request, 'videos/home.html', context)


def video_detail(request, video_id):
    """Video detail page with player and comments"""
    video = get_object_or_404(Video, id=video_id, is_public=True)
    
    # Increment views
    video.increment_views()
    
    # Get comments
    comments = video.comments.select_related('user').order_by('-created_at')
    
    # Handle comment form
    comment_form = CommentForm()
    if request.method == 'POST' and request.user.is_authenticated:
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.video = video
            comment.user = request.user
            comment.save()
            messages.success(request, 'Your comment has been added!')
            return redirect('video_detail', video_id=video_id)
    
    # Related videos
    related_videos = Video.objects.filter(
        is_public=True
    ).exclude(id=video.id)[:6]
    
    context = {
        'video': video,
        'comments': comments,
        'comment_form': comment_form,
        'related_videos': related_videos,
    }
    return render(request, 'videos/video_detail.html', context)


class VideoStreamView:
    """Efficient video streaming with range request support"""
    
    @staticmethod
    def get(request, video_id):
        video = get_object_or_404(Video, id=video_id, is_public=True)
        
        # Get video file path
        video_path = video.video_file.path
        if not os.path.exists(video_path):
            raise Http404("Video file not found")
        
        # Get file info
        file_size = os.path.getsize(video_path)
        content_type = mimetypes.guess_type(video_path)[0] or 'video/mp4'
        
        # Handle range requests for efficient streaming
        range_header = request.META.get('HTTP_RANGE')
        if range_header:
            return VideoStreamView._handle_range_request(video_path, file_size, content_type, range_header)
        
        # Regular response for non-range requests
        response = StreamingHttpResponse(
            VideoStreamView._file_iterator(video_path),
            content_type=content_type
        )
        response['Content-Length'] = str(file_size)
        response['Accept-Ranges'] = 'bytes'
        return response
    
    @staticmethod
    def _handle_range_request(file_path, file_size, content_type, range_header):
        """Handle HTTP range requests for video streaming"""
        try:
            byte_start = 0
            byte_end = file_size - 1
            
            # Parse range header
            if range_header.startswith('bytes='):
                ranges = range_header[6:].split(',')[0]
                if '-' in ranges:
                    start, end = ranges.split('-', 1)
                    if start:
                        byte_start = int(start)
                    if end:
                        byte_end = int(end)
            
            # Ensure valid range
            byte_start = max(0, byte_start)
            byte_end = min(file_size - 1, byte_end)
            content_length = byte_end - byte_start + 1
            
            # Create streaming response
            response = StreamingHttpResponse(
                VideoStreamView._file_iterator(file_path, byte_start, content_length),
                status=206,  # Partial Content
                content_type=content_type
            )
            
            response['Content-Length'] = str(content_length)
            response['Content-Range'] = f'bytes {byte_start}-{byte_end}/{file_size}'
            response['Accept-Ranges'] = 'bytes'
            
            return response
            
        except (ValueError, OSError):
            # If range parsing fails, return full file
            response = StreamingHttpResponse(
                VideoStreamView._file_iterator(file_path),
                content_type=content_type
            )
            response['Content-Length'] = str(file_size)
            return response
    
    @staticmethod
    def _file_iterator(file_path, offset=0, length=None, chunk_size=8192):
        """Iterator for streaming file content"""
        with open(file_path, 'rb') as f:
            f.seek(offset)
            remaining = length
            while True:
                bytes_to_read = chunk_size
                if remaining is not None:
                    bytes_to_read = min(bytes_to_read, remaining)
                    if bytes_to_read <= 0:
                        break
                
                data = f.read(bytes_to_read)
                if not data:
                    break
                
                if remaining is not None:
                    remaining -= len(data)
                
                yield data


@login_required
def upload_video(request):
    """Video upload page"""
    if request.method == 'POST':
        form = VideoUploadForm(request.POST, request.FILES)
        if form.is_valid():
            video = form.save(commit=False)
            video.uploader = request.user
            video.save()
            
            messages.success(request, 'Video uploaded successfully!')
            return redirect('video_detail', video_id=video.id)
    else:
        form = VideoUploadForm()
    
    return render(request, 'videos/upload_video.html', {'form': form})


def register(request):
    """User registration"""
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful! Welcome to VideoStream!')
            return redirect('home')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'registration/register.html', {'form': form})


@login_required
def my_videos(request):
    """User's uploaded videos"""
    videos = Video.objects.filter(uploader=request.user).order_by('-uploaded_at')
    
    paginator = Paginator(videos, 12)
    page_number = request.GET.get('page')
    videos = paginator.get_page(page_number)
    
    return render(request, 'videos/my_videos.html', {'videos': videos})


@login_required
def delete_video(request, video_id):
    """Delete a video"""
    video = get_object_or_404(Video, id=video_id, uploader=request.user)
    
    if request.method == 'POST':
        # Delete video file
        if video.video_file:
            try:
                os.remove(video.video_file.path)
            except OSError:
                pass
        
        # Delete thumbnail file
        if video.thumbnail:
            try:
                os.remove(video.thumbnail.path)
            except OSError:
                pass
        
        video.delete()
        messages.success(request, 'Video deleted successfully!')
        return redirect('my_videos')
    
    return render(request, 'videos/delete_video.html', {'video': video})
