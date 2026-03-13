# 在线考试系统 API 接口文档

## 基础信息

- **Base URL**: `http://localhost:8010/api`
- **认证方式**: Bearer Token
- **响应格式**: JSON

## 通用响应格式

```json
{
  "code": 200,
  "message": "success",
  "data": {}
}
```

### 状态码说明

- `200`: 请求成功
- `400`: 请求参数错误
- `401`: 未授权，需要登录
- `403`: 无权限访问
- `404`: 资源不存在
- `500`: 服务器内部错误

---

## 1. 用户模块

### 1.1 用户注册

**接口地址**: `POST /user/register`

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| username | string | 是 | 用户名，唯一 |
| password | string | 是 | 密码 |
| nickname | string | 是 | 昵称 |
| role | string | 是 | 角色：student(学生) / teacher(教师) |

**请求示例**:
```json
{
  "username": "test_user",
  "password": "123456",
  "nickname": "测试用户",
  "role": "student"
}
```

**响应示例**:
```json
{
  "code": 200,
  "message": "注册成功",
  "data": {
    "id": 1,
    "username": "test_user",
    "nickname": "测试用户",
    "role": "student"
  }
}
```

### 1.2 用户登录

**接口地址**: `POST /user/login`

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| username | string | 是 | 用户名 |
| password | string | 是 | 密码 |

**请求示例**:
```json
{
  "username": "test_user",
  "password": "123456"
}
```

**响应示例**:
```json
{
  "code": 200,
  "message": "登录成功",
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "user_info": {
      "id": 1,
      "username": "test_user",
      "nickname": "测试用户",
      "role": "student",
      "avatar": null
    }
  }
}
```

### 1.3 获取用户信息

**接口地址**: `GET /user/info`

**请求头**: `Authorization: Bearer {token}`

**响应示例**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": 1,
    "username": "test_user",
    "nickname": "测试用户",
    "avatar": null,
    "role": "student",
    "status": 1,
    "create_time": "2024-01-01 00:00:00"
  }
}
```

### 1.4 更新用户信息

**接口地址**: `PUT /user/update`

**请求头**: `Authorization: Bearer {token}`

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| nickname | string | 否 | 昵称 |
| avatar | string | 否 | 头像URL |

**请求示例**:
```json
{
  "nickname": "新昵称",
  "avatar": "http://example.com/avatar.jpg"
}
```

**响应示例**:
```json
{
  "code": 200,
  "message": "更新成功",
  "data": {
    "id": 1,
    "nickname": "新昵称",
    "avatar": "http://example.com/avatar.jpg"
  }
}
```

### 1.5 修改密码

**接口地址**: `PUT /user/password`

**请求头**: `Authorization: Bearer {token}`

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| old_password | string | 是 | 原密码 |
| new_password | string | 是 | 新密码 |

**请求示例**:
```json
{
  "old_password": "123456",
  "new_password": "654321"
}
```

**响应示例**:
```json
{
  "code": 200,
  "message": "密码修改成功",
  "data": null
}
```

---

## 2. 题目模块

### 2.1 获取题目列表

**接口地址**: `GET /question/list`

**请求头**: `Authorization: Bearer {token}`

**请求参数** (Query):

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| page | int | 否 | 页码，默认1 |
| size | int | 否 | 每页数量，默认10 |
| type | string | 否 | 题目类型：single/multiple/judge/fill |
| category | string | 否 | 题目分类 |
| difficulty | string | 否 | 难度：easy/medium/hard |

**响应示例**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "list": [
      {
        "id": 1,
        "type": "single",
        "category": "数学",
        "content": "1+1等于多少？",
        "options": {
          "A": "1",
          "B": "2",
          "C": "3",
          "D": "4"
        },
        "answer": "B",
        "analysis": "1+1=2",
        "difficulty": "easy",
        "score": 5,
        "creator_id": 1,
        "create_time": "2024-01-01 00:00:00"
      }
    ],
    "total": 100,
    "page": 1,
    "size": 10
  }
}
```

### 2.2 获取题目详情

**接口地址**: `GET /question/{id}`

**请求头**: `Authorization: Bearer {token}`

**路径参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| id | int | 是 | 题目ID |

**响应示例**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": 1,
    "type": "single",
    "category": "数学",
    "content": "1+1等于多少？",
    "options": {
      "A": "1",
      "B": "2",
      "C": "3",
      "D": "4"
    },
    "answer": "B",
    "analysis": "1+1=2",
    "difficulty": "easy",
    "score": 5,
    "creator_id": 1,
    "create_time": "2024-01-01 00:00:00"
  }
}
```

### 2.3 添加题目

**接口地址**: `POST /question/add`

**请求头**: `Authorization: Bearer {token}`

**权限要求**: teacher、admin

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| type | string | 是 | 题目类型：single/multiple/judge/fill |
| category | string | 是 | 题目分类 |
| content | string | 是 | 题目内容 |
| options | object | 否 | 选项（单选/多选需要） |
| answer | string | 是 | 正确答案 |
| analysis | string | 否 | 题目解析 |
| difficulty | string | 是 | 难度：easy/medium/hard |
| score | int | 是 | 分值 |

**请求示例** (单选题):
```json
{
  "type": "single",
  "category": "数学",
  "content": "1+1等于多少？",
  "options": {
    "A": "1",
    "B": "2",
    "C": "3",
    "D": "4"
  },
  "answer": "B",
  "analysis": "1+1=2",
  "difficulty": "easy",
  "score": 5
}
```

**请求示例** (多选题):
```json
{
  "type": "multiple",
  "category": "数学",
  "content": "以下哪些是偶数？",
  "options": {
    "A": "1",
    "B": "2",
    "C": "3",
    "D": "4"
  },
  "answer": "B,D",
  "analysis": "2和4是偶数",
  "difficulty": "medium",
  "score": 10
}
```

**请求示例** (判断题):
```json
{
  "type": "judge",
  "category": "常识",
  "content": "地球是圆的",
  "answer": "true",
  "analysis": "地球是圆的",
  "difficulty": "easy",
  "score": 5
}
```

**请求示例** (填空题):
```json
{
  "type": "fill",
  "category": "语文",
  "content": "床前明月光，疑是____霜",
  "answer": "地上",
  "analysis": "李白《静夜思》",
  "difficulty": "easy",
  "score": 5
}
```

**响应示例**:
```json
{
  "code": 200,
  "message": "添加成功",
  "data": {
    "id": 1
  }
}
```

### 2.4 更新题目

**接口地址**: `PUT /question/{id}`

**请求头**: `Authorization: Bearer {token}`

**权限要求**: teacher、admin

**路径参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| id | int | 是 | 题目ID |

**请求参数**: 同添加题目

**响应示例**:
```json
{
  "code": 200,
  "message": "更新成功",
  "data": null
}
```

### 2.5 删除题目

**接口地址**: `DELETE /question/{id}`

**请求头**: `Authorization: Bearer {token}`

**权限要求**: teacher、admin

**路径参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| id | int | 是 | 题目ID |

**响应示例**:
```json
{
  "code": 200,
  "message": "删除成功",
  "data": null
}
```

### 2.6 批量删除题目

**接口地址**: `DELETE /question/batch`

**请求头**: `Authorization: Bearer {token}`

**权限要求**: teacher、admin

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| ids | array | 是 | 题目ID列表 |

**请求示例**:
```json
{
  "ids": [1, 2, 3]
}
```

**响应示例**:
```json
{
  "code": 200,
  "message": "批量删除成功",
  "data": null
}
```

---

## 3. 试卷模块

### 3.1 获取试卷列表

**接口地址**: `GET /exam/list`

**请求头**: `Authorization: Bearer {token}`

**权限要求**: teacher、admin

**请求参数** (Query):

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| page | int | 否 | 页码，默认1 |
| size | int | 否 | 每页数量，默认10 |
| title | string | 否 | 试卷标题（模糊搜索） |
| status | string | 否 | 状态：draft/published/closed |

**响应示例**:
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
        "create_time": "2024-01-01 00:00:00"
      }
    ],
    "total": 20,
    "page": 1,
    "size": 10
  }
}
```

### 3.2 获取学生可参加的考试列表

**接口地址**: `GET /exam/available`

**请求头**: `Authorization: Bearer {token}`

**权限要求**: student

**响应示例**:
```json
{
  "code": 200,
  "message": "success",
  "data": [
    {
      "id": 1,
      "title": "数学测试卷",
      "description": "第一章测试",
      "duration": 60,
      "total_score": 100,
      "pass_score": 60,
      "start_time": "2024-01-01 10:00:00",
      "end_time": "2024-01-01 12:00:00",
      "status": "published"
    }
  ]
}
```

### 3.3 获取试卷详情

**接口地址**: `GET /exam/{id}`

**请求头**: `Authorization: Bearer {token}`

**路径参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| id | int | 是 | 试卷ID |

**响应示例**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
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
    "question_ids": [1, 2, 3],
    "questions": [
      {
        "id": 1,
        "type": "single",
        "content": "1+1等于多少？",
        "options": {
          "A": "1",
          "B": "2",
          "C": "3",
          "D": "4"
        },
        "score": 5
      }
    ],
    "create_time": "2024-01-01 00:00:00"
  }
}
```

### 3.4 创建试卷

**接口地址**: `POST /exam/add`

**请求头**: `Authorization: Bearer {token}`

**权限要求**: teacher、admin

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| title | string | 是 | 试卷标题 |
| description | string | 否 | 试卷描述 |
| duration | int | 是 | 考试时长（分钟） |
| total_score | int | 是 | 总分 |
| pass_score | int | 是 | 及格分数 |
| start_time | string | 否 | 考试开始时间 |
| end_time | string | 否 | 考试结束时间 |
| is_random | int | 是 | 是否随机组卷：0否 1是 |
| question_ids | array | 是 | 题目ID列表 |

**请求示例**:
```json
{
  "title": "数学测试卷",
  "description": "第一章测试",
  "duration": 60,
  "total_score": 100,
  "pass_score": 60,
  "start_time": "2024-01-01 10:00:00",
  "end_time": "2024-01-01 12:00:00",
  "is_random": 0,
  "question_ids": [1, 2, 3, 4, 5]
}
```

**响应示例**:
```json
{
  "code": 200,
  "message": "创建成功",
  "data": {
    "id": 1
  }
}
```

### 3.5 更新试卷

**接口地址**: `PUT /exam/{id}`

**请求头**: `Authorization: Bearer {token}`

**权限要求**: teacher、admin

**路径参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| id | int | 是 | 试卷ID |

**请求参数**: 同创建试卷

**响应示例**:
```json
{
  "code": 200,
  "message": "更新成功",
  "data": null
}
```

### 3.6 删除试卷

**接口地址**: `DELETE /exam/{id}`

**请求头**: `Authorization: Bearer {token}`

**权限要求**: teacher、admin

**路径参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| id | int | 是 | 试卷ID |

**响应示例**:
```json
{
  "code": 200,
  "message": "删除成功",
  "data": null
}
```

### 3.7 发布试卷

**接口地址**: `PUT /exam/{id}/publish`

**请求头**: `Authorization: Bearer {token}`

**权限要求**: teacher、admin

**路径参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| id | int | 是 | 试卷ID |

**响应示例**:
```json
{
  "code": 200,
  "message": "发布成功",
  "data": null
}
```

### 3.8 关闭试卷

**接口地址**: `PUT /exam/{id}/close`

**请求头**: `Authorization: Bearer {token}`

**权限要求**: teacher、admin

**路径参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| id | int | 是 | 试卷ID |

**响应示例**:
```json
{
  "code": 200,
  "message": "关闭成功",
  "data": null
}
```

---

## 4. 考试模块

### 4.1 开始考试

**接口地址**: `POST /exam/start`

**请求头**: `Authorization: Bearer {token}`

**权限要求**: student

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| exam_id | int | 是 | 试卷ID |

**请求示例**:
```json
{
  "exam_id": 1
}
```

**响应示例**:
```json
{
  "code": 200,
  "message": "考试开始",
  "data": {
    "id": 1,
    "exam_id": 1,
    "user_id": 1,
    "status": "in_progress",
    "start_time": "2024-01-01 10:00:00"
  }
}
```

### 4.2 获取考试题目

**接口地址**: `GET /exam/{exam_id}/questions`

**请求头**: `Authorization: Bearer {token}`

**权限要求**: student

**路径参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| exam_id | int | 是 | 试卷ID |

**响应示例**:
```json
{
  "code": 200,
  "message": "success",
  "data": [
    {
      "id": 1,
      "type": "single",
      "category": "数学",
      "content": "1+1等于多少？",
      "options": {
        "A": "1",
        "B": "2",
        "C": "3",
        "D": "4"
      },
      "score": 5
    }
  ]
}
```

### 4.3 保存答案

**接口地址**: `POST /exam/answer`

**请求头**: `Authorization: Bearer {token}`

**权限要求**: student

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| exam_record_id | int | 是 | 考试记录ID |
| question_id | int | 是 | 题目ID |
| user_answer | string | 是 | 用户答案 |

**请求示例** (单选题):
```json
{
  "exam_record_id": 1,
  "question_id": 1,
  "user_answer": "B"
}
```

**请求示例** (多选题):
```json
{
  "exam_record_id": 1,
  "question_id": 2,
  "user_answer": "A,B,D"
}
```

**请求示例** (判断题):
```json
{
  "exam_record_id": 1,
  "question_id": 3,
  "user_answer": "true"
}
```

**请求示例** (填空题):
```json
{
  "exam_record_id": 1,
  "question_id": 4,
  "user_answer": "地上"
}
```

**响应示例**:
```json
{
  "code": 200,
  "message": "答案保存成功",
  "data": null
}
```

### 4.4 提交试卷

**接口地址**: `POST /exam/submit`

**请求头**: `Authorization: Bearer {token}`

**权限要求**: student

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| exam_record_id | int | 是 | 考试记录ID |

**请求示例**:
```json
{
  "exam_record_id": 1
}
```

**响应示例**:
```json
{
  "code": 200,
  "message": "试卷提交成功",
  "data": {
    "id": 1,
    "score": 85,
    "is_passed": 1,
    "status": "graded",
    "submit_time": "2024-01-01 11:00:00"
  }
}
```

---

## 5. 考试记录模块

### 5.1 获取考试记录列表

**接口地址**: `GET /exam/record/list`

**请求头**: `Authorization: Bearer {token}`

**请求参数** (Query):

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| page | int | 否 | 页码，默认1 |
| size | int | 否 | 每页数量，默认10 |
| title | string | 否 | 试卷标题（模糊搜索） |
| status | string | 否 | 状态：not_started/in_progress/submitted/graded |

**响应示例**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "list": [
      {
        "id": 1,
        "exam": {
          "id": 1,
          "title": "数学测试卷"
        },
        "user_id": 1,
        "score": 85,
        "is_passed": 1,
        "status": "graded",
        "start_time": "2024-01-01 10:00:00",
        "submit_time": "2024-01-01 11:00:00"
      }
    ],
    "total": 50,
    "page": 1,
    "size": 10
  }
}
```

### 5.2 获取考试记录详情

**接口地址**: `GET /exam/record/{id}`

**请求头**: `Authorization: Bearer {token}`

**路径参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| id | int | 是 | 记录ID |

**响应示例**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": 1,
    "exam": {
      "id": 1,
      "title": "数学测试卷",
      "duration": 60,
      "total_score": 100,
      "pass_score": 60
    },
    "user_id": 1,
    "score": 85,
    "is_passed": 1,
    "status": "graded",
    "start_time": "2024-01-01 10:00:00",
    "submit_time": "2024-01-01 11:00:00",
    "answers": [
      {
        "id": 1,
        "question": {
          "id": 1,
          "type": "single",
          "content": "1+1等于多少？",
          "options": {
            "A": "1",
            "B": "2",
            "C": "3",
            "D": "4"
          },
          "answer": "B",
          "analysis": "1+1=2",
          "score": 5
        },
        "user_answer": "B",
        "is_correct": 1,
        "score": 5
      }
    ]
  }
}
```

---

## 6. 统计模块

### 6.1 获取考试统计

**接口地址**: `GET /exam/{exam_id}/statistics`

**请求头**: `Authorization: Bearer {token}`

**权限要求**: teacher、admin

**路径参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| exam_id | int | 是 | 试卷ID |

**响应示例**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "total_participants": 30,
    "average_score": 78.5,
    "pass_rate": 0.8,
    "max_score": 100,
    "min_score": 45,
    "question_stats": [
      {
        "question_id": 1,
        "correct_rate": 0.9
      }
    ]
  }
}
```

---

## 注意事项

1. 所有需要认证的接口都需要在请求头中携带 `Authorization: Bearer {token}`
2. 日期时间格式统一为 `YYYY-MM-DD HH:mm:ss`
3. 分页从第1页开始
4. 多选题的答案需要用逗号分隔，如 `A,B,D`
5. 判断题的答案为 `true` 或 `false`
6. 试卷状态流转：draft -> published -> closed
7. 考试记录状态流转：not_started -> in_progress -> submitted -> graded