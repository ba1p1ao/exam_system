# 在线考试系统 - IFLOW 上下文文档

## 项目概述

这是一个基于 Django REST Framework 后端和 Vue 3 前端的在线考试系统。系统支持用户管理、题目管理、试卷管理、在线考试、考试记录统计、班级管理、错题本、成绩排名等完整功能。

### 技术栈

**后端 (exam_system):**
- Python 3.10+
- Django 4.2.5
- Django REST Framework
- MySQL 数据库（开发环境）
- Redis 缓存
- JWT 认证

**前端 (exam-frontend):**
- Vue 3.5.24
- Vite 7.2.4
- Element Plus 2.13.0 UI 组件库
- Pinia 3.0.4 状态管理
- Vue Router 4.6.4
- Axios 1.13.2 HTTP 客户端
- ECharts 5.6.0 数据可视化
- xlsx 0.18.5 Excel 处理

## 项目结构

```
kaoshigunalimanager/
├── exam_system/                    # Django 后端项目
│   ├── apps/                       # Django 应用
│   │   ├── user/                   # 用户管理模块
│   │   ├── question/               # 题目管理模块
│   │   ├── exam/                   # 试卷和考试模块
│   │   ├── classes/                # 班级管理模块
│   │   ├── adminer/                # 管理员模块
│   │   ├── student/                # 学生模块
│   │   ├── teacher/                # 教师模块
│   │   └── mistake/                # 错题本模块
│   ├── exam_system/                # Django 项目配置
│   │   ├── settings.py             # 项目设置
│   │   ├── urls.py                 # 主路由配置
│   │   └── ...
│   ├── utils/                      # 工具模块
│   │   ├── JWTAuth.py              # JWT 认证
│   │   ├── PasswordEncode.py       # 密码加密
│   │   ├── ResponseMessage.py      # 响应消息工具
│   │   ├── exceptions.py           # 异常处理
│   │   ├── ReportPDF.py            # PDF 报告生成
│   │   └── RequestLoggingMiddleware.py  # 请求日志中间件
│   ├── logs/                       # 日志目录
│   │   ├── django.log              # Django 日志
│   │   └── django_error.log        # 错误日志
│   ├── static/                     # 静态文件
│   │   ├── question_export/        # 题目导出文件
│   │   └── report_pdfs/            # PDF 报告文件
│   ├── manage.py                   # Django 管理脚本
│   └── db.sqlite3                  # SQLite 数据库（已弃用，改用 MySQL）
├── exam-frontend/                  # Vue 前端项目
│   ├── src/
│   │   ├── api/                    # API 接口定义
│   │   │   ├── user.js             # 用户相关 API
│   │   │   ├── question.js         # 题目相关 API
│   │   │   ├── exam.js             # 考试相关 API
│   │   │   ├── class.js            # 班级相关 API
│   │   │   ├── admin.js            # 管理员相关 API
│   │   │   ├── ranking.js          # 排名相关 API
│   │   │   ├── mistake.js          # 错题本相关 API
│   │   │   ├── chart.js            # 图表相关 API
│   │   │   ├── report.js           # 报告相关 API
│   │   │   ├── anti-cheat.js       # 防作弊相关 API
│   │   │   └── import-export.js    # 导入导出相关 API
│   │   ├── assets/                 # 静态资源
│   │   ├── components/             # 公共组件
│   │   │   ├── ClassMemberDialog.vue       # 班级成员对话框
│   │   │   ├── QuestionImportDialog.vue    # 题目导入对话框
│   │   │   ├── ScoreTrendChart.vue         # 成绩趋势图表
│   │   │   └── StudentScoreComparisonChart.vue  # 学生成绩对比图
│   │   ├── router/                 # 路由配置
│   │   │   └── index.js            # 路由定义
│   │   ├── stores/                 # Pinia 状态管理
│   │   │   └── user.js             # 用户状态
│   │   ├── utils/                  # 工具函数
│   │   │   └── request.js          # Axios 请求封装
│   │   ├── views/                  # 页面视图
│   │   │   ├── Login.vue           # 登录页面
│   │   │   ├── Home.vue            # 首页
│   │   │   ├── Layout.vue          # 布局页面
│   │   │   ├── Profile.vue         # 个人中心
│   │   │   ├── Questions.vue       # 题库管理
│   │   │   ├── QuestionForm.vue    # 题目表单
│   │   │   ├── Exams.vue           # 试卷管理
│   │   │   ├── ExamForm.vue        # 试卷表单
│   │   │   ├── ExamDetail.vue      # 试卷详情
│   │   │   ├── ExamList.vue        # 考试列表（学生）
│   │   │   ├── ExamTake.vue        # 参加考试
│   │   │   ├── ExamRecord.vue      # 考试记录详情
│   │   │   ├── Records.vue         # 考试记录
│   │   │   ├── Ranking.vue         # 成绩排名
│   │   │   ├── MistakeBook.vue     # 错题本
│   │   │   ├── ClassManagement.vue # 班级管理
│   │   │   └── Users.vue           # 用户管理
│   │   ├── App.vue                 # 根组件
│   │   ├── main.js                 # 应用入口
│   │   └── style.css               # 全局样式
│   ├── package.json                # 前端依赖配置
│   ├── vite.config.js              # Vite 配置
│   └── index.html                  # HTML 入口
├── API文档.md                      # v1.0 API 接口文档
├── API文档v2.0.md                  # v2.0 API 接口文档
├── API文档v3.0.md                  # v3.0 API 接口文档（最新）
├── 班级管理API文档.md              # 班级管理 API 文档
├── 班级管理功能实现文档.md          # 班级管理功能实现说明
├── 错题本合并API接口说明.md        # 错题本 API 说明
├── 考试记录分组API文档.md          # 考试记录分组 API 文档
├── 前端v2.0实现说明.md             # 前端实现说明
├── todo.md                         # 待办事项
└── IFLOW.md                        # 本文档
```

## API 接口文档

完整的 API 接口文档请参考以下文件：
- `API文档.md` - v1.0 基础功能 API
- `API文档v2.0.md` - v2.0 新增功能 API
- `API文档v3.0.md` - v3.0 完整合并版 API（推荐参考）
- `班级管理API文档.md` - 班级管理功能 API

### 基础信息
- **Base URL**: `http://localhost:8010/api`
- **认证方式**: Bearer Token
- **响应格式**: JSON

### 主要模块

1. **用户模块** (`/api/user/`)
   - 用户注册、登录、信息管理
   - JWT 认证（Token 有效期 24 小时）
   - 密码修改

2. **题目模块** (`/api/question/`)
   - 题目增删改查
   - 支持单选、多选、判断、填空四种题型
   - 题目导入导出（Excel）
   - 批量删除

3. **试卷模块** (`/api/exam/`)
   - 试卷创建、发布、关闭
   - 随机组卷功能
   - 试卷详情、统计
   - 试卷状态管理（draft/published/closed）

4. **考试模块** (`/api/exam/`)
   - 开始考试、保存答案、提交试卷
   - 考试记录管理
   - 获取学生可参加的考试列表
   - 考试题目获取

5. **考试记录模块** (`/api/exam/`)
   - 考试记录列表
   - 考试记录详情
   - 按考试分组的记录查询
   - 自动评分

6. **统计模块** (`/api/exam/`)
   - 考试统计（参与人数、平均分、及格率等）
   - 系统统计数据
   - 考试排名

7. **班级模块** (`/api/class/`)
   - 班级增删改查
   - 班级成员管理（添加/移除学生）
   - 班级成绩统计
   - 教师班级查询
   - 学生班级查询

8. **管理员模块** (`/api/admin/`)
   - 用户管理
   - 用户状态和角色管理
   - 用户统计

9. **教师模块** (`/api/teacher/`)
   - 教师班级查询

10. **学生模块** (`/api/student/`)
    - 学生成绩趋势
    - 学生班级查询

11. **错题本模块** (`/api/mistake/`)
    - 错题列表
    - 错题统计
    - 标记掌握

## 开发环境设置

### 数据库配置

项目使用 MySQL 数据库，需先创建数据库：

```sql
CREATE DATABASE exam_system CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

在 `exam_system/exam_system/__init__.py` 中添加：

```python
from pymysql import install_as_MySQLdb
install_as_MySQLdb()
```

### 后端设置

1. **安装依赖**：
   ```bash
   cd exam_system
   pip install django==4.2.5 djangorestframework django-cors-headers pymysql redis
   ```

2. **数据库迁移**：
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

3. **创建超级用户**：
   ```bash
   python manage.py createsuperuser
   ```

4. **运行开发服务器**：
   ```bash
   python manage.py runserver 8010
   ```

### 前端设置

1. **安装依赖**：
   ```bash
   cd exam-frontend
   npm install
   ```

2. **运行开发服务器**：
   ```bash
   npm run dev
   ```
   前端将在 `http://localhost:8090` 运行，并代理 API 请求到 `http://localhost:8010`

## 构建和部署

### 后端构建
```bash
cd exam_system
# 生产环境设置
# 修改 settings.py 中的 DEBUG = False
# 配置 ALLOWED_HOSTS
python manage.py collectstatic
```

### 前端构建
```bash
cd exam-frontend
npm run build
```
构建后的文件在 `dist/` 目录中。

## 开发约定

### 后端约定
1. **应用结构**：每个功能模块对应一个 Django 应用
2. **认证方式**：使用 JWT Token 认证，Token 有效期 24 小时
3. **响应格式**：统一使用 `ResponseMessage` 工具类返回 JSON 响应
4. **错误处理**：使用自定义异常类处理业务异常
5. **跨域配置**：已配置允许所有域名跨域访问（开发环境）
6. **权限控制**：使用 `@check_permission` 装饰器限制访问权限
7. **数据库**：使用 MySQL 数据库，配置了连接池
8. **缓存**：使用 Redis 缓存
9. **日志**：配置了日志系统，日志文件保存在 `logs/` 目录

### 前端约定
1. **组件结构**：使用 Vue 3 Composition API
2. **状态管理**：使用 Pinia 进行状态管理
3. **UI 组件**：使用 Element Plus 组件库
4. **API 调用**：统一使用 `src/utils/request.js` 中的 axios 实例
5. **路由管理**：使用 Vue Router 4
6. **权限控制**：在路由配置中添加角色验证，无权限用户自动跳转

### 日志配置
- **日志级别**：INFO
- **日志文件**：
  - `logs/django.log` - 所有日志
  - `logs/django_error.log` - 错误日志
- **日志轮转**：单文件最大 10MB，保留 10 个备份

## 用户角色权限

### 学生 (student)
- 可访问：首页、考试列表、参加考试、考试记录、成绩排名、错题本、个人中心
- 不可访问：题库管理、试卷管理、班级管理、用户管理

### 教师 (teacher)
- 可访问：首页、题库管理、试卷管理、班级管理（仅自己管理的班级）、考试记录、成绩排名、个人中心
- 不可访问：用户管理、考试列表、错题本

### 管理员 (admin)
- 可访问：所有页面，包括用户管理和班级管理

## 数据库模型

### 用户模型 (User)
- 用户名、密码、昵称、角色（student/teacher/admin）
- 头像、状态、创建时间

### 题目模型 (Question)
- 题目类型（single/multiple/judge/fill）
- 题目内容、选项、正确答案
- 分类、难度、分值、解析
- 创建者 ID

### 试卷模型 (Exam)
- 试卷标题、描述、时长
- 总分、及格分、开始/结束时间
- 是否随机组卷、状态（draft/published/closed）
- 题目 ID 列表（JSON）

### 考试记录模型 (ExamRecord)
- 用户、试卷关联
- 考试成绩、是否通过
- 状态（not_started/in_progress/submitted/graded）
- 开始时间、提交时间
- 答案（JSON）

### 班级模型 (Class)
- 班级名称、年级、班主任
- 状态、创建时间

### 用户班级关联模型 (UserClass)
- 用户、班级关联
- 加入时间

### 错题模型 (Mistake)
- 用户、题目关联
- 用户答案、是否已掌握
- 创建时间

## 常见问题

1. **跨域问题**：后端已配置 CORS，确保前端代理配置正确
2. **数据库问题**：首次运行需要执行数据库迁移，需先创建 MySQL 数据库
3. **端口冲突**：后端默认端口 8010，前端默认端口 8090
4. **JWT 认证**：登录后需要在请求头中添加 `Authorization: Bearer {token}`，Token 有效期 24 小时
5. **权限问题**：确保用户角色正确设置，否则无法访问相应页面
6. **Redis 连接**：确保 Redis 服务已启动，配置在 settings.py 中
7. **日志问题**：日志文件保存在 `logs/` 目录，确保该目录有写入权限

## 项目状态

当前项目为 v3.0 版本，包含完整的用户管理、题目管理、试卷管理、在线考试、班级管理、成绩排名、错题本等功能。前端界面使用 Element Plus 构建，支持三种用户角色（学生、教师、管理员）的权限控制。

## 已实现功能

### 核心功能
- ✅ 用户注册、登录、信息管理
- ✅ 题库管理（增删改查、导入导出、批量删除）
- ✅ 试卷管理（创建、编辑、发布、关闭）
- ✅ 在线考试（参加考试、保存答案、自动提交）
- ✅ 考试记录查看（个人记录、按考试分组）
- ✅ 成绩排名（考试排名、成绩趋势）
- ✅ 错题本（错题列表、错题统计）
- ✅ 班级管理（创建、编辑、删除班级）
- ✅ 班级成员管理（添加、移除成员）
- ✅ 班级成绩统计
- ✅ PDF 报告生成

### 权限控制
- ✅ 基于角色的访问控制（RBAC）
- ✅ 前端页面权限验证
- ✅ 后端接口权限验证

### 数据可视化
- ✅ 成绩趋势图表
- ✅ 班级统计卡片
- ✅ 学生成绩对比图

### 系统功能
- ✅ 日志记录
- ✅ Redis 缓存
- ✅ MySQL 数据库
- ✅ 数据库连接池

## 待实现功能

根据 API 文档 v3.0，以下功能后端已定义但前端尚未完全实现：

1. **防作弊模块**
   - 考试行为记录（前端监控）
   - 考试行为记录查看（教师端）

2. **数据可视化模块**
   - 考试成绩分布图
   - 题目正确率图

3. **错题本模块**
   - 标记错题为已掌握
   - 导出错题本

4. **班级高级统计**
   - 班级考试排名
   - 班级成绩趋势

5. **用户管理**
   - 用户删除功能
   - 用户状态管理

## 相关文件

- `API文档.md` - v1.0 基础功能 API 文档
- `API文档v2.0.md` - v2.0 新增功能 API 文档
- `API文档v3.0.md` - v3.0 完整合并版 API 文档（推荐）
- `班级管理API文档.md` - 班级管理 API 文档
- `班级管理功能实现文档.md` - 班级管理功能实现说明
- `错题本合并API接口说明.md` - 错题本 API 说明
- `考试记录分组API文档.md` - 考试记录分组 API 文档
- `前端v2.0实现说明.md` - 前端实现说明
- `exam_system/` - Django 后端项目
- `exam-frontend/` - Vue 前端项目

## 快速开始

### 1. 启动数据库
确保 MySQL 和 Redis 服务已启动

### 2. 配置数据库
修改 `exam_system/exam_system/settings.py` 中的数据库配置

### 3. 运行后端
```bash
cd exam_system
python manage.py migrate
python manage.py runserver 8010
```

### 4. 运行前端
```bash
cd exam-frontend
npm install
npm run dev
```

### 5. 访问应用
- 前端：http://localhost:8090
- 后端 API：http://localhost:8010/api
- Django Admin：http://localhost:8010/admin