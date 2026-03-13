# 考试记录分组 API 文档

## 概述

为满足管理员/老师查看考试记录的需求，新增按考试分组的 API 接口。原有 `/api/exam/record/list/` 接口保持不变，供学生查看个人考试记录使用。

## 新增接口

### 1. 获取按考试分组的考试记录

**接口地址**: `GET /api/exam/grouped-records/`

**权限要求**: teacher、admin

**请求参数** (Query):

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| page | int | 否 | 页码，默认1 |
| size | int | 否 | 每页数量，默认10 |
| title | string | 否 | 试卷标题（模糊搜索） |
| status | string | 否 | 试卷状态：draft/published/closed |

**响应格式**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "list": [
      {
        "id": 1,
        "title": "数学测试卷",
        "description": "第一章测试",
        "duration": 60,
        "total_score": 100,
        "pass_score": 60,
        "start_time": "2024-01-01 10:00:00",
        "end_time": "2024-01-01 12:00:00",
        "is_random": 0,
        "status": "published",
        "creator_id": 1,
        "create_time": "2024-01-01 00:00:00",
        "participant_count": 30,
        "average_score": 78.5,
        "pass_rate": 0.8,
        "student_records": [
          {
            "id": 101,
            "user_id": 1,
            "username": "student1",
            "nickname": "学生1",
            "score": 85,
            "is_passed": 1,
            "status": "graded",
            "start_time": "2024-01-01 10:00:00",
            "submit_time": "2024-01-01 11:00:00"
          },
          {
            "id": 102,
            "user_id": 2,
            "username": "student2",
            "nickname": "学生2",
            "score": 45,
            "is_passed": 0,
            "status": "graded",
            "start_time": "2024-01-01 10:05:00",
            "submit_time": "2024-01-01 10:45:00"
          }
        ]
      }
    ],
    "total": 20,
    "page": 1,
    "size": 10
  }
}
```

**字段说明**:

#### 考试信息字段
- `id`: 试卷ID
- `title`: 试卷标题
- `description`: 试卷描述
- `duration`: 考试时长（分钟）
- `total_score`: 总分
- `pass_score`: 及格分数
- `start_time`: 考试开始时间
- `end_time`: 考试结束时间
- `is_random`: 是否随机组卷（0否 1是）
- `status`: 试卷状态（draft/published/closed）
- `creator_id`: 创建者ID
- `create_time`: 创建时间
- `participant_count`: 参加考试人数
- `average_score`: 平均分（可为null，如果无人参加）
- `pass_rate`: 及格率（0-1之间的小数，可为null）

#### 学生记录字段（student_records数组）
- `id`: 考试记录ID
- `user_id`: 学生ID
- `username`: 用户名
- `nickname`: 昵称
- `score`: 得分（可为null，如果未批改）
- `is_passed`: 是否及格（1及格 0不及格，可为null）
- `status`: 考试记录状态（not_started/in_progress/submitted/graded）
- `start_time`: 开始考试时间
- `submit_time`: 提交试卷时间

## 数据库查询逻辑

### 1. 查询考试列表（按条件过滤）
```sql
SELECT 
    e.*,
    COUNT(DISTINCT er.id) as participant_count,
    AVG(er.score) as average_score,
    AVG(CASE WHEN er.is_passed = 1 THEN 1.0 ELSE 0.0 END) as pass_rate
FROM exam e
LEFT JOIN exam_record er ON e.id = er.exam_id AND er.status = 'graded'
WHERE e.status IN ('published', 'closed')  -- 只查询已发布或已关闭的考试
GROUP BY e.id
ORDER BY e.create_time DESC
```

### 2. 查询单个考试的所有学生记录
```sql
SELECT 
    er.*,
    u.username,
    u.nickname
FROM exam_record er
JOIN user u ON er.user_id = u.id
WHERE er.exam_id = ?
ORDER BY er.score DESC, er.submit_time ASC
```

## 后端实现建议

### 1. 新增序列化器 `GroupedExamSerializer`
```python
class GroupedExamSerializer(serializers.ModelSerializer):
    participant_count = serializers.IntegerField()
    average_score = serializers.FloatField(allow_null=True)
    pass_rate = serializers.FloatField(allow_null=True)
    student_records = StudentRecordSerializer(many=True, read_only=True)
    
    class Meta:
        model = Exam
        fields = ['id', 'title', 'description', 'duration', 'total_score', 
                 'pass_score', 'start_time', 'end_time', 'is_random', 'status',
                 'creator_id', 'create_time', 'participant_count', 
                 'average_score', 'pass_rate', 'student_records']

class StudentRecordSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username')
    nickname = serializers.CharField(source='user.nickname')
    
    class Meta:
        model = ExamRecord
        fields = ['id', 'user_id', 'username', 'nickname', 'score', 
                 'is_passed', 'status', 'start_time', 'submit_time']
```

### 2. 新增视图 `GroupedExamRecordListView`
```python
class GroupedExamRecordListView(APIView):
    @check_auth
    def get(self, request):
        # 检查权限
        if request.user.get('role') not in ['teacher', 'admin']:
            return MyResponse.failed("无权限访问")
        
        # 获取查询参数
        title = request.GET.get('title', '')
        status = request.GET.get('status', '')
        page = int(request.GET.get('page', 1))
        size = int(request.GET.get('size', 10))
        
        # 构建查询条件
        queryset = Exam.objects.all()
        
        if title:
            queryset = queryset.filter(title__icontains=title)
        if status:
            queryset = queryset.filter(status=status)
        else:
            # 默认只显示已发布和已关闭的考试
            queryset = queryset.filter(status__in=['published', 'closed'])
        
        # 添加统计信息
        queryset = queryset.annotate(
            participant_count=Count('examrecord', filter=Q(examrecord__status='graded')),
            average_score=Avg('examrecord__score', filter=Q(examrecord__status='graded')),
            pass_rate=Avg(
                Case(
                    When(examrecord__is_passed=1, then=1.0),
                    When(examrecord__is_passed=0, then=0.0),
                    default=None,
                    output_field=FloatField()
                ),
                filter=Q(examrecord__status='graded')
            )
        )
        
        # 分页
        total = queryset.count()
        offset = (page - 1) * size
        exams = queryset.order_by('-create_time')[offset:offset + size]
        
        # 为每个考试获取学生记录
        result = []
        for exam in exams:
            exam_data = GroupedExamSerializer(exam).data
            
            # 获取该考试的所有学生记录
            student_records = ExamRecord.objects.filter(
                exam=exam
            ).select_related('user').order_by('-score', 'submit_time')
            
            exam_data['student_records'] = StudentRecordSerializer(
                student_records, many=True
            ).data
            
            result.append(exam_data)
        
        response_data = {
            "list": result,
            "total": total,
            "page": page,
            "size": size
        }
        
        return MyResponse.success(data=response_data)
```

### 3. 在 `urls.py` 中添加路由
```python
from . import views

urlpatterns = [
    # ... 原有路由
    
    # 考试记录分组
    path("grouped-records/", views.GroupedExamRecordListView.as_view()),
]
```

## 前端对接说明

### 1. API 调用
前端已添加 `getGroupedExamRecords` 方法：
```javascript
// 获取按考试分组的考试记录（管理员/老师专用）
export const getGroupedExamRecords = (params) => {
  return request({
    url: '/exam/grouped-records/',
    method: 'get',
    params
  })
}
```

### 2. 页面逻辑
- 学生角色：继续使用原有 `/exam/record/list/` 接口
- 管理员/老师角色：默认使用新的 `/exam/grouped-records/` 接口
- 支持视图切换：可以在"按考试分组"和"列表视图"之间切换

### 3. 数据展示
分组视图展示以下信息：
- 考试基本信息（标题、描述、总分、及格分等）
- 参加人数、平均分、及格率
- 展开显示所有学生成绩列表
- 链接到考试详情和学生考试记录详情

## 性能优化建议

1. **数据库索引**：
   - `exam_record` 表添加 `(exam_id, status)` 复合索引
   - `exam_record` 表添加 `(exam_id, score)` 复合索引

2. **查询优化**：
   - 使用 `select_related` 减少查询次数
   - 考虑分页加载学生记录（如果学生数量很多）

3. **缓存策略**：
   - 考试统计信息可以缓存，减少重复计算
   - 缓存时间建议：5-10分钟

## 测试用例

### 1. 权限测试
- 学生角色访问 `/exam/grouped-records/` 应返回无权限错误
- 老师/管理员角色可以正常访问

### 2. 数据准确性测试
- 验证 `participant_count` 只计算 `status='graded'` 的记录
- 验证 `average_score` 和 `pass_rate` 计算正确
- 验证分页功能正常

### 3. 性能测试
- 模拟大量考试记录，测试查询性能
- 测试并发访问性能