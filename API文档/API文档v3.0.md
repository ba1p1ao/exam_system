# 在线考试系统 API 接口文档

## 版本说明

**版本**: v3.0  
**发布日期**: 2026-01-04  
**更新内容**: 整合所有模块接口，确保文档与前端API调用完全一致

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

**接口地址**: `POST /user/register/`

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

**接口地址**: `POST /user/login/`

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

**接口地址**: `GET /user/info/`

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

**接口地址**: `PUT /user/update/`

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

**接口地址**: `PUT /user/password/`

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

**接口地址**: `GET /question/list/`

**请求头**: `Authorization: Bearer {token}`

**请求参数** (Query):

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| page | int | 否 | 页码，默认1 |
| size | int | 否 | 每页数量，默认10 |
| type | string | 否 | 题目类型：single/multiple/judge/fill |
| content | string | 否 | 题目内容（模糊搜索） |
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

**接口地址**: `GET /question/{id}/`

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

**接口地址**: `POST /question/add/`

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

**接口地址**: `PUT /question/{id}/`

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

**接口地址**: `DELETE /question/{id}/`

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

**接口地址**: `DELETE /question/batch/`

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

### 2.7 批量导入题目

**接口地址**: `POST /question/import/`

**请求头**: `Authorization: Bearer {token}`

**权限要求**: teacher、admin

**请求参数**: multipart/form-data

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| file | file | 是 | Excel 文件 |

**响应示例**:
```json
{
  "code": 200,
  "message": "导入成功",
  "data": {
    "total": 50,
    "success": 48,
    "failed": 2,
    "failed_list": [
      {
        "row": 3,
        "reason": "题目类型不正确"
      },
      {
        "row": 15,
        "reason": "缺少必填字段"
      }
    ]
  }
}
```

### 2.8 导出题目

**接口地址**: `POST /question/export/`

**请求头**: `Authorization: Bearer {token}`

**权限要求**: teacher、admin

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| type | string | 否 | 题目类型筛选 |
| category | string | 否 | 题目分类筛选 |
| difficulty | string | 否 | 难度筛选 |
| ids | array | 否 | 指定题目ID列表 |

**请求示例**:
```json
{
  "type": "single",
  "category": "数学",
  "ids": [1, 2, 3]
}
```

**响应**: Excel 文件下载

---

## 3. 试卷模块

### 3.1 获取试卷列表

**接口地址**: `GET /exam/list/`

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

**接口地址**: `GET /exam/available/`

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

**接口地址**: `GET /exam/{id}/`

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

**接口地址**: `POST /exam/add/`

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

**接口地址**: `PUT /exam/{id}/`

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

**接口地址**: `DELETE /exam/{id}/`

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

**接口地址**: `PUT /exam/{id}/publish/`

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

**接口地址**: `PUT /exam/{id}/close/`

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

**接口地址**: `POST /exam/start/`

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
  "message": "success",
  "data": {
    "id": 1,
    "exam_id": 1,
    "user_id": 1,
    "status": "in_progress",
    "start_time": "2024-01-01 10:00:00",
    "duration": 60
  }
}
```

### 4.2 获取考试题目

**接口地址**: `GET /exam/{exam_id}/questions/`

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
  "data": {
    "questions": [
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
        "score": 5,
        "difficulty": "easy"
      }
    ],
    "exam_record_id": 1,
    "saved_answers": {
      "1": "B"
    }
  }
}
```

### 4.3 保存答案

**接口地址**: `POST /exam/answer/`

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

**接口地址**: `POST /exam/submit/`

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

**接口地址**: `GET /exam/record/list/`

**请求头**: `Authorization: Bearer {token}`

**请求参数** (Query):

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| page | int | 否 | 页码，默认1 |
| size | int | 否 | 每页数量，默认10 |
| status | string | 否 | 状态：not_started/in_progress/submitted/graded |
| title | string | 否 | 试卷标题（模糊搜索） |

**响应示例**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "list": [
      {
        "id": 1,
        "exam_id": 1,
        "exam_title": "数学测试卷",
        "exam_total_score": 100,
        "exam_pass_score": 60,
        "exam_duration": 60,
        "user_id": 1,
        "score": 85,
        "is_passed": 1,
        "status": "graded",
        "start_time": "2024-01-01 10:00:00",
        "submit_time": "2024-01-01 11:00:00",
        "duration": 60,
        "total_score": 100,
        "pass_score": 60
      }
    ],
    "total": 50,
    "page": 1,
    "size": 10
  }
}
```

### 5.2 获取考试记录详情

**接口地址**: `GET /exam/record/{id}/`

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

### 5.3 获取按考试分组的考试记录

**接口地址**: `GET /exam/grouped-records/`

**请求头**: `Authorization: Bearer {token}`

**权限要求**: teacher、admin

**请求参数** (Query):

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| page | int | 否 | 页码，默认1 |
| size | int | 否 | 每页数量，默认10 |
| title | string | 否 | 试卷标题（模糊搜索） |
| status | string | 否 | 试卷状态：draft/published/closed |

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

---

## 6. 统计模块

### 6.1 获取考试统计

**接口地址**: `GET /exam/{exam_id}/statistics/`

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

**字段说明**:
- `total_participants`: 参加考试人数（去重统计）
- `average_score`: 平均分（保留两位小数，无数据时为 null）
- `pass_rate`: 及格率（0-1之间的小数，无数据时为 null）
- `max_score`: 最高分
- `min_score`: 最低分
- `question_stats`: 题目正确率统计数组
  - `question_id`: 题目ID
  - `correct_rate`: 正确率（0-1之间的小数）

### 6.2 获取系统统计数据

**接口地址**: `GET /exam/statistics/`

**请求头**: `Authorization: Bearer {token}`

**权限要求**: teacher、admin

**响应示例**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "total_users": 100,
    "total_questions": 500,
    "total_exams": 20,
    "total_records": 1000
  }
}
```

### 6.3 获取考试排名

**接口地址**: `GET /exam/{exam_id}/ranking/`

**请求头**: `Authorization: Bearer {token}`

**权限要求**: 所有角色

**路径参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| exam_id | int | 是 | 试卷ID |

**请求参数** (Query):

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| page | int | 否 | 页码，默认1 |
| size | int | 否 | 每页数量，默认10 |
| class_id | int | 否 | 班级ID（仅教师/管理员可用） |

**响应示例**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "exam_id": 1,
    "exam_title": "数学测试卷",
    "total_participants": 100,
    "my_rank": 5,
    "my_score": 95,
    "list": [
      {
        "rank": 1,
        "user_id": 10,
        "username": "student1",
        "nickname": "学霸",
        "score": 100,
        "is_passed": 1,
        "submit_time": "2024-01-01 10:30:00"
      },
      {
        "rank": 2,
        "user_id": 20,
        "username": "student2",
        "nickname": "学神",
        "score": 98,
        "is_passed": 1,
        "submit_time": "2024-01-01 10:35:00"
      }
    ],
    "total": 100,
    "page": 1,
    "size": 10
  }
}
```

---

## 7. 班级管理模块

### 7.1 获取班级列表（管理员）

**接口地址**: `GET /class/list/`

**请求头**: `Authorization: Bearer {token}`

**权限要求**: admin、teacher

**请求参数** (Query):

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| page | int | 否 | 页码，默认1 |
| size | int | 否 | 每页数量，默认10 |
| name | string | 否 | 班级名称（模糊搜索） |
| grade | string | 否 | 年级筛选 |
| status | int | 否 | 状态：1正常 0禁用 |

**响应示例**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "list": [
      {
        "id": 1,
        "name": "三年二班",
        "grade": "三年级",
        "head_teacher_id": 2,
        "head_teacher_name": "张老师",
        "student_count": 45,
        "status": 1,
        "create_time": "2024-01-01 00:00:00"
      },
      {
        "id": 2,
        "name": "三年三班",
        "grade": "三年级",
        "head_teacher_id": 3,
        "head_teacher_name": "李老师",
        "student_count": 42,
        "status": 1,
        "create_time": "2024-01-01 00:00:00"
      }
    ],
    "total": 20,
    "page": 1,
    "size": 10
  }
}
```

### 7.2 获取教师管理的班级列表

**接口地址**: `GET /teacher/classes/`

**请求头**: `Authorization: Bearer {token}`

**权限要求**: teacher

**请求参数** (Query):

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| page | int | 否 | 页码，默认1 |
| size | int | 否 | 每页数量，默认10 |
| name | string | 否 | 班级名称（模糊搜索） |
| grade | string | 否 | 年级筛选 |
| status | int | 否 | 状态：1正常 0禁用 |

**响应示例**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "list": [
      {
        "id": 1,
        "name": "三年二班",
        "grade": "三年级",
        "head_teacher_id": 2,
        "head_teacher_name": "张老师",
        "student_count": 45,
        "status": 1,
        "create_time": "2024-01-01 00:00:00"
      }
    ],
    "total": 1,
    "page": 1,
    "size": 10
  }
}
```

### 7.3 获取班级详情

**接口地址**: `GET /class/{class_id}/`

**请求头**: `Authorization: Bearer {token}`

**权限要求**: admin、teacher

**路径参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| class_id | int | 是 | 班级ID |

**响应示例**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": 1,
    "name": "三年二班",
    "grade": "三年级",
    "head_teacher_id": 2,
    "head_teacher_name": "张老师",
    "student_count": 45,
    "exam_count": 10,
    "average_score": 85.5,
    "status": 1,
    "create_time": "2024-01-01 00:00:00"
  }
}
```

### 7.4 创建班级

**接口地址**: `POST /class/create/`

**请求头**: `Authorization: Bearer {token}`

**权限要求**: admin

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| name | string | 是 | 班级名称 |
| grade | string | 否 | 年级 |
| head_teacher_id | int | 否 | 班主任ID |

**请求示例**:
```json
{
  "name": "三年四班",
  "grade": "三年级",
  "head_teacher_id": 4
}
```

**响应示例**:
```json
{
  "code": 200,
  "message": "班级创建成功",
  "data": {
    "id": 3,
    "name": "三年四班",
    "grade": "三年级",
    "head_teacher_id": 4,
    "status": 1,
    "create_time": "2024-01-02 10:00:00"
  }
}
```

### 7.5 更新班级信息

**接口地址**: `PUT /class/{class_id}/`

**请求头**: `Authorization: Bearer {token}`

**权限要求**: admin

**路径参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| class_id | int | 是 | 班级ID |

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| name | string | 否 | 班级名称 |
| grade | string | 否 | 年级 |
| head_teacher_id | int | 否 | 班主任ID |

**请求示例**:
```json
{
  "name": "三年四班（更新）",
  "grade": "三年级",
  "head_teacher_id": 5
}
```

**响应示例**:
```json
{
  "code": 200,
  "message": "班级信息更新成功",
  "data": null
}
```

### 7.6 删除班级

**接口地址**: `DELETE /class/{class_id}/`

**请求头**: `Authorization: Bearer {token}`

**权限要求**: admin

**路径参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| class_id | int | 是 | 班级ID |

**响应示例**:
```json
{
  "code": 200,
  "message": "班级删除成功",
  "data": null
}
```

### 7.7 更新班级状态

**接口地址**: `PUT /class/{class_id}/status/`

**请求头**: `Authorization: Bearer {token}`

**权限要求**: admin

**路径参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| class_id | int | 是 | 班级ID |

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| status | int | 是 | 状态：1正常 0禁用 |

**请求示例**:
```json
{
  "status": 0
}
```

**响应示例**:
```json
{
  "code": 200,
  "message": "班级状态更新成功",
  "data": null
}
```

### 7.8 获取班级成员列表

**接口地址**: `GET /class/{class_id}/members/`

**请求头**: `Authorization: Bearer {token}`

**权限要求**: admin、teacher

**路径参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| class_id | int | 是 | 班级ID |

**请求参数** (Query):

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| page | int | 否 | 页码，默认1 |
| size | int | 否 | 每页数量，默认10 |
| role | string | 否 | 角色筛选：student/teacher |

**响应示例**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "class_id": 1,
    "class_name": "三年二班",
    "list": [
      {
        "id": 10,
        "username": "student1",
        "nickname": "张三",
        "role": "student",
        "avatar": null,
        "status": 1,
        "join_time": "2024-01-01 00:00:00"
      },
      {
        "id": 2,
        "username": "teacher1",
        "nickname": "张老师",
        "role": "teacher",
        "avatar": null,
        "status": 1,
        "join_time": "2024-01-01 00:00:00"
      }
    ],
    "total": 47,
    "page": 1,
    "size": 10
  }
}
```

### 7.9 添加学生到班级

**接口地址**: `POST /class/{class_id}/members/add/`

**请求头**: `Authorization: Bearer {token}`

**权限要求**: admin、teacher

**路径参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| class_id | int | 是 | 班级ID |

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| user_ids | array | 是 | 用户ID列表 |

**请求示例**:
```json
{
  "user_ids": [11, 12, 13]
}
```

**响应示例**:
```json
{
  "code": 200,
  "message": "添加成功",
  "data": {
    "success_count": 3,
    "failed_count": 0,
    "failed_list": []
  }
}
```

### 7.10 从班级移除学生

**接口地址**: `DELETE /class/{class_id}/members/remove/`

**请求头**: `Authorization: Bearer {token}`

**权限要求**: admin、teacher

**路径参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| class_id | int | 是 | 班级ID |

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| user_ids | array | 是 | 用户ID列表 |

**请求示例**:
```json
{
  "user_ids": [11, 12, 13]
}
```

**响应示例**:
```json
{
  "code": 200,
  "message": "移除成功",
  "data": {
    "success_count": 3,
    "failed_count": 0,
    "failed_list": []
  }
}
```

### 7.11 获取可选学生列表（未加入班级的学生）

**接口地址**: `GET /class/{class_id}/available-students/`

**请求头**: `Authorization: Bearer {token}`

**权限要求**: admin、teacher

**路径参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| class_id | int | 是 | 班级ID |

**请求参数** (Query):

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| keyword | string | 否 | 搜索关键词（用户名/昵称） |

**响应示例**:
```json
{
  "code": 200,
  "message": "success",
  "data": [
    {
      "id": 20,
      "username": "student20",
      "nickname": "王五",
      "role": "student",
      "status": 1
    },
    {
      "id": 21,
      "username": "student21",
      "nickname": "赵六",
      "role": "student",
      "status": 1
    }
  ]
}
```

### 7.12 获取班级成绩统计

**接口地址**: `GET /class/{class_id}/statistics/`

**请求头**: `Authorization: Bearer {token}`

**权限要求**: admin、teacher

**路径参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| class_id | int | 是 | 班级ID |

**响应示例**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "class_id": 1,
    "class_name": "三年二班",
    "student_count": 45,
    "exam_count": 10,
    "average_score": 85.5,
    "highest_score": 100,
    "lowest_score": 60,
    "pass_rate": 0.9,
    "excellent_rate": 0.6,
    "score_distribution": {
      "0-59": 5,
      "60-69": 10,
      "70-79": 15,
      "80-89": 20,
      "90-100": 25
    }
  }
}
```

### 7.13 获取所有班级（用于下拉选择）

**接口地址**: `GET /class/options/`

**请求头**: `Authorization: Bearer {token}`

**权限要求**: admin、teacher

**响应示例**:
```json
{
  "code": 200,
  "message": "success",
  "data": [
    {
      "id": 1,
      "name": "三年二班",
      "grade": "三年级"
    },
    {
      "id": 2,
      "name": "三年三班",
      "grade": "三年级"
    }
  ]
}
```

### 7.14 获取学生所在班级信息

**接口地址**: `GET /student/class`

**请求头**: `Authorization: Bearer {token}`

**权限要求**: student

**响应示例**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": 1,
    "name": "三年二班",
    "grade": "三年级",
    "head_teacher_name": "张老师",
    "student_count": 45,
    "my_rank": 5,
    "join_time": "2024-01-01 00:00:00"
  }
}
```

---

## 8. 用户管理模块（管理员专用）

### 8.1 获取用户列表

**接口地址**: `GET /admin/users/`

**请求头**: `Authorization: Bearer {token}`

**权限要求**: admin

**请求参数** (Query):

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| page | int | 否 | 页码，默认1 |
| size | int | 否 | 每页数量，默认10 |
| username | string | 否 | 用户名（模糊搜索） |
| nickname | string | 否 | 昵称（模糊搜索） |
| role | string | 否 | 角色：student/teacher/admin |
| status | int | 否 | 状态：1正常 0禁用 |
| class_id | int | 否 | 班级ID |

**响应示例**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "list": [
      {
        "id": 1,
        "username": "admin",
        "nickname": "管理员",
        "avatar": null,
        "role": "admin",
        "status": 1,
        "class_name": null,
        "create_time": "2024-01-01 00:00:00"
      },
      {
        "id": 2,
        "username": "teacher1",
        "nickname": "张老师",
        "avatar": null,
        "role": "teacher",
        "status": 1,
        "class_name": "三年二班",
        "create_time": "2024-01-01 00:00:00"
      }
    ],
    "total": 100,
    "page": 1,
    "size": 10
  }
}
```

### 8.2 获取用户详情

**接口地址**: `GET /admin/users/{user_id}/`

**请求头**: `Authorization: Bearer {token}`

**权限要求**: admin

**路径参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| user_id | int | 是 | 用户ID |

**响应示例**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": 1,
    "username": "teacher1",
    "nickname": "张老师",
    "avatar": null,
    "role": "teacher",
    "status": 1,
    "create_time": "2024-01-01 00:00:00",
    "exam_count": 10,
    "question_count": 50,
    "record_count": 20
  }
}
```

### 8.3 更新用户状态

**接口地址**: `PUT /admin/users/{user_id}/status/`

**请求头**: `Authorization: Bearer {token}`

**权限要求**: admin

**路径参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| user_id | int | 是 | 用户ID |

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| status | int | 是 | 状态：1正常 0禁用 |

**请求示例**:
```json
{
  "status": 0
}
```

**响应示例**:
```json
{
  "code": 200,
  "message": "用户状态更新成功",
  "data": null
}
```

### 8.4 更新用户角色

**接口地址**: `PUT /admin/users/{user_id}/role/`

**请求头**: `Authorization: Bearer {token}`

**权限要求**: admin

**路径参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| user_id | int | 是 | 用户ID |

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| role | string | 是 | 角色：student/teacher/admin |

**请求示例**:
```json
{
  "role": "teacher"
}
```

**响应示例**:
```json
{
  "code": 200,
  "message": "用户角色更新成功",
  "data": null
}
```

### 8.5 删除用户

**接口地址**: `DELETE /admin/users/{user_id}/`

**请求头**: `Authorization: Bearer {token}`

**权限要求**: admin

**路径参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| user_id | int | 是 | 用户ID |

**响应示例**:
```json
{
  "code": 200,
  "message": "用户删除成功",
  "data": null
}
```

### 8.6 获取用户统计数据

**接口地址**: `GET /admin/users/statistics/`

**请求头**: `Authorization: Bearer {token}`

**权限要求**: admin

**响应示例**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "total_users": 100,
    "student_count": 80,
    "teacher_count": 15,
    "admin_count": 5,
    "active_users": 95,
    "disabled_users": 5
  }
}
```

---

## 9. 学生模块

### 9.1 获取学生个人成绩趋势

**接口地址**: `GET /student/score/trend/`

**请求头**: `Authorization: Bearer {token}`

**权限要求**: student

**请求参数** (Query):

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| days | int | 否 | 统计天数，默认30 |

**响应示例**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "total_exams": 10,
    "average_score": 85.5,
    "highest_score": 100,
    "lowest_score": 70,
    "pass_rate": 0.9,
    "trend": [
      {
        "date": "2024-01-01",
        "exam_title": "数学测试",
        "score": 85
      },
      {
        "date": "2024-01-05",
        "exam_title": "语文测试",
        "score": 90
      }
    ]
  }
}
```

---

## 10. 错题本模块（前端已实现，后端待实现）
获取错题列表和统计（合并接口）

  接口地址: GET /mistake/list-with-statistics/

  请求头: Authorization: Bearer {token}

  权限要求: student

  请求参数 (Query):


  ┌──────────┬────────┬──────┬──────────────────┐
  │ 参数名   │ 类型   │ 必填 │ 说明             │
  ├──────────┼────────┼──────┼──────────────────┤
  │ page     │ int    │ 否   │ 页码，默认1      │
  │ size     │ int    │ 否   │ 每页数量，默认10 │
  │ type     │ string │ 否   │ 题目类型筛选     │
  │ category │ string │ 否   │ 题目分类筛选     │
  └──────────┴────────┴──────┴──────────────────┘

  响应示例:
    1 {
    2   "code": 200,
    3   "message": "success",
    4   "data": {
    5     "list": [
    6       {
    7         "id": 1,
    8         "question_id": 10,
    9         "type": "single",
   10         "category": "数学",
   11         "content": "1+1等于多少？",
   12         "options": {
   13           "A": "1",
   14           "B": "2",
   15           "C": "3",
   16           "D": "4"
   17         },
   18         "user_answer": "A",
   19         "correct_answer": "B",
   20         "analysis": "1+1=2",
   21         "mistake_count": 2,
   22         "last_mistake_time": "2024-01-01 10:00:00",
   23         "exam_title": "数学测试卷"
   24       }
   25     ],
   26     "statistics": {
   27       "total_mistakes": 100,
   28       "unique_questions": 50,
   29       "type_distribution": {
   30         "single": 30,
   31         "multiple": 20,
   32         "judge": 25,
   33         "fill": 25
   34       },
   35       "category_distribution": {
   36         "数学": 40,
   37         "语文": 20,
   38         "英语": 30,
   39         "物理": 10
   40       },
   41       "recent_mistakes": [
   42         {
   43           "question_id": 10,
   44           "mistake_count": 3,
   45           "last_mistake_time": "2024-01-01 10:00:00"
   46         }
   47       ]
   48     },
   49     "total": 50,
   50     "page": 1,
   51     "size": 10
   52   }
   53 }
### 10.3 标记错题为已掌握

**接口地址**: `PUT /mistake/{mistake_id}/mastered/`

**请求头**: `Authorization: Bearer {token}`

**权限要求**: student

**路径参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| mistake_id | int | 是 | 错题ID |

**响应示例**:
```json
{
  "code": 200,
  "message": "标记成功",
  "data": null
}
```

### 10.4 导出错题本

**接口地址**: `POST /mistake/export/`

**请求头**: `Authorization: Bearer {token}`

**权限要求**: student

**响应**: Excel 文件下载

---

## 11. 防作弊模块（前端已实现，后端待实现）

### 11.1 记录考试行为

**接口地址**: `POST /exam/behavior/log/`

**请求头**: `Authorization: Bearer {token}`

**权限要求**: student

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| exam_record_id | int | 是 | 考试记录ID |
| behavior_type | string | 是 | 行为类型：focus_loss/copy_paste/tab_switch/fullscreen_exit |
| behavior_detail | string | 否 | 行为详情 |
| timestamp | string | 是 | 时间戳 |

**请求示例**:
```json
{
  "exam_record_id": 1,
  "behavior_type": "focus_loss",
  "behavior_detail": "失去焦点5次",
  "timestamp": "2024-01-01 10:30:00"
}
```

**响应示例**:
```json
{
  "code": 200,
  "message": "行为记录成功",
  "data": null
}
```

### 11.2 获取考试行为记录

**接口地址**: `GET /exam/{exam_record_id}/behavior/logs/`

**请求头**: `Authorization: Bearer {token}`

**权限要求**: teacher、admin

**路径参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| exam_record_id | int | 是 | 考试记录ID |

**响应示例**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "exam_record_id": 1,
    "student_name": "张三",
    "exam_title": "数学测试",
    "total_behaviors": 15,
    "focus_loss_count": 5,
    "copy_paste_count": 3,
    "tab_switch_count": 5,
    "fullscreen_exit_count": 2,
    "logs": [
      {
        "id": 1,
        "behavior_type": "focus_loss",
        "behavior_detail": "失去焦点",
        "timestamp": "2024-01-01 10:30:00"
      }
    ]
  }
}
```

---

## 12. 数据可视化模块（前端已实现，后端待实现）

### 12.1 获取考试成绩分布图数据

**接口地址**: `GET /exam/{exam_id}/chart/score-distribution/`

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
    "exam_id": 1,
    "exam_title": "数学测试卷",
    "distribution": {
      "0-59": 5,
      "60-69": 15,
      "70-79": 25,
      "80-89": 30,
      "90-100": 25
    },
    "total": 100
  }
}
```

### 12.2 获取题目正确率图数据

**接口地址**: `GET /exam/{exam_id}/chart/question-correctness/`

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
    "exam_id": 1,
    "questions": [
      {
        "question_id": 1,
        "question_content": "1+1等于多少？",
        "correct_count": 95,
        "incorrect_count": 5,
        "correct_rate": 0.95
      },
      {
        "question_id": 2,
        "question_content": "2+2等于多少？",
        "correct_count": 80,
        "incorrect_count": 20,
        "correct_rate": 0.8
      }
    ]
  }
}
```

### 12.3 获取学生成绩对比图数据

**接口地址**: `GET /student/chart/score-comparison/`


**权限要求**: student

**响应示例**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "my_scores": [85, 90, 88, 92, 95],
    "class_average": [75, 78, 80, 82, 85],
    "exam_titles": ["数学测试1", "数学测试2", "数学测试3", "数学测试4", "数学测试5"]
  }
}
```

---

## 13. 考试分析报告模块（前端已实现，后端待实现）

### 13.1 生成考试分析报告

**接口地址**: `POST /exam/{exam_id}/report/generate/`

**请求头**: `Authorization: Bearer {token}`

**权限要求**: teacher、admin

**路径参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| exam_id | int | 是 | 试卷ID |

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| include_charts | boolean | 否 | 是否包含图表，默认true |
| include_ranking | boolean | 否 | 是否包含排名，默认true |

**响应示例**:
```json
{
  "code": 200,
  "message": "报告生成成功",
  "data": {
    "report_id": 1,
    "exam_id": 1,
    "exam_title": "数学测试卷",
    "generate_time": "2024-01-01 12:00:00",
    "summary": {
      "total_participants": 100,
      "average_score": 78.5,
      "pass_rate": 0.8,
      "highest_score": 100,
      "lowest_score": 45
    },
    "question_analysis": [
      {
        "question_id": 1,
        "correct_rate": 0.95,
        "difficulty_level": "easy"
      }
    ],
    "recommendations": [
      "题目2正确率较低，建议加强相关知识点的讲解",
      "整体成绩良好，继续保持"
    ]
  }
}
```

### 13.2 导出考试分析报告（PDF）

**接口地址**: `GET /exam/{exam_id}/report/export/`

**请求头**: `Authorization: Bearer {token}`

**权限要求**: teacher、admin

**路径参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| exam_id | int | 是 | 试卷ID |

**响应**: PDF 文件下载

### 13.3 发送成绩单邮件

**接口地址**: `POST /exam/{exam_id}/report/email/`

**请求头**: `Authorization: Bearer {token}`

**权限要求**: teacher、admin

**路径参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| exam_id | int | 是 | 试卷ID |

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| user_ids | array | 否 | 学生ID列表，不传则发送给所有学生 |

**请求示例**:
```json
{
  "user_ids": [1, 2, 3]
}
```

**响应示例**:
```json
{
  "code": 200,
  "message": "成绩单发送成功",
  "data": {
    "total_sent": 3,
    "success": 3,
    "failed": 0
  }
}
```

### 13.4 自动提交试卷

**接口地址**: `POST /exam/auto-submit/`

**请求头**: `Authorization: Bearer {token}`

**权限要求**: student

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| exam_record_id | int | 是 | 考试记录ID |

**响应示例**:
```json
{
  "code": 200,
  "message": "考试时间已到，试卷自动提交成功",
  "data": {
    "id": 1,
    "score": 85,
    "is_passed": 1,
    "status": "graded",
    "submit_time": "2024-01-01 11:00:00",
    "auto_submitted": true
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

---

## 功能清单

✅ 用户模块
- 用户注册、登录、信息管理
- 密码修改

✅ 题目模块
- 题目增删改查
- 题目批量删除
- 题目导入导出

✅ 试卷模块
- 试卷创建、编辑、发布、关闭
- 试卷详情查看

✅ 考试模块
- 开始考试、保存答案、提交试卷
- 获取考试题目

✅ 考试记录模块
- 考试记录列表（学生/教师/管理员）
- 考试记录详情
- 按考试分组的考试记录（教师/管理员）

✅ 统计模块
- 考试统计
- 系统统计
- 考试排名

✅ 班级管理模块
- 班级增删改查
- 班级成员管理
- 班级成绩统计
- 教师班级查询
- 学生班级查询

✅ 用户管理模块（管理员专用）
- 用户列表查询
- 用户状态管理
- 用户角色管理
- 用户删除功能
- 用户统计数据

✅ 学生模块
- 学生个人成绩趋势

🔲 错题本模块（前端已实现，后端待实现）
- 获取错题列表
- 获取错题统计
- 标记错题为已掌握
- 导出错题本

🔲 防作弊模块（前端已实现，后端待实现）
- 记录考试行为
- 获取考试行为记录

🔲 数据可视化模块（前端已实现，后端待实现）
- 获取考试成绩分布图数据
- 获取题目正确率图数据
- 获取学生成绩对比图数据

🔲 考试分析报告模块（前端已实现，后端待实现）
- 生成考试分析报告
- 导出考试分析报告（PDF）
- 发送成绩单邮件
- 自动提交试卷

---

## 联系方式

如有问题或建议，请联系开发团队。
