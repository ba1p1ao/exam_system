import pymysql
import time

# # 创建数据库连接
# db = pymysql.connect(
#     host="localhost",  # 数据库主机地址
#     user="root",  # 用户名
#     password="123",  # 密码
#     database="exam_system"  # 数据库名称
# )

# # 创建游标对象
# cursor = db.cursor()

# # 执行 SQL 查询
# cursor.execute("select * from question")
# desc = cursor.description
# alldata = [dict(zip([col[0] for col in desc], row)) for row in cursor.fetchall()]
# # print(alldata)


# # 修改 以ABCD的方式返回
# # for data in alldata:
# #     if data["options"] and "[" == data["options"][0] and "]" == data["options"][-1]:
# #         newoptions = data["options"]
# #         ops = newoptions[1:-1].split(", ")
# #         print(data['answer'])
# #         newanswer = data['answer']
# #         ans = data['answer'].split(",")
# #         newanswerlist = []
# #         for i, op in enumerate(ops):
# #             # print(op, end="")
# #
# #             for a in ans:
# #                 if op[1:-1] == a:
# #                     newanswerlist.append(chr(i+ord('A')))
# #                     break
# #         print(newanswerlist)
# #         # newstr = f'"A": {ops[0]}, "B": {ops[1]}, "C": {ops[2]}, "D": {ops[3]}'
# #         newoptionsstr = '{"A": %s, "B": %s, "C": %s, "D": %s}' % (ops[0], ops[1], ops[2], ops[3])
# #         newanswerstr = newanswerlist.__str__().replace("'", '"')
# #         print(newoptionsstr, newanswerstr)

#         # update_sql = f"update question set options = '{newoptionsstr}', answer = '{newanswerstr}' where id = {data['id']}"
#         #
#         # # 执行SQL语句
#         # cursor.execute(update_sql)
#         # # 提交到数据库执行
#         # db.commit()

# # 修改answer 列表长度为1的时候直接返回字符

# for data in alldata:
#     if data["type"] in ["multiple"]:
#         # if "," not in data["answer"] and '"' in data["answer"]:
#         if '"' in data["answer"]:
#             print(data["content"])
#             print(data["answer"])
#             new_answer = data["answer"].replace('"', '').replace('[', '').replace(']', '')
#             print(new_answer)
#             update_sql = f"update question set answer = '{new_answer}' where id = {data['id']}"
#             # print(update_sql)
#             # 执行SQL语句
#             cursor.execute(update_sql)
#             # 提交到数据库执行
#             db.commit()
# # 关闭连接
# db.close()


# # from datetime import datetime

# # s = "2000-12-30 10:20:02"
# # t = "%Y-%m-%d %H:%M:%S"

# # print(type(datetime.strptime(s, t)))



# # a = [1,2,5,3,6,7,8]
# # print(a)
# # a.sort()
# # print(a)



# # s = '["A","C"]'


# # print(s.replace("[", "").replace("]", "").replace('"', ""))


# import pandas as pd

# questions = [
#     {'id': 52, 
#      'type': 'single', 
#      'category': '数学', 
#      'content': '123', 
#      'options': {'A': '123', 'B': '123', 'C': '123', 'D': '123'}, 
#      'answer': 'A', 
#      'analysis': '123', 
#      'difficulty': 'medium', 
#      'score': 5
#      }, 
#     {'id': 57, 'type': 'single', 'category': '数学', 'content': '100+100等于多少？', 'options': {'A': 100.0, 'B': 200.0, 'C': 300.0, 'D': 400.0}, 'answer': 'B', 'analysis': '100+100=200', 'difficulty': 'easy', 'score': 5}, {'id': 59, 'type': 'judge', 'category': '常识', 'content': '地球是圆的', 'options': {'A': '正确', 'B': '错误'}, 'answer': 'true', 'analysis': '地球是圆的', 'difficulty': 'easy', 'score': 5}, {'id': 60, 'type': 'fill', 'category': '语文', 'content': '床前明月光，疑是____霜', 'options': None, 'answer': '地上', 'analysis': '李白《静夜思》', 'difficulty': 'easy', 'score': 5}]
# frame = {
#     "题目类型": [],  
#     "题目分类": [],
#     "题目内容": [],
#     "选项A": [],
#     "选项B": [],
#     "选项C": [],
#     "选项D": [],
#     "正确答案": [],
#     "题目解析": [],
#     "难度": [],
#     "分值": [],
# }

# for question in questions:
#     frame['题目类型'].append(question["type"])
#     frame['题目分类'].append(question["category"])
#     frame['题目内容'].append(question["content"])

#     if question.get("options") and question["type"] != 'judge':
#             frame['选项A'].append(question.get("options").get("A"))
#             frame['选项B'].append(question.get("options").get("B"))
#             frame['选项C'].append(question.get("options").get("C"))
#             frame['选项D'].append(question.get("options").get("D"))
            
#     else:
#         frame['选项A'].append(None)
#         frame['选项B'].append(None)
#         frame['选项C'].append(None)
#         frame['选项D'].append(None)
#     frame['正确答案'].append(question["answer"])
#     frame['题目解析'].append(question["analysis"])
#     frame['难度'].append(question["difficulty"])
#     frame['分值'].append(question["score"])
    
# print(frame)
# # 创建一个简单的 DataFrame
# df = pd.DataFrame(frame)

# # 将 DataFrame 写入 Excel 文件，写入 'Sheet1' 表单
# df.to_excel('output.xlsx', sheet_name='Sheet1', index=False)

# # # 写入多个表单，使用 ExcelWriter
# # with pd.ExcelWriter('output.xlsx') as writer:
# #     df.to_excel(writer, sheet_name='Sheet1', index=False)
# #     df.to_excel(writer, sheet_name='Sheet2', index=False)


#
# ## 同步错题本表
# # 创建数据库连接
# db = pymysql.connect(
#     host="localhost",  # 数据库主机地址
#     user="root",  # 用户名
#     password="123",  # 密码
#     database="exam_system"  # 数据库名称
# )
#
# # 创建游标对象
# cursor = db.cursor()
#
# # 执行 SQL 查询
# cursor.execute("""
# select user.id as user_id, ar.question_id, ar.exam_record_id, ar.update_time from user
# left join exam_record er on er.user_id = user.id
# left join answer_record ar on ar.exam_record_id = er.id
# where user.role = 'student' and ar.is_correct = 0
# """)
# desc = cursor.description
# alldata = [dict(zip([col[0] for col in desc], row)) for row in cursor.fetchall()]
# for a in alldata:
#     print(a)
#
# user_mistake_map = {}
# print(user_mistake_map)
#
# for data in alldata:
#     if not user_mistake_map.get(data["user_id"]):
#         user_mistake_map[data["user_id"]] = {
#             data["question_id"]: {
#                 "mistake_count": 1,
#                 "exam_record_id": data["exam_record_id"],
#                 "update_time": data["update_time"],
#             }
#         }
#     else:
#         if not user_mistake_map[data["user_id"]].get(data["question_id"]):
#             user_mistake_map[data["user_id"]][data["question_id"]] = {
#                 "mistake_count": 1,
#                 "exam_record_id": data["exam_record_id"],
#                 "update_time": data["update_time"],
#             }
#
#         else:
#             user_mistake_map[data["user_id"]][data["question_id"]]["mistake_count"] += 1
#             user_mistake_map[data["user_id"]][data["question_id"]]["update_time"] = max(data["update_time"], user_mistake_map[data["user_id"]][data["question_id"]]["update_time"])
#
#
# for user_id, v in user_mistake_map.items():
#     for questioin_id, vv in v.items():
#
#         print(f"user_id: {user_id}, question_id: {questioin_id}, mistake_count: {vv['mistake_count']}, exam_record_id:{vv['exam_record_id']}, update_time:{vv['update_time']}")
#
#         update_sql = f"""
#             insert into mistake (user_id, question_id, exam_record_id, mistake_count, last_mistake_time)
#             values('{user_id}', '{questioin_id}', '{vv['exam_record_id']}', '{vv['mistake_count']}', '{vv['update_time']}')
#             """
#
#         # 执行SQL语句
#         cursor.execute(update_sql)
#         # 提交到数据库执行
#         db.commit()


# print(user_mistake_map)




# for data in alldata:
#     user_mistake_map[data["user_id"]]["question"] =

# 修改 以ABCD的方式返回
# for data in alldata:
#     if data["options"] and "[" == data["options"][0] and "]" == data["options"][-1]:
#         newoptions = data["options"]
#         ops = newoptions[1:-1].split(", ")
#         print(data['answer'])
#         newanswer = data['answer']
#         ans = data['answer'].split(",")
#         newanswerlist = []
#         for i, op in enumerate(ops):
#             # print(op, end="")
#
#             for a in ans:
#                 if op[1:-1] == a:
#                     newanswerlist.append(chr(i+ord('A')))
#                     break
#         print(newanswerlist)
#         # newstr = f'"A": {ops[0]}, "B": {ops[1]}, "C": {ops[2]}, "D": {ops[3]}'
#         newoptionsstr = '{"A": %s, "B": %s, "C": %s, "D": %s}' % (ops[0], ops[1], ops[2], ops[3])
#         newanswerstr = newanswerlist.__str__().replace("'", '"')
#         print(newoptionsstr, newanswerstr)

        # update_sql = f"update question set options = '{newoptionsstr}', answer = '{newanswerstr}' where id = {data['id']}"
        #
        # # 执行SQL语句
        # cursor.execute(update_sql)
        # # 提交到数据库执行
        # db.commit()

# 修改answer 列表长度为1的时候直接返回字符

# for data in alldata:
#     if data["type"] in ["multiple"]:
#         # if "," not in data["answer"] and '"' in data["answer"]:
#         if '"' in data["answer"]:
#             print(data["content"])
#             print(data["answer"])
#             new_answer = data["answer"].replace('"', '').replace('[', '').replace(']', '')
#             print(new_answer)
#             update_sql = f"update question set answer = '{new_answer}' where id = {data['id']}"
#             # print(update_sql)
#             # 执行SQL语句
#             cursor.execute(update_sql)
#             # 提交到数据库执行
#             db.commit()
# # 关闭连接
# db.close()
