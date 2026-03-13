# 在线考试系统 API 接口文档 v2.0

## 版本说明

**版本**: v2.0  
**发布日期**: 2025-12-31  
**更新内容**: 新增用户管理、题目导入导出、防作弊、错题本、成绩排名、数据可视化等功能

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

## v2.0 新增功能模块

### 8. 用户管理模块（管理员专用）

#### 8.1 获取用户列表

**接口地址**: `GET /admin/users`

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
        "create_time": "2024-01-01 00:00:00"
      },
      {
        "id": 2,
        "username": "teacher1",
        "nickname": "张老师",
        "avatar": null,
        "role": "teacher",
        "status": 1,
        "create_time": "2024-01-01 00:00:00"
      }
    ],
    "total": 100,
    "page": 1,
    "size": 10
  }
}
```

#### 8.2 获取用户详情

**接口地址**: `GET /admin/users/{id}`

**请求头**: `Authorization: Bearer {token}`

**权限要求**: admin

**路径参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| id | int | 是 | 用户ID |

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

#### 8.3 更新用户状态

**接口地址**: `PUT /admin/users/{id}/status`

**请求头**: `Authorization: Bearer {token}`

**权限要求**: admin

**路径参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| id | int | 是 | 用户ID |

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

#### 8.4 更新用户角色

**接口地址**: `PUT /admin/users/{id}/role`

**请求头**: `Authorization: Bearer {token}`

**权限要求**: admin

**路径参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| id | int | 是 | 用户ID |

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

#### 8.5 删除用户

**接口地址**: `DELETE /admin/users/{id}`

**请求头**: `Authorization: Bearer {token}`

**权限要求**: admin

**路径参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| id | int | 是 | 用户ID |

**响应示例**:
```json
{
  "code": 200,
  "message": "用户删除成功",
  "data": null
}
```

#### 8.6 获取用户统计数据

**接口地址**: `GET /admin/users/statistics`

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

### 9. 题目导入导出模块

#### 9.1 下载题目导入模板 (前端实现了，不需要后端实现)

**接口地址**: `GET /question/import/template`

**请求头**: `Authorization: Bearer {token}`

**权限要求**: teacher、admin

**响应**: Excel 文件下载

#### 9.2 批量导入题目

**接口地址**: `POST /question/import`

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

#### 9.3 导出题目

**接口地址**: `POST /question/export`

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

### 10. 防作弊模块

#### 10.1 记录考试行为

**接口地址**: `POST /exam/behavior/log`

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

#### 10.2 获取考试行为记录

**接口地址**: `GET /exam/{exam_record_id}/behavior/logs`

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

### 11. 错题本模块

#### 11.1 获取错题列表

**接口地址**: `GET /mistake/list`

**请求头**: `Authorization: Bearer {token}`

**权限要求**: student

**请求参数** (Query):

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| page | int | 否 | 页码，默认1 |
| size | int | 否 | 每页数量，默认10 |
| type | string | 否 | 题目类型筛选 |
| category | string | 否 | 题目分类筛选 |

**响应示例**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "list": [
      {
        "id": 1,
        "question_id": 10,
        "type": "single",
        "category": "数学",
        "content": "1+1等于多少？",
        "options": {
          "A": "1",
          "B": "2",
          "C": "3",
          "D": "4"
        },
        "user_answer": "A",
        "correct_answer": "B",
        "analysis": "1+1=2",
        "mistake_count": 2,
        "last_mistake_time": "2024-01-01 10:00:00",
        "exam_title": "数学测试卷"
      }
    ],
    "total": 50,
    "page": 1,
    "size": 10
  }
}
```

#### 11.2 获取错题统计

**接口地址**: `GET /mistake/statistics`

**请求头**: `Authorization: Bearer {token}`

**权限要求**: student

**响应示例**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "total_mistakes": 100,
    "unique_questions": 50,
    "type_distribution": {
      "single": 30,
      "multiple": 20,
      "judge": 25,
      "fill": 25
    },
    "category_distribution": {
      "数学": 40,
      "语文": 20,
      "英语": 30,
      "物理": 10
    },
    "recent_mistakes": [
      {
        "question_id": 10,
        "mistake_count": 3,
        "last_mistake_time": "2024-01-01 10:00:00"
      }
    ]
  }
}
```

#### 11.3 标记错题为已掌握

**接口地址**: `PUT /mistake/{mistake_id}/mastered`

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

#### 11.4 导出错题本

**接口地址**: `POST /mistake/export`

**请求头**: `Authorization: Bearer {token}`

**权限要求**: student

**响应**: Excel 文件下载

---

### 12. 成绩排名模块

#### 12.1 获取考试排名

**接口地址**: `GET /exam/{exam_id}/ranking`

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

#### 12.2 获取学生个人成绩趋势

**接口地址**: `GET /student/score/trend`

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

#### 12.3 获取班级成绩排名（教师）

**接口地址**: `GET /teacher/class/ranking`

**请求头**: `Authorization: Bearer {token}`

**权限要求**: teacher、admin

**请求参数** (Query):

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| exam_id | int | 否 | 试卷ID，不传则返回所有考试 |
| page | int | 否 | 页码，默认1 |
| size | int | 否 | 每页数量，默认10 |

**响应示例**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "exam_id": 1,
    "exam_title": "数学测试卷",
    "total_students": 50,
    "average_score": 78.5,
    "pass_rate": 0.8,
    "list": [
      {
        "rank": 1,
        "user_id": 10,
        "username": "student1",
        "nickname": "学霸",
        "score": 100,
        "is_passed": 1,
        "submit_time": "2024-01-01 10:30:00"
      }
    ],
    "total": 50,
    "page": 1,
    "size": 10
  }
}
```

---

### 13. 数据可视化模块

#### 13.1 获取考试成绩分布图数据

**接口地址**: `GET /exam/{exam_id}/chart/score-distribution`

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

#### 13.2 获取题目正确率图数据

**接口地址**: `GET /exam/{exam_id}/chart/question-correctness`

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

#### 13.3 获取学生成绩对比图数据

**接口地址**: `GET /student/chart/score-comparison`

**请求头**: `Authorization: Bearer {token}`

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

### 14. 考试分析报告模块

#### 14.1 生成考试分析报告

**接口地址**: `POST /exam/{exam_id}/report/generate`

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

#### 14.2 导出考试分析报告（PDF）

**接口地址**: `GET /exam/{exam_id}/report/export`

**请求头**: `Authorization: Bearer {token}`

**权限要求**: teacher、admin

**路径参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| exam_id | int | 是 | 试卷ID |

**响应**: PDF 文件下载

#### 14.3 发送成绩单邮件

**接口地址**: `POST /exam/{exam_id}/report/email`

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

---

### 15. 考试时间自动提交优化

#### 15.1 自动提交试卷（内部接口）

**接口地址**: `POST /exam/auto-submit`

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

## 数据库表结构变更

### 新增表

#### user_behavior_log 表（考试行为日志）
```sql
CREATE TABLE user_behavior_log (
  id INT PRIMARY KEY AUTO_INCREMENT,
  exam_record_id INT NOT NULL COMMENT '考试记录ID',
  user_id INT NOT NULL COMMENT '用户ID',
  behavior_type VARCHAR(50) NOT NULL COMMENT '行为类型',
  behavior_detail TEXT COMMENT '行为详情',
  timestamp DATETIME NOT NULL COMMENT '时间戳',
  create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (exam_record_id) REFERENCES exam_record(id),
  FOREIGN KEY (user_id) REFERENCES user(id)
);
```

#### mistake_question 表（错题本）
```sql
CREATE TABLE mistake_question (
  id INT PRIMARY KEY AUTO_INCREMENT,
  user_id INT NOT NULL COMMENT '用户ID',
  question_id INT NOT NULL COMMENT '题目ID',
  exam_record_id INT NOT NULL COMMENT '考试记录ID',
  user_answer TEXT COMMENT '用户答案',
  correct_answer TEXT COMMENT '正确答案',
  mistake_count INT DEFAULT 1 COMMENT '错误次数',
  last_mistake_time DATETIME COMMENT '最后错误时间',
  is_mastered INT DEFAULT 0 COMMENT '是否已掌握：0否 1是',
  mastered_time DATETIME COMMENT '掌握时间',
  create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
  update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES user(id),
  FOREIGN KEY (question_id) REFERENCES question(id),
  FOREIGN KEY (exam_record_id) REFERENCES exam_record(id),
  UNIQUE KEY uk_user_question (user_id, question_id)
);
```

#### exam_report 表（考试分析报告）
```sql
CREATE TABLE exam_report (
  id INT PRIMARY KEY AUTO_INCREMENT,
  exam_id INT NOT NULL COMMENT '试卷ID',
  creator_id INT NOT NULL COMMENT '创建者ID',
  report_data TEXT NOT NULL COMMENT '报告数据（JSON）',
  generate_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '生成时间',
  FOREIGN KEY (exam_id) REFERENCES exam(id),
  FOREIGN KEY (creator_id) REFERENCES user(id)
);
```

---

## 注意事项

1. **文件上传限制**：
   - 导入题目文件大小限制：10MB
   - 支持的文件格式：.xlsx, .xls

2. **防作弊机制**：
   - 失去焦点超过3次将记录警告
   - 切换标签页超过5次将自动提交试卷
   - 退出全屏模式超过3次将记录警告

3. **错题本**：
   - 自动收集所有做错的题目
   - 标记为已掌握后不再显示在错题列表中
   - 可以重新添加到错题本

4. **成绩排名**：
   - 实时更新排名
   - 同分情况下按提交时间排序

5. **数据可视化**：
   - 图表数据实时计算
   - 支持导出图表为图片

6. **考试分析报告**：
   - 报告包含文字分析、图表、排名等
   - 支持导出为 PDF 格式
   - 支持邮件发送给学生

7. **API 限流**：
   - 每个用户每分钟最多请求 100 次
   - 超过限制将返回 429 状态码

8. **时间格式**：
   - 所有时间格式统一为 `YYYY-MM-DD HH:mm:ss`
   - 时区使用 Asia/Shanghai

---

## v2.0 功能清单

✅ 用户管理模块（管理员专用）
- 用户列表查询
- 用户状态管理
- 用户角色管理
- 用户删除功能
- 用户统计数据

✅ 题目导入导出模块
- 下载导入模板
- 批量导入题目
- 导出题目

✅ 防作弊模块
- 记录考试行为
- 获取考试行为记录

✅ 错题本模块
- 获取错题列表
- 获取错题统计
- 标记错题为已掌握
- 导出错题本

✅ 成绩排名模块
- 获取考试排名
- 获取学生个人成绩趋势
- 获取班级成绩排名

✅ 数据可视化模块
- 获取考试成绩分布图数据
- 获取题目正确率图数据
- 获取学生成绩对比图数据

✅ 考试分析报告模块
- 生成考试分析报告
- 导出考试分析报告（PDF）
- 发送成绩单邮件

✅ 考试时间自动提交优化
- 自动提交试卷（内部接口）

---

## 版本升级说明

从 v1.0 升级到 v2.0 需要执行以下操作：

1. **数据库迁移**：
   - 执行新增表的 SQL 建表语句
   - 检查是否需要调整现有表结构

2. **依赖安装**：
   - 安装 Excel 处理库：`pip install openpyxl`
   - 安装 PDF 生成库：`pip install reportlab`
   - 安装邮件发送库：`pip install django-smtp-ssl`

3. **配置更新**：
   - 添加邮件服务器配置
   - 添加文件上传大小限制配置
   - 添加 API 限流配置

4. **前端更新**：
   - 更新 API 接口调用
   - 添加新功能页面
   - 添加图表库（如 ECharts）

---

## 联系方式

如有问题或建议，请联系开发团队。
