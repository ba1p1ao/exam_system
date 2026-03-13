from rest_framework import serializers
from apps.user.models import User
from utils.PasswordEncode import hash_password


class UserSerializers(serializers.ModelSerializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)
    nickname = serializers.CharField(required=True)
    role = serializers.CharField(required=True)
    avatar = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    create_time = serializers.DateTimeField(required=False, format='%Y-%m-%d %H:%M:%S')
    update_time = serializers.DateTimeField(required=False, format='%Y-%m-%d %H:%M:%S')

    def create(self, validated_data):
        validated_data["password"] = hash_password(validated_data["password"])
        user = User.objects.create(**validated_data)
        return user

    class Meta:
        model = User
        fields = "__all__"


class UserUpdateSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=False, read_only=True)
    password = serializers.CharField(required=False, write_only=True)
    nickname = serializers.CharField(required=False)
    avatar = serializers.CharField(required=False, allow_null=True, allow_blank=True)

    def update(self, instance, validated_data):
        instance.nickname = validated_data.get("nickname", instance.nickname)
        instance.avatar = validated_data.get("avatar", instance.avatar)
        if "password" in validated_data:
            instance.password = hash_password(validated_data["password"])
        instance.save()
        return instance

    class Meta:
        model = User
        fields = ["username", "password", "nickname", "avatar"]



