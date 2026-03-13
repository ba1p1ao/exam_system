import logging
from unicodedata import category

import pandas as pd
import io
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.generics import RetrieveAPIView, CreateAPIView, UpdateAPIView, DestroyAPIView
from django.http import FileResponse
from urllib.parse import quote
from apps.question.serializers import QuestionListSerializers, QuestionSerializers, QuestionAddSerializers
from apps.question.models import Question
from apps.user.models import User
from utils.ResponseMessage import MyResponse, check_permission
from django.db import transaction
from utils.CacheConfig import (
    CACHE_KEY_QUESTION_LIST,
    CACHE_TIMEOUT_QUESTION_LIST,
    CACHE_KEY_QUESTION_DETAIL,
    CACHE_TIMEOUT_QUESTION_DETAIL,
    generate_cache_key,
    generate_filter_key, CACHE_KEY_SYSTEM_STATISTICS, CACHE_TIMEOUT_EMPTY_RESULT,
    get_cache_timeout, CACHE_KEY_USER_STATISTICS,
)
from utils.CacheTools import cache_delete_pattern
from django.core.cache import cache


logger = logging.getLogger('apps')

# 题目类型映射常量
QUESTION_TYPE_MAP = {
    # 导入用
    "单选题": "single",
    "单选": "single",
    "多选题": "multiple",
    "多选": "multiple",
    "判断题": "judge",
    "判断": "judge",
    "填空题": "fill",
    "填空": "fill",
    # 导出用
    "single": "单选题",
    "multiple": "多选题",
    "judge": "判断题",
    "fill": "填空题",
}

# 难度映射常量
DIFFICULTY_MAP = {
    # 导入用
    "简单": "easy",
    "中等": "medium",
    "困难": "hard",
    # 导出用
    "easy": "简单",
    "medium": "中等",
    "hard": "困难",
}

# 添加验证函数
def validate_import_question(question_data, index):
    """
    验证导入的题目数据
    Args:
       question_data: 题目数据字典
        index: 行号

    Returns:
        (is_valid, error_message): (是否有效, 错误信息)
    """

    # 验证题目类型
    valid_types = ["single", "multiple", "judge", "fill"]
    if not question_data.get("type") or question_data["type"] not in valid_types:
        return False, f"题目类型无效，必须是：单选题、多选题、判断题、填空题"

    # 验证题目内容
    content = question_data.get("content")
    if not content or not isinstance(content, str):
        return False, "题目内容不能为空"
    if len(content) > 2000:
        return False, f"题目内容过长，最多2000个字符（当前{len(content)}个）"

    # 验证正确答案
    answer = question_data.get("answer")
    if not answer or not isinstance(answer, str):
        return False, "正确答案不能为空"
    if len(answer) > 500:
        return False, f"正确答案过长，最多500个字符（当前{len(answer)}个）"

    # 验证题目分类
    category = question_data.get("category")
    if category and len(str(category)) > 100:
        return False, f"题目分类过长，最多100个字符"

    # 验证题目解析
    analysis = question_data.get("analysis")
    if analysis and len(str(analysis)) > 2000:
        return False, f"题目解析过长，最多2000个字符"

    # 验证难度
    valid_difficulties = ["easy", "medium", "hard"]
    difficulty = question_data.get("difficulty")
    if difficulty and difficulty not in valid_difficulties:
        return False, "难度无效，必须是：简单、中等、困难"

    # 验证分值
    score = question_data.get("score")
    if score is not None:
        try:
            score = float(score)
            if score <= 0 or score > 100:
                return False, f"分值必须在1-100之间（当前{score}）"
            question_data["score"] = score
        except (ValueError, TypeError):
            return False, "分值必须是数字"
    else:
        question_data["score"] = 10  # 设置默认分值

    # 验证选项（单选和多选题需要选项）
    question_type = question_data.get("type")
    options = question_data.get("options")

    if question_type in ["single", "multiple"]:
        if not options or not isinstance(options, dict):
            return False, "单选和多选题必须包含选项"

        valid_option_keys = ["A", "B", "C", "D"]
        for key in valid_option_keys:
            option_value = options.get(key)
            if option_value and len(str(option_value)) > 500:
                return False, f"选项{key}过长，最多500个字符"

    # 验证填空题答案格式
    if question_type == "fill":
        # 填空题答案可以用 | 分隔多个答案
        answers = [a.strip() for a in answer.split("|")]
        if len(answers) == 0:
            return False, "填空题答案不能为空"
        for ans in answers:
            if len(ans) > 200:
                return False, f"填空题答案过长，每个答案最多200个字符"

    # 验证多选题答案格式
    if question_type == "multiple":
        # 多选题答案应该是多个字母，如 "AB" 或 "ABC"
        valid_answers = set("ABCD")
        answer_set = set(answer.upper())
        if not answer_set.issubset(valid_answers):
            return False, f"多选题答案格式错误，应该是字母组合（如 AB、ABC、ABCD）"

    # 验证判断题答案格式
    if question_type == "judge":
        if answer not in ["A", "B", "正确", "错误", "true", "false"]:
            return False, "判断题答案必须是：正确/错误"

    # 清理数据：去除首尾空格
    for key in ["content", "category", "answer", "analysis"]:
        if question_data.get(key) and isinstance(question_data[key], str):
            question_data[key] = question_data[key].strip()

    return True, None



class QuestionListView(APIView):

    def get(self, request):
        payload = request.user
        if not payload:
            return MyResponse.other(code=403, message="用户信息已过期，请重新登录")

        if payload.get("role") not in ["teacher", "admin"]:
            return MyResponse.other(code=403, message="只有教师和管理员可以访问题库")

        filter_body = {}
        request_data = request.GET
        for k, v in request_data.items():
            if k == "page" or k == "size":
                continue
            elif k == "content" and v:
                filter_body["content__icontains"] = v
            elif v:
                filter_body[k] = v

        page = int(request_data.get("page", 1))
        page_size = int(request_data.get("size", 10))
        offset = (page - 1) * page_size

        # 生成缓存键
        filters = generate_filter_key(filter_body)
        cache_key = generate_cache_key(
            CACHE_KEY_QUESTION_LIST, filter=filters, page=page, size=page_size
        )
        # 尝试从缓存获取
        cache_data = cache.get(cache_key)
        if cache_data:
           return MyResponse.success(data=cache_data)

        question_list = Question.objects.filter(**filter_body).all().order_by("-update_time")
        page_list = question_list[offset:offset + page_size]
        ser_data = QuestionSerializers(instance=page_list, many=True).data
        response_data = {
            "list": ser_data,
            "total": len(question_list),
            "page": page,
            "size": page_size,
        }
        # 这是缓存
        if not ser_data:
            cache.set(cache_key, response_data, get_cache_timeout(CACHE_TIMEOUT_EMPTY_RESULT))
        else:
            cache.set(cache_key, response_data, get_cache_timeout(CACHE_TIMEOUT_QUESTION_LIST))
        return MyResponse.success(data=response_data)


class QuestionInfoView(RetrieveAPIView, UpdateAPIView, DestroyAPIView):
    queryset = Question.objects
    serializer_class = QuestionSerializers
    lookup_field = "id"

    def get_payload(self):
        payload = self.request.user

        if not payload:
            return MyResponse.other(code=403, message="用户信息已过期，请重新登录")

        if payload.get("role") not in ["teacher", "admin"]:
            return MyResponse.other(code=403, message="只有教师和管理员可以访问题库")

    def retrieve(self, request, *args, **kwargs):
        payload = self.get_payload()
        if isinstance(payload, MyResponse):
            return payload
        question = self.get_object()

        # 设置 cache key
        cache_key = generate_cache_key(CACHE_KEY_QUESTION_DETAIL, id=question.id)
        # 获取 缓存数据
        cache_data = cache.get(cache_key)
        if cache_data:
            return MyResponse.success(data=cache_data)

        ser_data = self.get_serializer(instance=question).data
        cache.set(cache_key, ser_data, get_cache_timeout(CACHE_TIMEOUT_QUESTION_DETAIL))
        return MyResponse.success(data=ser_data)

    def update(self, request, *args, **kwargs):
        payload = self.get_payload()
        if isinstance(payload, MyResponse):
            return payload

        question = self.get_object()
        request_data = request.data

        question_ser = QuestionAddSerializers(instance=question, data=request_data, partial=True)
        try:
            if question_ser.is_valid(raise_exception=True):
                question_ser.save()
                logger.info(f"题目 ID {question.id} 更新成功")
                cache.delete(generate_cache_key(CACHE_KEY_QUESTION_DETAIL, id=question.id))
                cache_delete_pattern("question:list:*")
                # 清除包含这些题目的考试题目缓存
                cache_delete_pattern("exam:questions:*")
                # 清除考试相关缓存
                cache_delete_pattern("exam:list:*")
                cache_delete_pattern("exam:detail:*")
                cache_delete_pattern("exam:statistics:*")
                cache_delete_pattern("exam:ranking:*")
                # 清除班级相关缓存（因为班级统计、排名、趋势都依赖题目）
                cache_delete_pattern("class:ranking:*")
                cache_delete_pattern("class:trend:*")
                cache_delete_pattern("class:statistics:*")
                # 清除用户统计缓存
                cache.delete(CACHE_KEY_USER_STATISTICS)
                # 清除系统统计缓存
                cache.delete(CACHE_KEY_SYSTEM_STATISTICS)
                return MyResponse.success("更新成功")
        except Exception as e:
            logger.error(f"题目 ID {question.id} 更新失败: {e}")
            return MyResponse.failed(message=f"题目 ID {question.id} 更新失败")

    def destroy(self, request, *args, **kwargs):
        payload = self.get_payload()
        if isinstance(payload, MyResponse):
            return payload
        question = self.get_object()
        question_id = question.id
        self.perform_destroy(question)
        logger.info(f"题目 ID {question_id} 删除成功")
        cache.delete(generate_cache_key(CACHE_KEY_QUESTION_DETAIL, id=question_id))
        cache_delete_pattern("question:list:*")
        # 清除包含这些题目的考试题目缓存
        cache_delete_pattern("exam:questions:*")
        # 清除考试相关缓存
        cache_delete_pattern("exam:list:*")
        cache_delete_pattern("exam:detail:*")
        cache_delete_pattern("exam:statistics:*")
        cache_delete_pattern("exam:ranking:*")
        # 清除班级相关缓存（因为班级统计、排名、趋势都依赖题目）
        cache_delete_pattern("class:ranking:*")
        cache_delete_pattern("class:trend:*")
        cache_delete_pattern("class:statistics:*")
        # 清除用户统计缓存
        cache.delete(CACHE_KEY_USER_STATISTICS)
        # 清除系统统计缓存
        cache.delete(CACHE_KEY_SYSTEM_STATISTICS)
        return MyResponse.success("删除成功")


class QuestionAddView(CreateAPIView):
    queryset = Question.objects
    serializer_class = QuestionAddSerializers

    def create(self, request, *args, **kwargs):
        payload = request.user
        if not payload:
            return MyResponse.other(code=403, message="用户信息已过期，请重新登录")

        if payload.get("role") not in ["teacher", "admin"]:
            return MyResponse.other(code=403, message="只有教师和管理员可以访问题库")
        request_data = request.data
        request_data["creator"] = payload.get("id")
        question_ser = self.get_serializer(data=request_data)
        try:
            if question_ser.is_valid(raise_exception=True):
                question_ser.save()
                logger.info(f"用户 {payload.get('username')} 添加题目成功")
                cache_delete_pattern("question:list:*")
                # 清除考试相关缓存（因为新题目可能被添加到试卷）
                cache_delete_pattern("exam:questions:*")
                # 清除系统统计缓存
                cache.delete(CACHE_KEY_SYSTEM_STATISTICS)
                return MyResponse.success(message='添加成功', data={"id": payload.get("id")})
        except Exception as e:
            logger.error(f"用户 {payload.get('username')} 添加题目失败: {e}")
            return MyResponse.failed(message=e)


class QuestionDeleteListView(APIView):
    @check_permission
    def delete(self, request):
        payload = request.user
        if not payload:
            return MyResponse.other(code=403, message="用户信息已过期，请重新登录")

        if payload.get("role") not in ["teacher", "admin"]:
            return MyResponse.other(code=403, message="只有教师和管理员可以访问题库")

        ids = request.data.get("ids")
        if not ids:
            return MyResponse.other(code=404, message="请选择要删除的题目")

        delete_count = Question.objects.filter(id__in=ids).delete()
        if delete_count:
            logger.info(f"用户 {payload.get('username')} 批量删除题目成功，数量: {len(ids)}")
            cache.delete_many([generate_cache_key(CACHE_KEY_QUESTION_DETAIL, id=id) for id in ids])
            cache_delete_pattern("question:list:*")
            # 清除包含这些题目的考试题目缓存
            cache_delete_pattern("exam:questions:*")
            # 清除考试相关缓存
            cache_delete_pattern("exam:list:*")
            cache_delete_pattern("exam:detail:*")
            cache_delete_pattern("exam:statistics:*")
            cache_delete_pattern("exam:ranking:*")
            # 清除班级相关缓存（因为班级统计、排名、趋势都依赖题目）
            cache_delete_pattern("class:ranking:*")
            cache_delete_pattern("class:trend:*")
            cache_delete_pattern("class:statistics:*")
            # 清除用户统计缓存
            cache.delete(CACHE_KEY_USER_STATISTICS)
            # 清除系统统计缓存
            cache.delete(CACHE_KEY_SYSTEM_STATISTICS)

            return MyResponse.success(message="批量删除成功")
        return MyResponse.other(code=404, message="请选择要删除的题目")



class QuestionImportView(APIView):
    # 添加文件解析器
    parser_classes = [MultiPartParser, FormParser]

    # 文件上传大小限制（字节）
    MAX_FILE_SIZE = 50 * 1024 * 1024 # 50MB

    @check_permission
    def post(self, request):
        payload = request.user

        question_file = request.FILES.get("file")
        if not question_file:
            return MyResponse.failed("只能上传 .xlsx/.xls 文件，且不超过 10MB ")

        if question_file.size > self.MAX_FILE_SIZE:
            return MyResponse.failed(f"文件大小超过限制，最大允许 {self.MAX_FILE_SIZE // (1024 * 1024)}MB")


        file_name = question_file.name.lower()
        if not (file_name.endswith(".xlsx") or file_name.endswith(".xls")):
            return MyResponse.failed("只能上传 .xlsx/.xls 文件")

        df = pd.read_excel(question_file)
        result = self.process_import_data(df)
        if result.get("error"):
            return MyResponse.failed(message=result["error"])

        questions = result["questions"]

        current_user = User.objects.get(id=payload.get("id"))
        response_data = {
            "total": len(questions),
            "success": 0,
            "failed": 0,
            "failed_list": []
        }
        try:
            success_count = 0
            failed_count = 0
            failed_list = []
            valid_questions = []

            with transaction.atomic():
                for question in questions:
                    # 检查是否有验证错误
                    if question.get("error"):
                        failed_count += 1
                        failed_list.append({
                            "row": question["index"],
                            "reason": question["error"],
                        })
                        continue

                    # 移除不需要的字段
                    question_index = question.pop("index")
                    question.pop("error", None)

                    # 设置创建者
                    question["creator"] = current_user

                    valid_questions.append(Question(**question))
                    success_count += 1

                # 批量创建题目
                if valid_questions:
                    Question.objects.bulk_create(valid_questions)

                response_data["success"] = success_count
                response_data["failed"] = failed_count
                response_data["failed_list"] = failed_list
                logger.info(f"用户 {current_user.username} 导入题目成功，成功: {success_count}，失败: {failed_count}")
                # 清除题目列表缓存
                cache_delete_pattern("question:list:*")
                # 清除系统统计缓存
                cache.delete(CACHE_KEY_SYSTEM_STATISTICS)
                return MyResponse.success(message="题目导入成功", data=response_data)
        except Exception as e:
            logger.error(f"用户 {payload.get('username')} 导入题目失败: {e}")
            return MyResponse.failed(f"题目导入失败，{e}")


    def process_import_data(self, df):
        questions = []
        try:
            # 验证必需的列是否存在
            required_columns = ["题目类型", "题目内容", "正确答案"]
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                return {
                    "error": f"Excel文件缺少必需的列：{', '.join(missing_columns)}",
                    "questions": []
                }

                # 限制最大导入数量
            max_import_count = 1000
            if len(df) > max_import_count:
                return {
                    "error": f"一次最多导入{max_import_count}道题目，当前有{len(df)}道",
                    "questions": []
                }

            for index, row in df.iterrows():
                question = {}
                question["index"] = index + 2  # +2 因为Excel从第2行开始（第1行是表头）

                # 获取题目类型，处理NaN值
                type_value = row.get("题目类型")
                if pd.isna(type_value) or not isinstance(type_value, str):
                    question["type"] = None
                else:
                    question["type"] = QUESTION_TYPE_MAP.get(row["题目类型"])

                # 获取题目分类
                category = row.get("题目分类")
                question["category"] = category if not pd.isna(category) else ""

                # 获取题目内容
                content = row.get("题目内容")
                question["content"] = content if not pd.isna(content) else ""

                # 获取选项
                question["options"] = None
                if question["type"] == "fill":
                    question["options"] = None
                elif question["type"] == "judge":
                    question["options"] = {"A": "正确", "B": "错误"}
                else:
                    options = {}
                    for key in ["A", "B", "C", "D"]:
                        option_key = f"选项{key}"
                        option_value = row.get(option_key)
                        options[key] = option_value if not pd.isna(option_value) else ""
                    question["options"] = options

                # 获取正确答案
                answer = row.get("正确答案")
                question["answer"] = answer if not pd.isna(answer) else ""

                # 获取题目解析
                analysis = row.get("题目解析")
                question["analysis"] = analysis if not pd.isna(analysis) else ""

                # 获取难度
                difficulty_value = row.get("难度")
                if pd.isna(difficulty_value) or not isinstance(difficulty_value, str):
                    question["difficulty"] = None
                else:
                    question["difficulty"] = DIFFICULTY_MAP.get(difficulty_value.strip())

                # 获取分值
                score = row.get("分值")
                question["score"] = score if not pd.isna(score) else 10

                # 验证题目数据
                is_valid, error_message = validate_import_question(question, question["index"])
                if not is_valid:
                    question["error"] = error_message

                questions.append(question)

            return {"error": None, "questions": questions}

        except Exception as e:
            return {
                "error": "格式存在错误，请下载导入模板，按模板的格式填写",
                "questions": []
            }


class QuestionExportView(APIView):
    @check_permission
    def post(self, request):
        ids = request.data.get("ids")
        questions = Question.objects.filter(id__in=ids)
        if not questions:
            return MyResponse.failed(message="请选择要导出的题目")
        ser_question_data = QuestionListSerializers(instance=questions, many=True).data

        try:
            # 使用内存流生成文件
            excel_buffer = self.export_to_excel(ser_question_data)

            logger.info(f"用户 {request.user.get('username')} 导出题目成功，数量: {len(ids)}")

            # 返回文件供前端下载
            filename = f"题目导出_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            encoded_filename = quote(filename)

            response = FileResponse(
                excel_buffer,
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            response['Content-Disposition'] = f'attachment; filename*=UTF-8\'\'{encoded_filename}'
            return response
        except Exception as e:
            logger.error(f"用户 {request.user.get('username')} 导出题目失败: {e}")
            return MyResponse.failed(f"到处文件是发生错误，{e}")


    def export_to_excel(self, questions):
        frame = {
            "题目类型": [],
            "题目分类": [],
            "题目内容": [],
            "选项A": [],
            "选项B": [],
            "选项C": [],
            "选项D": [],
            "正确答案": [],
            "题目解析": [],
            "难度": [],
            "分值": [],
        }

        for question in questions:
            frame['题目类型'].append(QUESTION_TYPE_MAP.get(question["type"]))
            frame['题目分类'].append(question["category"])
            frame['题目内容'].append(question["content"])

            options = question.get("options")
            if options and question["type"] != 'judge':
                frame['选项A'].append(options.get("A"))
                frame['选项B'].append(options.get("B"))
                frame['选项C'].append(options.get("C"))
                frame['选项D'].append(options.get("D"))
            else:
                frame['选项A'].append(None)
                frame['选项B'].append(None)
                frame['选项C'].append(None)
                frame['选项D'].append(None)

            frame['正确答案'].append(question["answer"])
            frame['题目解析'].append(question["analysis"])
            frame['难度'].append(DIFFICULTY_MAP.get(question["difficulty"]))
            frame['分值'].append(question["score"])

        # 创建 DataFrame
        df = pd.DataFrame(frame)

        # 使用内存流代替临时文件
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='题目列表', index=False)

        # 重置指针到开头
        output.seek(0)
        return output