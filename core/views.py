from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from core.models import User, Video
from rest_framework.permissions import AllowAny
from core.serializers import UserSerializer, VideoSerializer
from collections import defaultdict
import random
from rest_framework.parsers import MultiPartParser, FormParser
from cloudinary.uploader import upload


class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_queryset(self):
        user = self.request.user

        return User.objects.get(id=user.id)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        serializer = self.get_serializer(queryset, many=False)

        return Response(serializer.data)

    @action(
        detail=False,
        methods=["POST"],
        url_path="video-creation",
        parser_classes=[MultiPartParser, FormParser],
    )
    def create_video(self, request):
        serializer = VideoSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=False,
        methods=["POST"],
        url_path="sign-up",
        permission_classes=[AllowAny],
    )
    def sign_up(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VideoViewSet(ModelViewSet):
    queryset = Video.objects.all()
    serializer_class = VideoSerializer

    def get_queryset(self):
        user = self.request.user
        return Video.objects.filter(user=user).order_by("-uploaded_at")

    @action(detail=False, methods=["GET"], url_path="group-by-genre")
    def group_by_genre(self, request):
        user = self.request.user
        videos = Video.objects.filter(user=user)
        grouped_videos = defaultdict(list)

        for video in videos:
            genre = video.genre if video.genre else "N/A"
            grouped_videos[genre].append(video)

        # Randomize the order in the list of videos for each genre
        for genre in grouped_videos:
            random.shuffle(grouped_videos[genre])

        # Sort the genres by the length of their video list
        sorted_grouped_videos = dict(
            sorted(grouped_videos.items(), key=lambda item: len(item[1]), reverse=True)
        )

        # Serialize the grouped videos
        grouped_videos_serialized = {
            genre: VideoSerializer(videos, many=True).data
            for genre, videos in sorted_grouped_videos.items()
        }

        return Response(grouped_videos_serialized, status=status.HTTP_200_OK)

    @action(
        detail=False,
        methods=["POST"],
        url_path="update-video",
        parser_classes=[MultiPartParser, FormParser],
    )
    def update_video(self, request):
        video_id = request.data.get("id")
        try:
            video = Video.objects.get(id=video_id)
        except Video.DoesNotExist:
            return Response(
                {"error": "Video not found"}, status=status.HTTP_404_NOT_FOUND
            )

        video.title = request.data.get("title", video.title)
        video.description = request.data.get("description", video.description)
        video.genre = request.data.get("genre", video.genre)

        if "video_file_object" in request.data:
            video_file_object = request.data["video_file_object"]
            video_cloudinary_response = upload(video_file_object, resource_type="video")
            video.video_file = video_cloudinary_response.get("secure_url")

        if "thumbnail_file_object" in request.data:
            thumbnail_file_object = request.data["thumbnail_file_object"]
            thumbnail_cloudinary_response = upload(
                thumbnail_file_object, resource_type="image"
            )
            video.thumbnail = thumbnail_cloudinary_response.get("secure_url")

        video.save()
        return Response(VideoSerializer(video).data, status=status.HTTP_200_OK)
