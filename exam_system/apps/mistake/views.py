import logging
from rest_framework.views import APIView
from django.db.models import Count, Max, Min, Q
from django.core.cache import cache
from apps.question.models import Question
from apps.user.models import User
from apps.exam.models import AnswerRecord, ExamRecord
from apps.mistake.models import Mistake
from utils.ResponseMessage import check_auth, MyResponse
from utils.CacheConfig import (
    CACHE_KEY_MISTAKE_LIST,
    CACHE_TIMEOUT_MISTAKE_LIST,
    generate_cache_key,
    generate_filter_key,
    get_cache_timeout,
)
from utils.CacheTools import cache_delete_pattern

logger = logging.getLogger('apps')


# # 没有使用错题本表实现，学生的错题统计
# class MistakeListWithStatisticsView(APIView):
#     @check_auth
#     def get(self, request):
#         payload = request.user
#
#         user_id = payload.get("id")
#         # 判断用户是否存在
#         try:
#             student = User.objects.get(id=user_id)
#         except User.DoesNotExist:
#             return MyResponse.failed(message="学生信息不存在")
#
#         request_data = request.GET
#
#         page = int(request_data.get("page", 1))
#         page_size = int(request_data.get("size", 10))
#         offset = (page - 1) * page_size
#         # 构建筛选条件
#         filter_body = {}
#         for k, v in request_data.items():
#             if k in ["page", "size"]:
#                 continue
#             elif v:
#                 filter_body[f"question__{k}__icontains"] = v
#
#         # 构建响应数据
#         response_data = {
#             "list": [],
#             "page": page,
#             "size": page_size,
#             "total": 0,
#             "statistics": {
#                 "total_mistakes": 0,
#                 "unique_questions": 0,
#                 "type_distribution": {},
#                 "category_distribution": {},
#                 "recent_mistakes": [],
#             },
#         }
#         # 获取学生参加的考试id
#         exam_record_ids = ExamRecord.objects.filter(
#             user_id=user_id, status="graded"
#         ).values_list("id", flat=True).distinct()
#         # print(exam_record_ids)
#         if not exam_record_ids:
#             return MyResponse.success(message="暂时没有错误题目信息", data=response_data)
#
#         # 获取符合条件的，学生错误的题目
#         answer_records = AnswerRecord.objects.filter(
#             **filter_body,
#             exam_record_id__in=exam_record_ids,
#             is_correct=0
#         ).select_related("question", "exam_record__exam")
#
#         if not answer_records.exists():
#             return MyResponse.success(message="暂时没有错误题目信息", data=response_data)
#
#         # 获取学生每一个题目的错误次数和最后一次错误时间
#         mistake_stats = answer_records.values("question_id").annotate(
#             mistake_count=Count("question_id"),
#             last_mistake_time=Max("create_time"),
#         ).order_by("-last_mistake_time")
#
#         total = mistake_stats.count()
#         # 分页
#         mistake_stats_page = mistake_stats[offset:offset + page_size]
#         # 学生参加的考试中的错误题目的id
#         question_ids = [ms["question_id"] for ms in mistake_stats_page]
#         # print(question_ids)
#
#         # 获取错误题目的，题目信息
#         correct_questions = Question.objects.filter(id__in=question_ids)
#         question_map = {q.id: q for q in correct_questions}
#         # print(correct_questions)
#
#         # 获取最后一次答题记录（用于获取用户答案和考试标题）
#         last_answer_records = {}
#         for record in answer_records:
#             qid = record.question_id
#             if qid not in last_answer_records or record.create_time > last_answer_records[qid].create_time:
#                 last_answer_records[qid] = record
#
#         # 构建相应数据中的错误题目
#         response_list = []
#         for ms in mistake_stats_page:
#             qid = ms["question_id"]
#             question = question_map.get(qid)
#             last_record = last_answer_records.get(qid)
#             if not question or not last_record:
#                 continue
#             data = {
#                 "id": len(response_list) + 1,
#                 "question_id": question.id,
#                 "type": question.type,
#                 "category": question.category,
#                 "content": question.content,
#                 "options": question.options,
#                 "user_answer": last_record.user_answer,
#                 "correct_answer": question.answer,
#                 "analysis": question.analysis,
#                 "mistake_count": ms["mistake_count"],
#                 "last_mistake_time": ms["last_mistake_time"].strftime("%Y-%m-%d %H:%M:%S"),
#                 "exam_title": last_record.exam_record.exam.title if last_record.exam_record else ""
#             }
#             response_list.append(data)
#
#         response_data["list"] = response_list
#         response_data["total"] = total
#
#         # 获取统计信息
#         statistics = {
#             "total_mistakes": answer_records.count(),
#             "unique_questions": total,
#             "type_distribution": {},
#             "category_distribution": {},
#             "recent_mistakes": []
#         }
#
#         for ms in mistake_stats:
#             qid = ms["question_id"]
#             question = question_map.get(qid)
#
#             # 跳过已删除的题目
#             if not question:
#                 continue
#
#             statistics["type_distribution"][question.type] = statistics["type_distribution"].get(question.type, 0) + 1
#             statistics["category_distribution"][question.category] = statistics["category_distribution"].get(question.category, 0) + 1
#             statistics["recent_mistakes"].append({
#                 "question_id": ms["question_id"],
#                 "mistake_count": ms["mistake_count"],
#                 "last_mistake_time": ms["last_mistake_time"].strftime("%Y-%m-%d %H:%M:%S"),
#             })
#
#         response_data["statistics"] = statistics
#         return MyResponse.success(data=response_data)


# 使用错题本表实现，学生的错题
class MistakeListWithStatisticsView(APIView):
    @check_auth
    def get(self, request):
        payload = request.user

        user_id = payload.get("id")
        # 判断用户是否存在
        try:
            student = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return MyResponse.failed(message="学生信息不存在")

        request_data = request.GET

        page = int(request_data.get("page", 1))
        page_size = int(request_data.get("size", 10))
        offset = (page - 1) * page_size
        # 构建筛选条件
        filter_body = {}
        for k, v in request_data.items():
            if k in ["page", "size"]:
                continue
            elif v:
                filter_body[f"question__{k}__icontains"] = v

        # 构建缓存键
        cache_filters = generate_filter_key(filter_body)
        cache_key = generate_cache_key(
            CACHE_KEY_MISTAKE_LIST, user_id=user_id, filter=cache_filters, page=page, size=page_size
        )
        # 获取缓存数据
        cache_data = cache.get(cache_key)
        if cache_data:
            return MyResponse.success(data=cache_data)

        # 构建响应数据
        response_data = {
            "list": [],
            "page": page,
            "size": page_size,
            "total": 0,
            "statistics": {
                "total_mistakes": 0,
                "unique_questions": 0,
                "type_distribution": {},
                "category_distribution": {},
                "recent_mistakes": [],
            },
        }

        # 获取用户的错题
        user_mistakes = Mistake.objects.filter(
            user_id=user_id, is_mastered=0, **filter_body
        ).select_related("question", "exam_record__exam").order_by("-mistake_count")
        # print(user_mistakes)
        if not user_mistakes.exists():
            return MyResponse.success(data=response_data)

        total = user_mistakes.count()
        response_data["total"] = total
        # 分页
        user_mistakes_page = user_mistakes[offset:offset + page_size]
        # 获取当前页错题的题目ID和考试记录ID
        mistakes_question_ids = [um.question.id for um in user_mistakes_page]
        mistakes_exam_record_ids = list(set([um.exam_record.id for um in user_mistakes_page]))
        # print(mistakes_question_ids, mistakes_exam_record_ids)

        # 获取学生答题记录
        if mistakes_exam_record_ids and mistakes_question_ids:
            all_answer_records = AnswerRecord.objects.filter(
                exam_record_id__in=mistakes_exam_record_ids,
                question_id__in=mistakes_question_ids,
                is_correct=0
            ).select_related("exam_record__exam").order_by("create_time")
            # print(all_answer_records)
            # 构建学生答题记录，学生答案和试卷title映射
            answer_record_map = {}
            for ar in all_answer_records:
                qid = ar.question_id
                if qid not in answer_record_map or ar.create_time > answer_record_map[qid]["create_time"]:
                    answer_record_map[qid] = {
                        "user_answer": ar.user_answer,
                        "exam_title": ar.exam_record.exam.title if ar.exam_record and ar.exam_record.exam else "",
                        "create_time": ar.create_time
                    }
        else:
            answer_record_map = {}

        # print(answer_record_map)
        question_list = []

        for um in user_mistakes_page:
            if not um.question:
                continue
            question_id = um.question.id
            mistake_count = um.mistake_count
            last_mistake_time = um.last_mistake_time.strftime("%Y-%m-%d %H:%M:%S") if um.last_mistake_time else ""

            # 获取用户答案和考试标题
            answer_info = answer_record_map.get(question_id, {})
            user_answer = answer_info.get("user_answer", "")
            exam_title = answer_info.get("exam_title", "")
            data = {
                "id": um.id,
                "question_id": question_id,
                "type": um.question.type,
                "category": um.question.category,
                "content": um.question.content,
                "options": um.question.options,
                "user_answer": user_answer,
                "correct_answer": um.question.answer,
                "analysis": um.question.analysis,
                "mistake_count": mistake_count,
                "last_mistake_time": last_mistake_time,
                "exam_title": exam_title,
            }
            question_list.append(data)

        statistics = {
            "total_mistakes": 0,
            "unique_questions": total,
            "type_distribution": {},
            "category_distribution": {},
            "recent_mistakes": [],
        }
        total_mistakes = 0
        for um in user_mistakes:
            if not um.question:
                continue

            total_mistakes += um.mistake_count

            # 统计类型分布
            q_type = um.question.type
            statistics["type_distribution"][q_type] = statistics["type_distribution"].get(q_type, 0) + 1

            # 统计分类分布
            q_category = um.question.category
            statistics["category_distribution"][q_category] = statistics["category_distribution"].get(q_category, 0) + 1
            # 最近错误

            last_mistake_time = um.last_mistake_time.strftime("%Y-%m-%d %H:%M:%S") if um.last_mistake_time else ""
            statistics["recent_mistakes"].append({
                "question_id": um.question.id,
                "mistake_count": um.mistake_count,
                "last_mistake_time": last_mistake_time
            })

        statistics["total_mistakes"] = total_mistakes
        # 错题题目id
        response_data["list"] = question_list
        response_data["statistics"] = statistics
        # 设置缓存
        cache.set(cache_key, response_data, get_cache_timeout(CACHE_TIMEOUT_MISTAKE_LIST))
        return MyResponse.success(data=response_data)


class MistakeMasteredView(APIView):
    @check_auth
    def put(self, request, mistake_id):
        payload = request.user

        if payload.get("role") != "student":
            return MyResponse.failed(message="没有权限修改")
        user_id = payload.get("id")
        try:
            mistake = Mistake.objects.get(id=mistake_id, user_id=user_id, is_mastered=0)
        except Mistake.DoesNotExist:
            return MyResponse.failed(message="错题信息不存在")

        mistake.is_mastered = 1
        mistake.save()

        logger.info(f"学生 {payload.get('username')} 标记错题为已掌握，错题ID: {mistake_id}")
        # 清除错题列表缓存
        cache_delete_pattern("mistake:list:*")

        return MyResponse.success(message="标记成功")


import pandas as pd
import io
from django.http import FileResponse
from urllib.parse import quote

# 题目类型映射常量
QUESTION_TYPE_MAP = {
    "single": "单选题",
    "multiple": "多选题",
    "judge": "判断题",
    "fill": "填空题",
}

# 难度映射常量
DIFFICULTY_MAP = {
    "easy": "简单",
    "medium": "中等",
    "hard": "困难",
}



class MistakeExportView(APIView):
    @check_auth
    def post(self, request):
        payload = request.user

        if payload.get("role") != "student":
            return MyResponse.failed(message="没有权限导出错题")

        user_id = payload.get("id")
        # 判断学生信息是否存在
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return MyResponse.failed(message="用户信息不存在")

        # 获取学生的错题信息
        user_mistakes = Mistake.objects.filter(
            user_id=user_id, is_mastered=0
        ).select_related("question", "exam_record__exam").order_by("-mistake_count")

        if not user_mistakes.exists():
            return MyResponse.failed(message="没有错题，无法导出")

        # 获取当前页错题的题目ID和考试记录ID
        mistakes_question_ids = [um.question.id for um in user_mistakes]
        mistakes_exam_record_ids = list(set([um.exam_record.id for um in user_mistakes]))


        # 获取学生答题记录
        if mistakes_exam_record_ids and mistakes_question_ids:
            all_answer_records = AnswerRecord.objects.filter(
                exam_record_id__in=mistakes_exam_record_ids,
                question_id__in=mistakes_question_ids,
                is_correct=0
            ).select_related("exam_record__exam").order_by("create_time")
            # print(all_answer_records)
            # 构建学生答题记录，学生答案和试卷title映射
            answer_record_map = {}
            for ar in all_answer_records:
                qid = ar.question_id
                if qid not in answer_record_map or ar.create_time > answer_record_map[qid]["create_time"]:
                    answer_record_map[qid] = {
                        "user_answer": ar.user_answer,
                        "exam_title": ar.exam_record.exam.title if ar.exam_record and ar.exam_record.exam else "",
                        "create_time": ar.create_time
                    }
        else:
            answer_record_map = {}

        # print(answer_record_map)
        question_list = []

        for um in user_mistakes:
            if not um.question:
                continue
            question_id = um.question.id
            mistake_count = um.mistake_count
            last_mistake_time = um.last_mistake_time.strftime("%Y-%m-%d %H:%M:%S") if um.last_mistake_time else ""

            # 获取用户答案和考试标题
            answer_info = answer_record_map.get(question_id, {})
            user_answer = answer_info.get("user_answer", "")
            exam_title = answer_info.get("exam_title", "")
            data = {
                "question_id": question_id,
                "type": um.question.type,
                "category": um.question.category,
                "content": um.question.content,
                "options": um.question.options,
                "user_answer": user_answer,
                "correct_answer": um.question.answer,
                "analysis": um.question.analysis,
                "mistake_count": mistake_count,
                "last_mistake_time": last_mistake_time,
                "exam_title": exam_title,
            }
            question_list.append(data)

        try:
            # 使用内存流生成文件
            excel_buffer = self.export_to_excel(question_list)

            logger.info(f"学生 {user.username} 导出错题本成功，数量: {len(question_list)}")

            # 返回文件供前端下载
            filename = f"错题本导出_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            encoded_filename = quote(filename)

            response = FileResponse(
                excel_buffer,
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            response['Content-Disposition'] = f'attachment; filename*=UTF-8\'\'{encoded_filename}'
            return response
        except Exception as e:
            logger.error(f"学生 {user.username} 导出错题本失败: {e}")
            return MyResponse.failed(f"导出文件是发生错误，{e}")



    def export_to_excel(self, questions):
        frame = {
            "题目类型": [],
            "题目分类": [],
            "题目内容": [],
            "选项A": [],
            "选项B": [],
            "选项C": [],
            "选项D": [],
            "学生答案": [],
            "正确答案": [],
            "题目解析": [],
            "错误次数": [],
            "最后一次错误时间": [],
            "试卷题目": [],
        }

        for question in questions:
            frame['题目类型'].append(QUESTION_TYPE_MAP.get(question["type"]))
            frame['题目分类'].append(question["category"])
            frame['题目内容'].append(question["content"])

            if question.get("options") and question["type"] != 'judge':
                frame['选项A'].append(question.get("options").get("A", ""))
                frame['选项B'].append(question.get("options").get("B", ""))
                frame['选项C'].append(question.get("options").get("C", ""))
                frame['选项D'].append(question.get("options").get("D", ""))
            else:
                frame['选项A'].append("")
                frame['选项B'].append("")
                frame['选项C'].append("")
                frame['选项D'].append("")

            if question["type"] == "judge":
                user_answer = question.get("user_answer", "").upper()
                correct_answer = question.get("correct_answer", "").upper()
                frame['学生答案'].append("正确" if user_answer == "A" else ("错误" if user_answer == "B" else ""))
                frame['正确答案'].append("正确" if correct_answer == "A" else ("错误" if correct_answer == "B" else ""))
            else:
                frame['学生答案'].append(question.get("user_answer", ""))
                frame['正确答案'].append(question.get("correct_answer", ""))

            frame['题目解析'].append(question["analysis"])
            frame['错误次数'].append(question["mistake_count"])
            frame['最后一次错误时间'].append(question["last_mistake_time"])
            frame['试卷题目'].append(question["exam_title"])

        # 创建 DataFrame
        df = pd.DataFrame(frame)

        # 使用内存流代替临时文件
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='错题列表', index=False)

        # 重置指针到开头
        output.seek(0)
        return output