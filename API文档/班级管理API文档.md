# 班级管理功能 API 接口文档

## 版本说明

**版本**: v1.0
**发布日期**: 2026-01-02
**功能**: 班级管理、班级成员管理、班级成绩统计

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

---

## 1. 班级管理模块

### 1.1 获取班级列表

**接口地址**: `GET /class/list`

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

---

### 1.2 获取班级详情

**接口地址**: `GET /class/{id}`

**请求头**: `Authorization: Bearer {token}`

**权限要求**: admin、teacher

**路径参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| id | int | 是 | 班级ID |

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

---

### 1.3 创建班级

**接口地址**: `POST /class/create`

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

---

### 1.4 更新班级信息

**接口地址**: `PUT /class/{id}`

**请求头**: `Authorization: Bearer {token}`

**权限要求**: admin

**路径参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| id | int | 是 | 班级ID |

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

---

### 1.5 删除班级

**接口地址**: `DELETE /class/{id}`

**请求头**: `Authorization: Bearer {token}`

**权限要求**: admin

**路径参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| id | int | 是 | 班级ID |

**响应示例**:
```json
{
  "code": 200,
  "message": "班级删除成功",
  "data": null
}
```

---

### 1.6 更新班级状态

**接口地址**: `PUT /class/{id}/status`

**请求头**: `Authorization: Bearer {token}`

**权限要求**: admin

**路径参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| id | int | 是 | 班级ID |

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

---

## 2. 班级成员管理模块

### 2.1 获取班级成员列表

**接口地址**: `GET /class/{id}/members`

**请求头**: `Authorization: Bearer {token}`

**权限要求**: admin、teacher

**路径参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| id | int | 是 | 班级ID |

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

---

### 2.2 添加学生到班级

**接口地址**: `POST /class/{id}/members/add`

**请求头**: `Authorization: Bearer {token}`

**权限要求**: admin、teacher

**路径参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| id | int | 是 | 班级ID |

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

---

### 2.3 从班级移除学生

**接口地址**: `DELETE /class/{id}/members/remove`

**请求头**: `Authorization: Bearer {token}`

**权限要求**: admin、teacher

**路径参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| id | int | 是 | 班级ID |

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

---

### 2.4 获取可选学生列表（未加入班级的学生）

**接口地址**: `GET /class/{id}/available-students`

**请求头**: `Authorization: Bearer {token}`

**权限要求**: admin、teacher

**路径参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| id | int | 是 | 班级ID |

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

---

## 3. 班级成绩统计模块

### 3.1 获取班级成绩统计

**接口地址**: `GET /class/{id}/statistics`

**请求头**: `Authorization: Bearer {token}`

**权限要求**: admin、teacher

**路径参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| id | int | 是 | 班级ID |

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

---

### 3.2 获取班级考试排名

**接口地址**: `GET /class/{id}/exam-ranking`

**请求头**: `Authorization: Bearer {token}`

**权限要求**: admin、teacher

**路径参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| id | int | 是 | 班级ID |

**请求参数** (Query):

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| exam_id | int | 否 | 试卷ID，不传则返回所有考试的平均排名 |
| page | int | 否 | 页码，默认1 |
| size | int | 否 | 每页数量，默认10 |

**响应示例**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "class_id": 1,
    "class_name": "三年二班",
    "exam_id": 1,
    "exam_title": "数学测试卷",
    "average_score": 85.5,
    "pass_rate": 0.9,
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
    "total": 45,
    "page": 1,
    "size": 10
  }
}
```

---

### 3.3 获取班级成绩趋势

**接口地址**: `GET /class/{id}/score-trend`

**请求头**: `Authorization: Bearer {token}`

**权限要求**: admin、teacher

**路径参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| id | int | 是 | 班级ID |

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
    "class_id": 1,
    "class_name": "三年二班",
    "total_exams": 10,
    "average_score": 85.5,
    "highest_average": 92,
    "lowest_average": 78,
    "pass_rate": 0.9,
    "trend": [
      {
        "date": "2024-01-01",
        "exam_title": "数学测试",
        "average_score": 85,
        "pass_rate": 0.9
      },
      {
        "date": "2024-01-05",
        "exam_title": "语文测试",
        "average_score": 88,
        "pass_rate": 0.92
      }
    ]
  }
}
```

---

## 4. 教师班级查询模块

### 4.1 获取教师管理的班级列表

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

---

## 5. 学生班级查询模块

### 5.1 获取学生所在班级信息

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

## 6. 班级选择器接口（用于下拉框）

### 6.1 获取所有班级（用于下拉选择）

**接口地址**: `GET /class/options`

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

---

## 数据库表结构建议

### class 表（班级表）
```sql
CREATE TABLE `class` (
  `id` INT PRIMARY KEY AUTO_INCREMENT,
  `name` VARCHAR(100) NOT NULL COMMENT '班级名称',
  `grade` VARCHAR(50) NULL COMMENT '年级',
  `head_teacher_id` INT NULL COMMENT '班主任ID',
  `status` INT DEFAULT 1 COMMENT '状态：1正常 0禁用',
  `create_time` DATETIME DEFAULT CURRENT_TIMESTAMP,
  `update_time` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (`head_teacher_id`) REFERENCES `user`(`id`),
  UNIQUE KEY `uk_name` (`name`)
) COMMENT='班级表';
```

### user_class 表（用户班级关联表）
```sql
CREATE TABLE `user_class` (
  `id` INT PRIMARY KEY AUTO_INCREMENT,
  `user_id` INT NOT NULL COMMENT '用户ID',
  `class_id` INT NOT NULL COMMENT '班级ID',
  `join_time` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '加入时间',
  FOREIGN KEY (`user_id`) REFERENCES `user`(`id`),
  FOREIGN KEY (`class_id`) REFERENCES `class`(`id`),
  UNIQUE KEY `uk_user_class` (`user_id`, `class_id`)
) COMMENT='用户班级关联表';
```

### user 表需要添加字段
```sql
ALTER TABLE `user` ADD COLUMN `class_id` INT NULL COMMENT '所属班级ID' AFTER `role`;
ALTER TABLE `user` ADD FOREIGN KEY (`class_id`) REFERENCES `class`(`id`);
```

---

## 注意事项

1. **权限控制**：
   - 班级创建、删除、编辑仅管理员可操作
   - 教师可以查看和管理自己负责的班级
   - 学生只能查看自己所在班级的信息

2. **数据验证**：
   - 班级名称不能重复
   - 一个学生只能属于一个班级
   - 删除班级前需要检查是否有学生

3. **级联操作**：
   - 删除班级时，需要处理班级成员
   - 删除用户时，需要清理班级关联

4. **统计优化**：
   - 成绩统计可以缓存
   - 排名查询可以添加索引

---

## 功能清单

✅ 班级管理模块
- 获取班级列表
- 获取班级详情
- 创建班级
- 更新班级信息
- 删除班级
- 更新班级状态

✅ 班级成员管理模块
- 获取班级成员列表
- 添加学生到班级
- 从班级移除学生
- 获取可选学生列表

✅ 班级成绩统计模块
- 获取班级成绩统计
- 获取班级考试排名
- 获取班级成绩趋势

✅ 教师班级查询模块
- 获取教师管理的班级列表

✅ 学生班级查询模块
- 获取学生所在班级信息

✅ 班级选择器接口
- 获取所有班级（用于下拉选择）

---

## 联系方式

如有问题或建议，请联系开发团队。