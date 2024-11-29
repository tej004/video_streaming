from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from core.models import User, Video
from cloudinary.uploader import upload
from cloudinary.utils import cloudinary_url


class UserVideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = ["id", "user", "title", "description", "video_file", "uploaded_at"]


class UserSerializer(serializers.ModelSerializer):
    videos = UserVideoSerializer(many=True, read_only=True)
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "password",
            "phone_number",
            "date_of_birth",
            "first_name",
            "last_name",
            "videos",
        ]

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        return user


class VideoSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    video_file_object = serializers.FileField(write_only=True)
    video_file = serializers.ReadOnlyField()
    thumbnail_file_object = serializers.FileField(write_only=True)
    thumbnail = serializers.ReadOnlyField()

    class Meta:
        model = Video
        fields = [
            "id",
            "user",
            "user_id",
            "title",
            "genre",
            "description",
            "video_file",
            "video_file_object",
            "thumbnail",
            "thumbnail_file_object",
            "uploaded_at",
        ]

    def get_user(self, obj):
        return {
            "id": obj.user.id,
            "username": obj.user.username,
            "email": obj.user.email,
        }

    def create(self, validated_data):
        print('asdfas', "asdfas")

        video_file_object = validated_data.pop("video_file_object")

        print(video_file_object, "asdfas")
        thumbnail_file_object = validated_data.pop("thumbnail_file_object", None)

        try:
            # Upload the video to Cloudinary
            video_cloudinary_response = upload(video_file_object, resource_type="video")
            video_url = video_cloudinary_response.get(
                "secure_url"
            )  # Use secure_url for HTTPS

            thumbnail_url = None
            if thumbnail_file_object:
                thumbnail_cloudinary_response = upload(
                    thumbnail_file_object, resource_type="image"
                )
                thumbnail_url = thumbnail_cloudinary_response.get(
                    "secure_url"
                )  # Use secure_url for HTTPS

            # Create the Video instance
            video_instance = Video.objects.create(
                user=User.objects.get(id=self.context["request"].user.id),
                video_file=video_url,
                thumbnail=thumbnail_url,  # Set the uploaded thumbnail URL
                **validated_data,
            )

            video_instance.save()

            return video_instance

        except Exception as e:
            raise ValidationError(f"Video upload failed: {str(e)}")
