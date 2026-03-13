from rest_framework import serializers
from apps.exam.models import Exam, ExamRecord, ExamQuestion, AnswerRecord
from apps.question.models import Question
from apps.question.serializers import QuestionSerializers 
from django.db.models import Avg


class ExamSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    start_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, allow_null=True)
    end_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, allow_null=True)

    class Meta:
        model = Exam
        fields = "__all__"


class ExamQuestionSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Question
        fields = ["id", "type", "content", "options", "score", "difficulty", "category"]


class ExamInfoSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    start_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, allow_null=True)
    end_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, allow_null=True)
    allow_retake = serializers.IntegerField(read_only=True)

    question_ids = serializers.SerializerMethodField()
    questions = serializers.SerializerMethodField()
    class_ids = serializers.SerializerMethodField()

    def get_question_ids(self, obj):
        examquestions = ExamQuestion.objects.filter(exam=obj).values("question_id")
        ids = [question.get("question_id") for question in examquestions]
        return ids

    def get_questions(self, obj):
        examquestions = ExamQuestion.objects.filter(exam=obj)
        questions = [examquestion.question for examquestion in examquestions]
        questions_ser_data = ExamQuestionSerializer(instance=questions, many=True).data
        return questions_ser_data

    def get_class_ids(self, obj):
        from apps.exam.models import ExamClass
        exam_classes = ExamClass.objects.filter(exam=obj).values("class_info_id")
        ids = [ec.get("class_info_id") for ec in exam_classes]
        return ids


    class Meta:
        model = Exam
        fields = "__all__"


class ExamRecordAddSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    
    def create(self, validated_data):
        return ExamRecord.objects.create(**validated_data)
    
    class Meta:
        model = ExamRecord
        fields = "__all__"
    

class ExamRecordListSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    exam_id = serializers.SerializerMethodField()
    user_id = serializers.SerializerMethodField()
    exam_title = serializers.SerializerMethodField()
    exam_total_score = serializers.SerializerMethodField()
    exam_pass_score = serializers.SerializerMethodField()
    exam_duration = serializers.SerializerMethodField()

    def get_exam_id(self, obj):
        return obj.exam_id

    def get_user_id(self, obj):
        return obj.user_id

    def get_exam_title(self, obj):
        return obj.exam.title

    def get_exam_total_score(self, obj):
        return obj.exam.total_score

    def get_exam_pass_score(self, obj):
        return obj.exam.pass_score

    def get_exam_duration(self, obj):
        return obj.exam.duration

    start_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, allow_null=True)
    submit_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, allow_null=True)

    class Meta:
        model = ExamRecord
        fields = ['id', 'exam_id', 'user_id', 'score', 'is_passed', 'status', 'start_time', 'submit_time', 'exam_title', 'exam_total_score', 'exam_pass_score', 'exam_duration']



class ExamRecordDetailSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    
    exam = serializers.SerializerMethodField()
    def get_exam(self, obj):
        return ExamSerializer(instance=obj.exam).data
    
    user_id = serializers.SerializerMethodField()
    def get_user_id(self, obj):
        return obj.user_id
    
    answers = serializers.SerializerMethodField()
    def get_answers(self, obj):
        exam_questions = ExamQuestion.objects.filter(exam_id=obj.exam_id)
        questions = [eq.question for eq in exam_questions]
        answers = []
        for question in questions:
            data = {        
                "user_answer": None,
                "is_correct": None,
                "score": None,
            }
            data["id"] = question.id
            data["question"] = QuestionSerializers(instance=question).data
            user_answer = AnswerRecord.objects.filter(exam_record_id=obj.id, question_id=question.id).first()
            if user_answer:
                data["user_answer"] = user_answer.user_answer
                data["is_correct"] = user_answer.is_correct
                data["score"] = user_answer.score
            answers.append(data)
        return answers
    
    start_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, allow_null=True)
    submit_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, allow_null=True)

    
    class Meta:
        model = ExamRecord
        fields = "__all__"


class AnswersSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    question = serializers.SerializerMethodField()
    create_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, allow_null=True)
    update_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, allow_null=True)
 
    def get_question(self, obj):
        return QuestionSerializers(instance=obj.question).data
    
    class Meta:
        model = AnswerRecord
        fields = "__all__"



class ExamRecordStatisticsSerializer(serializers.ModelSerializer):
    participant_count = serializers.IntegerField()
    average_score = serializers.FloatField()
    pass_rate = serializers.FloatField()
    
    class Meta:
        model = Exam
        fields = "__all__"
    
    
        
class GroupedExamSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    start_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, allow_null=True)
    end_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, allow_null=True)
    create_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, allow_null=True)
    # participant_count = serializers.SerializerMethodField()
    # average_score = serializers.SerializerMethodField()
    # pass_rate = serializers.SerializerMethodField()
    # student_records = serializers.SerializerMethodField()
    
    # def get_participant_count(self, obj):
    #     user_count = ExamRecord.objects.filter(exam_id=obj.id).values("user_id").distinct().count()
    #     return user_count
    
    # def get_average_score(self, obj):
    #     average_score = ExamRecord.objects.filter(exam_id=obj.id).aggregate(average_score=Avg("score"))["average_score"]
    #     return average_score
       
    # def get_pass_rate(self, obj):
    #     submit_count = ExamRecord.objects.filter(exam_id=obj.id).values("user_id").count()
    #     pass_count = ExamRecord.objects.filter(exam_id=obj.id, is_passed=1).count()
    #     pass_rate = 0
    #     if submit_count and pass_count:
    #         pass_rate = f"{(pass_count / submit_count):.2f}"
    #     return pass_rate

    participant_count = serializers.IntegerField()
    average_score = serializers.FloatField()
    pass_rate = serializers.FloatField()
    student_records = serializers.SerializerMethodField()

    def get_student_records(self, obj):
         # 获取该考试的所有学生记录
        student_records = ExamRecord.objects.filter(
            exam=obj
        ).select_related('user').order_by('-score', 'submit_time')
        
        # 应用学生筛选参数
        context = self.context if hasattr(self, 'context') else {}
        student_username = context.get('student_username', '')
        student_nickname = context.get('student_nickname', '')
        student_status = context.get('student_status', '')
        student_is_passed = context.get('student_is_passed', '')
        
        # 用户名筛选
        if student_username:
            student_records = student_records.filter(user__username__icontains=student_username)
        
        # 昵称筛选
        if student_nickname:
            student_records = student_records.filter(user__nickname__icontains=student_nickname)
        
        # 考试状态筛选
        if student_status:
            student_records = student_records.filter(status=student_status)
        
        # 是否及格筛选
        if student_is_passed != '':
            student_records = student_records.filter(is_passed=int(student_is_passed))
        
        student_records_data = StudentRecordSerializer(instance=student_records, many=True).data
        return student_records_data
    
    class Meta:
        model = Exam
        fields = "__all__"
        
        
class StudentRecordSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username')
    nickname = serializers.CharField(source='user.nickname')
    role = serializers.CharField(source='user.role')
    avatar = serializers.CharField(source='user.avatar', allow_null=True)
    user_status = serializers.IntegerField(source='user.status')
    
    start_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, allow_null=True)
    submit_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False, allow_null=True)
    
    class Meta:
        model = ExamRecord
        fields = ['id', 'user_id', 'username', 'nickname', 'role', 'avatar', 'user_status',
                'score', 'is_passed', 'status', 'start_time', 'submit_time']