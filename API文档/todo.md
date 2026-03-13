  后端待实现的API接口清单

  1. 错题本模块（4个接口）
   - GET /mistake/list/ - 获取错题列表 ok
   - GET /mistake/statistics/ - 获取错题统计 ok 获取错题列表和获取错题统计，合并为一个接口实现
   - PUT /mistake/{mistake_id}/mastered/ - 标记错题为已掌握 ok
   - POST /mistake/export/ - 导出错题本  ok

  2. 防作弊模块（2个接口）
   - POST /exam/behavior/log/ - 记录考试行为 
   - GET /exam/{exam_record_id}/behavior/logs/ - 获取考试行为记录

  3. 数据可视化模块（3个接口）
   - GET /exam/{exam_id}/chart/score-distribution/ - 获取考试成绩分布图数据 ok
   - GET /exam/{exam_id}/chart/question-correctness/ - 获取题目正确率图数据 ok
   - GET /student/chart/score-comparison/ - 获取学生成绩对比图数据 ok

  4. 考试分析报告模块（4个接口）
   - POST /exam/{exam_id}/report/generate/ - 生成考试分析报告 ok
   - GET /exam/{exam_id}/report/export/ - 导出考试分析报告（PDF） ok
   - POST /exam/{exam_id}/report/email/ - 发送成绩单邮件 不需要完成，废弃方案
   - POST /exam/auto-submit/ - 自动提交试卷  ok 前端实现



"GET /api/class/1/exam-ranking/?exam_id=1&page=1&size=100 HTTP/1.1" 404 4665

🔴 高优先级问题（立即修复）

  1. 调试代码未清理
  大量 print() 调试语句散落在各个文件中，应该移除：
   - exam_system/apps/question/views.py:109, 162, 181
   - exam_system/apps/exam/views.py:187, 189
   - exam_system/apps/classes/views.py:31, 56, 437
   - exam_system/apps/adminer/views.py:140
   - exam_system/apps/student/views.py:59, 134, 149, 163
   - exam_system/utils/ReportPDF.py:39, 42, 52, 54, 58

  2. 拼写错误
   - exam_system/apps/question/views.py:229 - filed 应为 failed
   - exam_system/apps/classes/views.py:456 - highest_averag 应为 highest_average
   - exam_system/utils/ResponseMessage.py:28 - response_dta 应为 response_data

  3. 敏感信息硬编码
   - exam_system/exam_system/settings.py:28 - SECRET_KEY 应使用环境变量
   - exam_system/exam_system/settings.py:85 - 数据库密码硬编码为 "123"

  4. 生产环境配置问题
   - DEBUG = True - 生产环境应设为 False
   - ALLOWED_HOSTS = [] - 应配置具体域名
   - CORS_ORIGIN_ALLOW_ALL = True - 应限制允许的域名

  ---

  🟡 中优先级问题（中期改进）

  5. 数据库性能问题
   - N+1 查询：exam_system/apps/exam/serializers.py:185-196 在循环中查询 AnswerRecord
   - 索引被注释：多个 Model 的 indexes 被注释掉，影响查询性能

  6. 安全性问题
   - JWT Token 有效期过长：24小时，建议缩短为1-2小时
   - 密码验证不严格：注册接口缺少对 admin 角色的验证
   - 权限验证不统一：部分接口未使用 @check_permission 装饰器

  7. 缓存未使用
  虽然配置了 Redis，但整个代码库中几乎未使用缓存功能

  8. 输入验证缺失
   - exam_system/apps/question/views.py:88-95 - page_size 没有验证最大值，可能导致性能问题

  ---

  🟢 低优先级问题（长期改进）

  9. 代码组织问题
   - 所有应用都放在 apps/ 目录下，不符合 Django 最佳实践
   - 模块间耦合度高（如 adminer 直接依赖 classes）

  10. 注释和文档
   - exam_system/apps/mistake/views.py - 大量注释的旧代码未删除
   - exam_system/utils/demo.py - 整个文件都是注释掉的代码

  11. 前端安全
   - 使用 localStorage 存储 token 存在 XSS 风险，建议使用 httpOnly cookie

  12. 功能缺失
   - 防作弊模块（考试行为记录）未实现
   - 数据可视化模块（考试成绩分布图、题目正确率图）未实现
   - 错题本标记已掌握功能未实现
   - 用户删除功能不完整（缺少对考试记录的检查）

  ---
  
  
  
  
  
  
  根据分析报告，我为你整理出项目中可以使用缓存的地方：

  ---

  📋 缓存使用场景分析

  1. 高频查询的数据


  ┌──────────────────────┬─────────────────────────────┬─────────────────────────────────────────────┬──────────┬────────────────────┐
  │ 位置                 │ 函数                        │ 缓存键建议                                  │ 过期时间 │ 失效策略           │
  ├──────────────────────┼─────────────────────────────┼─────────────────────────────────────────────┼──────────┼────────────────────┤
  │ question/views.py:64 │ QuestionListView.get()      │ questions:list:{page}:{size}:{filters_hash} │ 30分钟   │ 题目增删改时删除   │ok
  │ question/views.py:92 │ QuestionInfoView.retrieve() │ question:info:{id}                          │ 1小时    │ 题目更新时删除     │ok
  │ exam/views.py:56     │ ExamListView.get()          │ exams:list:{page}:{size}:{filters_hash}     │ 15分钟   │ 试卷增删改时删除   │ok
  │ exam/views.py:263    │ ExamAvailableView.list()    │ exams:available:{user_id}                   │ 5分钟    │ 试卷状态变更时删除 │
  │ exam/views.py:327    │ ExamQuestionsView.get()     │ exam:questions:{exam_id}                    │ 1小时    │ 试卷题目变更时删除 │
  └──────────────────────┴─────────────────────────────┴─────────────────────────────────────────────┴──────────┴────────────────────┘

  ---

  2. 静态配置数据


  ┌──────────────────────┬──────────────────────────┬────────────────────────────────────┬──────────┬──────────────────┐
  │ 位置                 │ 函数                     │ 缓存键建议                         │ 过期时间 │ 失效策略         │
  ├──────────────────────┼──────────────────────────┼────────────────────────────────────┼──────────┼──────────────────┤
  │ classes/views.py:26  │ ClassOptionView.get()    │ classes:options                    │ 1小时    │ 班级增删改时删除 │
  │ classes/views.py:40  │ ClassListView.get()      │ classes:list:{page}:{filters_hash} │ 30分钟   │ 班级增删改时删除 │
  │ adminer/views.py:106 │ UserStatisticsView.get() │ users:statistics                   │ 5分钟    │ 用户增删改时删除 │
  └──────────────────────┴──────────────────────────┴────────────────────────────────────┴──────────┴──────────────────┘

  ---

  3. 计算密集型操作（优先级最高）


  ┌────────────────────┬───────────────────────────────┬────────────────────────────────────┬─────────┬──────────────────┬─────────────┐
  │ 位置               │ 函数                          │ 缓存键建议                         │ 过期... │ 失效策略         │ 说明        │
  ├────────────────────┼───────────────────────────────┼────────────────────────────────────┼─────────┼──────────────────┼─────────────┤
  │ `classes/views.... │ ClassStatisticsView.get()     │ class:statistics:{class_id}        │ 15分钟  │ 新增考试记录...  │ 复杂聚合... │
  │ `classes/views.... │ ClassExamRankingView.get()    │ `class:exam_ranking:{class_id}:{e... │ 10分钟  │ 考试记录更新...  │ 排名计算    │
  │ `classes/views.... │ ClassScoreTrendView.get()     │ class:score_trend:{class_id}:{days}  │ 10分钟  │ 考试记录更新...  │ 趋势分析    │
  │ `student/views.... │ ScoreTrendView.get()          │ student:score_trend:{user_id}:{days} │ 10分钟  │ 考试记录更新...  │ 成绩趋势    │
  │ `student/views.... │ `StudentScoreComparisonVie... │ student:score_comparison:{user_id}   │ 10分钟  │ 考试记录更新...  │ 班级对比    │
  │ exam/views.py:828  │ `ExamRecordStatisticsView.... │ exam:statistics:{exam_id}          │ 15分钟  │ 考试记录更新...  │ 考试统计    │
  │ exam/views.py:1005 │ ExamRankingView.get()         │ exam:ranking:{exam_id}:{class_id}    │ 10分钟  │ 考试记录更新...  │ 排名计算    │
  │ exam/views.py:1172 │ ExamReportGenerate.post()     │ exam:report:{exam_id}              │ 1小时   │ 考试记录更新...  │ PDF生成     │
  └────────────────────┴───────────────────────────────┴────────────────────────────────────┴─────────┴──────────────────┴─────────────┘

  ---

  🔧 实现方法

  方法1: 使用 Django 缓存装饰器（推荐用于简单查询）

    1 from django.core.cache import cache
    2 
    3 def QuestionListView(APIView):
    4     def get(self, request):
    5         # 生成缓存键
    6         filters_hash = hash(str(sorted(request.GET.items())))
    7         cache_key = f'questions:list:{pagination.page}:{pagination.size}:{filters_hash}'
    8 
    9         # 尝试从缓存获取
   10         cached_data = cache.get(cache_key)
   11         if cached_data:
   12             return MyResponse.success(data=cached_data)
   13 
   14         # 执行查询
   15         # ... 查询逻辑 ...
   16 
   17         # 存入缓存
   18         cache.set(cache_key, response_data, 30 * 60)  # 30分钟
   19         return MyResponse.success(data=response_data)

  ---

  方法2: 使用 Django 缓存装饰器（推荐用于函数）

    1 from django.core.cache import cache
    2 from functools import wraps
    3 
    4 def cache_result(timeout=60*30, key_prefix=''):
    5     def decorator(func):
    6         @wraps(func)
    7         def wrapper(*args, **kwargs):
    8             # 生成缓存键
    9             cache_key = f'{key_prefix}:{str(args)}:{str(kwargs)}'
   10 
   11             # 尝试从缓存获取
   12             cached_data = cache.get(cache_key)
   13             if cached_data is not None:
   14                 return cached_data
   15 
   16             # 执行函数
   17             result = func(*args, **kwargs)
   18 
   19             # 存入缓存
   20             cache.set(cache_key, result, timeout)
   21             return result
   22         return wrapper
   23     return decorator
   24 
   25 # 使用示例
   26 @cache_result(timeout=60*15, key_prefix='class:statistics')
   27 def get_class_statistics(class_id):
   28     # ... 查询逻辑 ...
   29     return result

  ---

  方法3: 手动缓存管理（推荐用于复杂场景）

    1 from django.core.cache import cache
    2 
    3 class ClassStatisticsView(APIView):
    4     def get(self, request, class_id):
    5         cache_key = f'class:statistics:{class_id}'
    6 
    7         # 尝试从缓存获取
    8         cached_data = cache.get(cache_key)
    9         if cached_data:
   10             return MyResponse.success(data=cached_data)
   11 
   12         # 执行查询
   13         # ... 复杂的聚合查询 ...
   14 
   15         # 存入缓存
   16         cache.set(cache_key, response_data, 15 * 60)
   17         return MyResponse.success(data=response_data)

  ---

  方法4: 缓存失效（在数据更新时删除缓存）

    1 # 在题目更新时删除相关缓存
    2 def QuestionInfoView.update(self, request, *args, **kwargs):
    3     # ... 更新逻辑 ...
    4 
    5     # 删除题目详情缓存
    6     cache.delete(f'question:info:{question.id}')
    7 
    8     # 删除题目列表缓存（使用通配符）
    9     cache.delete_many(cache.keys('questions:list:*'))
   10 
   11     # 或者删除所有题目相关缓存
   12     cache.delete_pattern('questions:*')

  ---

  📊 实现优先级建议

  🔴 高优先级（立即实现）
   1. 考试报告生成 (exam:report:{exam_id}) - PDF生成最耗时
   2. 班级统计 (class:statistics:{class_id}) - 聚合查询复杂
   3. 考试排名 (exam:ranking:{exam_id}:{class_id}) - 排序计算重

  🟡 中优先级（短期实现）
   4. 班级考试排名
   5. 班级成绩趋势
   6. 学生成绩趋势
   7. 系统统计

  🟢 低优先级（长期优化）
   8. 题目列表
   9. 试卷列表
   10. 班级选项

  ---

  💡 注意事项

✦  1. 缓存键命名规范：使用冒号分隔层级，如 class:statistics:{class_id}
   2. 过期时间：根据数据更新频率设置，统计数据建议 5-15 分钟
   3. 缓存失效：在数据更新时主动删除相关缓存
   4. 缓存预热：系统启动时加载高频数据到缓存
   5. 缓存监控：记录缓存命中率，评估效果
   
   
   
   
   
   
   
   
   
   
   
根据三个探索代理的深入审查，我发现了项目中的多个逻辑问题。让我为您总结所有发现的问题：

  整体问题汇总

  🔴 严重问题（必须修复）

  用户认证和权限控制模块

   1. 登录时没有检查用户状态
      - 位置：exam_system/apps/user/views.py:33-51
      - 问题：被禁用的用户（status=0）仍然可以登录
      - 修复：在验证密码后添加 if user.status != 1 检查

   2. JWT 认证后没有检查用户状态
      - 位置：exam_system/utils/JWTAuth.py:40-70
      - 问题：用户被禁用后，已登录用户仍可继续使用系统
      - 修复：在 authenticate() 方法中查询用户当前状态

   3. JWT Token 包含敏感信息
      - 位置：exam_system/apps/user/views.py:48
      - 问题：Token payload 中包含用户密码哈希
      - 修复：只将必要的字段（id, username, role, status）放入 Token

   4. 没有登录失败次数限制
      - 位置：exam_system/apps/user/views.py:33-51
      - 问题：攻击者可以无限次尝试密码
      - 修复：使用 Redis 记录失败次数，连续失败 5 次后锁定账户

   5. @check_permission 装饰器没有检查用户状态
      - 位置：exam_system/utils/ResponseMessage.py:47-60
      - 问题：被禁用的用户仍可访问受保护资源
      - 修复：添加 if payload.get("status") != 1 检查

  考试核心业务逻辑模块

   6. 随机组卷功能未实现
      - 位置：exam_system/apps/exam/views.py:609-658
      - 问题：无论 is_random 设置为何值，都返回所有题目
      - 修复：根据 is_random 字段实现随机排序逻辑

   7. 考试开始存在竞态条件
      - 位置：exam_system/apps/exam/views.py:565-607
      - 问题：检查和创建之间没有使用数据库锁，可能创建多条记录
      - 修复：使用 select_for_update() 或数据库唯一约束

   8. 考试时间限制未强制执行
      - 位置：exam_system/apps/exam/views.py:707-878
      - 问题：提交试卷时没有验证考试时长，学生可以无限延长考试时间
      - 修复：在提交时检查 start_time + duration 是否超过当前时间

   9. 未检查考试开始时间
      - 位置：exam_system/apps/exam/views.py:529-607
      - 问题：学生可以在考试开始前就开始考试
      - 修复：在 ExamStartView 中检查 exam.start_time

   10. 答案保存无时间限制验证
       - 位置：exam_system/apps/exam/views.py:660-705
       - 问题：学生可以在考试时间结束后继续保存答案
       - 修复：在保存答案时验证考试是否超时

   11. 自动评分逻辑存在严重缺陷
       - 位置：exam_system/apps/exam/views.py:843-878
       - 问题：
         - 多选题评分过于严格，不支持部分得分
         - 填空题不支持模糊匹配
       - 修复：
         - 多选题：根据正确选项数量计算部分得分
         - 填空题：使用模糊匹配，忽略大小写和多余空格

   12. 未防止重复提交
       - 位置：exam_system/apps/exam/views.py:707-878
       - 问题：学生可以多次调用提交接口
       - 修复：检查考试记录状态，防止重复提交

   13. 未验证学生是否属于考试班级
       - 位置：exam_system/apps/exam/views.py:529-607
       - 问题：学生可能通过直接调用 API 开始不属于自己班级的考试
       - 修复：在 ExamStartView 中验证学生是否在考试关联的班级中

   14. 并发保存答案可能导致数据覆盖
       - 位置：exam_system/apps/exam/views.py:689-701
       - 问题：没有使用 select_for_update() 或原子操作
       - 修复：使用 select_for_update() 或乐观锁

  班级管理和错题本模块

   15. 班级成员添加/移除缺少事务保护
       - 位置：exam_system/apps/classes/views.py:141-144, 378-427, 471-496
       - 问题：多个数据库操作没有使用事务包裹，可能导致数据不一致
       - 修复：使用 @transaction.atomic 装饰器

   16. 班级成员添加存在竞态条件
       - 位置：exam_system/apps/classes/views.py:378-427
       - 问题：两个请求可能同时查询到相同的用户不在班级中，导致重复添加
       - 修复：使用 get_or_create() 或 select_for_update()

   17. 用户可能属于多个班级
       - 位置：exam_system/apps/classes/views.py:424
       - 问题：User.class_id 是单值字段，但 UserClass 表允许一个用户属于多个班级
       - 修复：明确业务规则，是否允许用户属于多个班级

   18. 错题创建存在竞态条件
       - 位置：exam_system/apps/exam/views.py:771-780
       - 问题：get() 和 create() 之间存在竞态条件
       - 修复：使用 get_or_create() 方法

   19. N+1 查询问题（班级排名）
       - 位置：exam_system/apps/classes/views.py:590-620
       - 问题：在循环中为每个学生单独查询 ExamRecord
       - 修复：在聚合查询中直接获取 is_passed 字段

   20. N+1 查询问题（错题统计）
       - 位置：exam_system/apps/mistake/views.py:210-280
       - 问题：先查询错题记录，再查询答题记录，存在两次数据库查询
       - 修复：优化查询结构，减少查询次数

  🟡 中等问题（建议修复）

   21. 没有 Token 黑名单机制
       - 用户注销后，Token 仍然有效直到过期
       - 修复：使用 Redis 存储 Token 黑名单

   22. Token 可以通过查询参数传递
       - Token 被记录在服务器日志、浏览器历史中，增加泄露风险
       - 修复：移除从查询参数获取 Token 的逻辑

   23. 没有密码复杂度验证
       - 用户可以设置弱密码（如 "123456"）
       - 修复：添加密码复杂度验证（长度、大小写、数字）

   24. 没有会话管理机制
       - 无法查看当前登录的设备，无法强制用户下线
       - 修复：实现会话管理功能

   25. 没有限制并发登录
       - 同一用户可以同时在多个设备上登录
       - 修复：实现并发登录限制

   26. 未作答也被计入错题本
       - 学生可能只是跳过了题目，不应计入错题本
       - 修复：只将答错的题目计入错题本

   27. 缓存键生成不一致
       - cache_delete_pattern 使用 custom_cache_key，但 cache.get() 使用默认键
       - 修复：统一缓存键生成方式

   28. 缓存失效策略不完整
       - 添加/移除班级成员后，没有清除相关的排名和趋势缓存
       - 修复：完善缓存失效逻辑

   29. 班级删除后用户 class_id 未更新
       - 班级删除后，用户的 class_id 字段不会自动更新为 NULL
       - 修复：在删除班级时更新相关用户的 class_id

   30. 发布试卷未验证业务规则
       - 没有验证试卷是否有题目、时间设置是否合理、分数设置是否合理
       - 修复：在发布试卷时添加验证逻辑

  🟢 轻微问题（可选优化）

   31. 没有密码重置功能
       - 用户忘记密码后无法自行重置
       - 修复：实现密码重置功能

   32. 没有审计日志
       - 没有记录敏感操作的历史
       - 修复：实现审计日志系统

   33. 没有验证码机制
       - 登录、注册等操作没有验证码
       - 修复：实现验证码机制

   34. 考试记录状态转换不完整
       - submitted 状态从未被使用，状态管理混乱
       - 修复：明确状态流转逻辑

   35. 关闭试卷权限检查不完整
       - 管理员无法关闭其他教师创建的试卷
       - 修复：管理员应该可以关闭任何试卷

   36. 未实现自动提交机制
       - 考试时间结束，学生未提交，记录会一直停留在 in_progress 状态
       - 修复：实现定时任务自动提交超时的考试

   37. 未记录答案修改历史
       - 无法追踪学生何时修改了答案
       - 修复：记录答案修改历史

   38. 未验证题目分数总和
       - 试卷总分可能与实际题目分数不一致
       - 修复：在创建/更新试卷时验证分数总和

   39. 缺少数据库索引
       - ExamRecord 表缺少 (user_id, status) 复合索引
       - 修复：添加必要的数据库索引

   40. 错题导出可能内存溢出
       - 没有限制导出的错题数量
       - 修复：添加分页或限制导出数量

  修复优先级建议

  P0（立即修复 - 安全和功能性问题）
   1. 登录时检查用户状态（问题 1）
   2. JWT 认证后检查用户状态（问题 2）
   3. 添加登录失败次数限制（问题 4）
   4. 修复考试开始竞态条件（问题 7）
   5. 强制执行考试时间限制（问题 8）
   6. 修复自动评分逻辑（问题 11）
   7. 防止重复提交（问题 12）
   8. 添加事务保护（问题 15）
   9. 修复错题创建竞态条件（问题 18）

  P1（尽快修复 - 数据一致性和性能问题）
   10. 实现随机组卷功能（问题 6）
   11. 检查考试开始时间（问题 9）
   12. 答案保存时间限制验证（问题 10）
   13. 验证学生班级权限（问题 13）
   14. 并发保存答案数据覆盖（问题 14）
   15. 解决 N+1 查询问题（问题 19, 20）
   16. 统一缓存键生成（问题 27）
   17. 完善缓存失效策略（问题 28）

  P2（计划修复 - 用户体验和安全性增强）
   18. 实现 Token 黑名单（问题 21）
   19. 移除查询参数传递 Token（问题 22）
   20. 添加密码复杂度验证（问题 23）
   21. 实现会话管理（问题 24）
   22. 限制并发登录（问题 25）
   23. 修复错题本逻辑（问题 26）
   24. 更新用户 class_id（问题 29）
   25. 验证试卷发布规则（问题 30）

✦ 您希望我针对哪些问题提供详细的修复方案？





  13. [中] 缺少速率限制
   - 位置: 所有 API 接口
   - 问题描述: 没有实现 API 速率限制机制
   - 影响: 容易受到 DDoS 攻击或暴力破解攻击
   - 建议: 使用 Django Ratelimit 或类似库实现速率限制
✦ 让我告诉你如何实现 API 速率限制功能：

  方案概述

  使用 django-ratelimit 库来实现 API 速率限制，这是 Django 最常用的速率限制库。

  实现步骤

  第一步：安装依赖

  在 exam_system/requirements.txt 中添加：

   1 django-ratelimit==4.1.0

  然后安装：

   1 pip install django-ratelimit==4.1.0

  ---

  第二步：配置 Django settings

  在 exam_system/exam_system/settings.py 中：

   1. 添加到 INSTALLED_APPS（大约第 29 行）：

    1 INSTALLED_APPS = [
    2     'django.contrib.admin',
    3     'django.contrib.auth',
    4     'django.contrib.contenttypes',
    5     'django.contrib.sessions',
    6     'django.contrib.messages',
    7     'django.contrib.staticfiles',
    8     'rest_framework',  # DRF 框架
    9     'corsheaders',  # 跨域配置
   10     'ratelimit',  # 添加这一行
   11     "apps.user",
   12     "apps.question",
   13     "apps.exam",
   14     "apps.adminer",
   15     "apps.student",
   16     "apps.classes",
   17     "apps.teacher",
   18     "apps.mistake",
   19 ]

   2. 添加速率限制配置（在文件末尾添加）：

    1 # ============================================
    2 # 速率限制配置
    3 # ============================================
    4 
    5 # 速率限制缓存后端（使用 Redis）
    6 RATELIMIT_USE_CACHE = 'default'
    7 
    8 # 速率限制时间窗口（秒）
    9 RATELIMIT_PERIOD = 60  # 1分钟
   10 
   11 # 速率限制次数
   12 RATELIMIT_COUNT = 100  # 每分钟最多100次请求
   13 
   14 # 登录接口速率限制
   15 RATELIMIT_LOGIN_COUNT = 5  # 每分钟最多5次登录尝试
   16 RATELIMIT_LOGIN_PERIOD = 60  # 1分钟
   17 
   18 # 敏感操作速率限制（如删除、更新）
   19 RATELIMIT_SENSITIVE_COUNT = 10  # 每分钟最多10次敏感操作
   20 RATELIMIT_SENSITIVE_PERIOD = 60  # 1分钟
   21 
   22 # 文件上传速率限制
   23 RATELIMIT_UPLOAD_COUNT = 3  # 每分钟最多3次文件上传
   24 RATELIMIT_UPLOAD_PERIOD = 60  # 1分钟

  ---

  第三步：创建速率限制装饰器

  在 exam_system/utils/ 目录下创建新文件 RateLimitDecorator.py：

    1 """
    2 速率限制装饰器
    3 """
    4 from django_ratelimit.decorators import ratelimit
    5 from django.core.cache import cache
    6 from utils.ResponseMessage import MyResponse
    7 import logging
    8 
    9 logger = logging.getLogger('apps')
   10 
   11 
   12 def rate_limit_login(func):
   13     """
   14     登录接口速率限制：每分钟最多5次
   15     """
   16     @ratelimit(key='ip', rate='5/m', block=False)
   17     def _wrapped_view(request, *args, **kwargs):
   18         # 检查是否被限流
   19         if getattr(request, 'limited', False):
   20             logger.warning(f"IP {request.META.get('REMOTE_ADDR')} 登录请求过于频繁")
   21             return MyResponse.failed(message="登录请求过于频繁，请1分钟后再试")
   22         return func(request, *args, **kwargs)
   23     return _wrapped_view
   24 
   25 
   26 def rate_limit_api(func):
   27     """
   28     普通 API 速率限制：每分钟最多100次
   29     """
   30     @ratelimit(key='ip', rate='100/m', block=False)
   31     def _wrapped_view(request, *args, **kwargs):
   32         # 检查是否被限流
   33         if getattr(request, 'limited', False):
   34             logger.warning(f"IP {request.META.get('REMOTE_ADDR')} API请求过于频繁")
   35             return MyResponse.failed(message="请求过于频繁，请稍后再试")
   36         return func(request, *args, **kwargs)
   37     return _wrapped_view
   38 
   39 
   40 def rate_limit_sensitive(func):
   41     """
   42     敏感操作速率限制：每分钟最多10次
   43     用于删除、更新等敏感操作
   44     """
   45     @ratelimit(key='ip', rate='10/m', block=False)
   46     def _wrapped_view(request, *args, **kwargs):
   47         # 检查是否被限流
   48         if getattr(request, 'limited', False):
   49             logger.warning(f"IP {request.META.get('REMOTE_ADDR')} 敏感操作请求过于频繁")
   50             return MyResponse.failed(message="操作过于频繁，请稍后再试")
   51         return func(request, *args, **kwargs)
   52     return _wrapped_view
   53 
   54 
   55 def rate_limit_upload(func):
   56     """
   57     文件上传速率限制：每分钟最多3次
   58     """
   59     @ratelimit(key='ip', rate='3/m', block=False)
   60     def _wrapped_view(request, *args, **kwargs):
   61         # 检查是否被限流
   62         if getattr(request, 'limited', False):
   63             logger.warning(f"IP {request.META.get('REMOTE_ADDR')} 文件上传请求过于频繁")
   64             return MyResponse.failed(message="上传过于频繁，请1分钟后再试")
   65         return func(request, *args, **kwargs)
   66     return _wrapped_view
   67 
   68 
   69 def rate_limit_user_based(func):
   70     """
   71     基于用户的速率限制：每个用户每分钟最多50次
   72     需要用户已登录
   73     """
   74     def _wrapped_view(request, *args, **kwargs):
   75         # 获取用户ID
   76         user_id = getattr(request.user, 'id', None)
   77         if not user_id:
   78             # 未登录用户使用 IP 限制
   79             @ratelimit(key='ip', rate='50/m', block=False)
   80             def _rate_limited_view(request, *args, **kwargs):
   81                 if getattr(request, 'limited', False):
   82                     logger.warning(f"IP {request.META.get('REMOTE_ADDR')} 请求过于频繁")
   83                     return MyResponse.failed(message="请求过于频繁，请稍后再试")
   84                 return func(request, *args, **kwargs)
   85             return _rate_limited_view(request, *args, **kwargs)
   86         else:
   87             # 已登录用户使用用户ID限制
   88             @ratelimit(key='user_or_ip', rate='100/m', block=False)
   89             def _rate_limited_view(request, *args, **kwargs):
   90                 if getattr(request, 'limited', False):
   91                     logger.warning(f"用户 {request.user.username} 请求过于频繁")
   92                     return MyResponse.failed(message="请求过于频繁，请稍后再试")
   93                 return func(request, *args, **kwargs)
   94             return _rate_limited_view(request, *args, **kwargs)
   95     return _wrapped_view

  ---

  第四步：应用到各个接口

  1. 登录接口（apps/user/views.py）

  在文件顶部添加导入：

   1 from utils.RateLimitDecorator import rate_limit_login

  然后在登录方法上添加装饰器：

   1 class LoginView(APIView):
   2     @rate_limit_login  # 添加这一行
   3     def post(self, request):
   4         # ... 登录逻辑

  2. 删除和更新操作（所有 apps）

  在文件顶部添加导入：

   1 from utils.RateLimitDecorator import rate_limit_sensitive

  然后在删除和更新方法上添加装饰器：

  示例：题目删除

   1 class QuestionDeleteListView(APIView):
   2     @check_permission
   3     @rate_limit_sensitive  # 添加这一行
   4     def delete(self, request):
   5         # ... 删除逻辑

  示例：班级更新

   1 class ClassView(APIView):
   2     @check_permission
   3     @rate_limit_sensitive  # 添加这一行
   4     def put(self, request, class_id):
   5         # ... 更新逻辑

  3. 文件上传接口

  在文件顶部添加导入：

   1 from utils.RateLimitDecorator import rate_limit_upload

  然后在文件上传方法上添加装饰器：

   1 class QuestionImportView(APIView):
   2     @check_permission
   3     @rate_limit_upload  # 添加这一行
   4     def post(self, request):
   5         # ... 上传逻辑

  4. 普通 API 接口（可选）

  对于普通的查询接口，可以添加基础速率限制：

  在文件顶部添加导入：

   1 from utils.RateLimitDecorator import rate_limit_api

  然后在方法上添加装饰器：

   1 class QuestionListView(APIView):
   2     @rate_limit_api  # 添加这一行
   3     def get(self, request):
   4         # ... 查询逻辑

  ---

  第五步：全局中间件（可选）

  如果想要对所有接口应用基础速率限制，可以在 settings.py 的 MIDDLEWARE 中添加：

    1 MIDDLEWARE = [
    2     'corsheaders.middleware.CorsMiddleware',
    3     'django_ratelimit.middleware.RatelimitMiddleware',  # 添加这一行
    4     'django.middleware.security.SecurityMiddleware',
    5     'django.contrib.sessions.middleware.SessionMiddleware',
    6     'django.middleware.common.CommonMiddleware',
    7     'django.middleware.csrf.CsrfViewMiddleware',
    8     'django.contrib.auth.middleware.AuthenticationMiddleware',
    9     'django.contrib.messages.middleware.MessageMiddleware',
   10     'django.middleware.clickjacking.XFrameOptionsMiddleware',
   11 ]

  然后在 settings.py 中添加全局限流配置：

   1 # 全局速率限制
   2 RATELIMIT_ENABLE = True
   3 RATELIMIT_VIEW = 'utils.RateLimitDecorator.rate_limit_api'

  ---

  需要修改的文件清单

   1. ✅ exam_system/requirements.txt - 添加依赖
   2. ✅ exam_system/exam_system/settings.py - 添加配置
   3. ✅ exam_system/utils/RateLimitDecorator.py - 创建新文件
   4. ✅ exam_system/apps/user/views.py - 登录接口
   5. ✅ exam_system/apps/question/views.py - 题目相关接口
   6. ✅ exam_system/apps/exam/views.py - 试卷相关接口
   7. ✅ exam_system/apps/classes/views.py - 班级相关接口
   8. ✅ exam_system/apps/adminer/views.py - 管理员相关接口

  ---

  速率限制规则总结


  ┌────────────────────────┬────────────┬──────────────────────┐
  │ 接口类型               │ 限制规则   │ 装饰器               │
  ├────────────────────────┼────────────┼──────────────────────┤
  │ 登录接口               │ 5次/分钟   │ @rate_limit_login      │
  │ 敏感操作（删除、更新） │ 10次/分钟  │ @rate_limit_sensitive  │
  │ 文件上传               │ 3次/分钟   │ @rate_limit_upload     │
  │ 普通 API               │ 100次/分钟 │ @rate_limit_api        │
  │ 已登录用户             │ 100次/分钟 │ @rate_limit_user_based │
  └────────────────────────┴────────────┴──────────────────────┘

  ---

  优势

   1. ✅ 防止 DDoS 攻击
   2. ✅ 防止暴力破解
   3. ✅ 保护敏感操作
   4. ✅ 合理分配服务器资源
   5. ✅ 提高系统稳定性

✦ 按照这个方案实施后，你的 API 就具备了完善的速率限制保护机制！

  14. [中] 前端 Token 存储不安全
   - 位置: exam-frontend/src/stores/user.js
   - 问题描述: Token 存储在 Pinia store 中，可能持久化到 localStorage
   - 影响: XSS 攻击可以窃取 Token
   - 建议: 考虑使用 httpOnly cookie 存储 Token

  15. [中] 前端缺少 CSRF 保护
   - 位置: exam-frontend/src/utils/request.js
   - 问题描述: Axios 请求拦截器没有添加 CSRF token
   - 影响: 容易受到 CSRF 攻击
   - 建议: 实现 CSRF token 机制

  16. [中] 考试计时依赖客户端
   - 位置: exam-frontend/src/views/ExamTake.vue
   - 问题描述: 考试剩余时间在前端计算，用户可以通过修改客户端时间绕过时间限制
   - 影响: 考试公平性问题
   - 建议: 在服务器端验证考试时间，定期同步剩余时间

  17. [中] 缺少文件上传大小限制验证
   - 位置: exam_system/apps/question/views.py:288-292
   - 问题描述: 虽然检查了文件大小，但没有在服务器端进行二次验证
   - 影响: 可能绕过前端限制上传大文件
   - 建议: 在 Django settings 中配置全局文件上传大小限制

  18. [中] 缺少数据库事务管理
   - 位置: 多个创建/更新操作
   - 问题描述: 某些涉及多个表的操作没有使用事务
   - 影响: 可能导致数据不一致
   - 建议: 使用 @transaction.atomic 装饰器确保数据一致性


