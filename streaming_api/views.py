from rest_framework import generics
from rest_framework.response import Response

class VideoList(generics.GenericAPIView):
    def get(self, request, *args, **kwargs):
        # Mock data - replace with actual video model later
        videos = [
            {
                'id': 1,
                'title': 'Sample Video 1',
                'url': 'http://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4'
            },
            {
                'id': 2,
                'title': 'Sample Video 2',
                'url': 'http://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ElephantsDream.mp4'
            }
        ]
        return Response(videos)
