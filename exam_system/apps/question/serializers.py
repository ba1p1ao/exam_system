from rest_framework import serializers
from apps.question.models import Question
from apps.user.models import User

class QuestionSerializers(serializers.ModelSerializer):
    
    create_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, allow_null=True)
    update_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, allow_null=True)
    class Meta:
        model = Question
        fields = "__all__"


class QuestionAddSerializers(serializers.ModelSerializer):
    type = serializers.CharField(required=True)
    category = serializers.CharField(required=True)
    content = serializers.CharField(required=True)
    options = serializers.JSONField(required=False)
    answer = serializers.CharField(required=True)
    analysis = serializers.CharField(required=False)
    difficulty = serializers.CharField(required=True)
    score = serializers.IntegerField(required=True)
    creator = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    def create(self, validated_data):
        return Question.objects.create(**validated_data)

    # ModelSerializer 已经内置了 update 逻辑，不需要重写。
    # def update(self, instance, validated_data):
    #     instance = validated_data
    #     return Question.objects.update(**instance)

    class Meta:
        model = Question
        fields = "__all__"
        
        
        
class QuestionListSerializers(serializers.ModelSerializer):
    # create_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, allow_null=True)
    # update_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, allow_null=True)
    class Meta:
        model = Question
        fields = ["id", "type", "category", "content", "options", "answer", "analysis", "difficulty", "score"]