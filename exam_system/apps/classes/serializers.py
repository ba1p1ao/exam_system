from rest_framework import serializers
from apps.classes.models import Class


class ClassListSerializer(serializers.ModelSerializer):
    create_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, allow_null=True)
    update_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, allow_null=True)

    class Meta:
        model = Class
        fields = '__all__'
