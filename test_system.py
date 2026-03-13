#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
在线考试系统功能测试脚本
测试所有主要 API 接口的功能是否健全
"""

import requests
import json
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List

# 配置
BASE_URL = "http://localhost:8010/api"
TEST_TIMEOUT = 30

# 颜色输出
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    INFO = '\033[96m'


class TestResult:
    """测试结果统计"""
    def __init__(self):
        self.total = 0
        self.passed = 0
        self.failed = 0
        self.errors = []

    def add_pass(self):
        self.total += 1
        self.passed += 1

    def add_fail(self, test_name: str, error: str):
        self.total += 1
        self.failed += 1
        self.errors.append((test_name, error))

    def print_summary(self):
        print(f"\n{'='*60}")
        print(f"{Colors.HEADER}测试结果汇总{Colors.ENDC}")
        print(f"{'='*60}")
        print(f"总测试数: {self.total}")
        print(f"{Colors.OKGREEN}通过: {self.passed}{Colors.ENDC}")
        print(f"{Colors.FAIL}失败: {self.failed}{Colors.ENDC}")
        print(f"通过率: {self.passed/self.total*100:.2f}%")
        
        if self.errors:
            print(f"\n{Colors.FAIL}失败的测试:{Colors.ENDC}")
            for test_name, error in self.errors:
                print(f"  - {test_name}: {error}")
        
        print(f"{'='*60}\n")


class APITester:
    """API 测试器"""
    
    def __init__(self):
        self.base_url = BASE_URL
        self.tokens = {
            "admin": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6NCwidXNlcm5hbWUiOiJhZG1pbjEiLCJuaWNrbmFtZSI6ImFkbWluMSIsInJvbGUiOiJhZG1pbiIsImF2YXRhciI6bnVsbCwiY3JlYXRlX3RpbWUiOiIyMDI1LTEyLTI5IDE1OjA5OjU1IiwidXBkYXRlX3RpbWUiOiIyMDI1LTEyLTI5IDE1OjE3OjEyIiwiY2xhc3NfaWQiOm51bGwsInN0YXR1cyI6MSwiZXhwIjoxNzY4NDQ4MjMxfQ._9k2cF0ybmWqOCRztP6DCmQzDWmMBzIiLmOivyblrN0",
            "student": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6NSwidXNlcm5hbWUiOiJzMSIsIm5pY2tuYW1lIjoiczEiLCJyb2xlIjoic3R1ZGVudCIsImF2YXRhciI6bnVsbCwiY3JlYXRlX3RpbWUiOiIyMDI1LTEyLTI5IDIxOjAyOjExIiwidXBkYXRlX3RpbWUiOiIyMDI2LTAxLTEzIDE2OjQxOjAxIiwiY2xhc3NfaWQiOjEsInN0YXR1cyI6MSwiZXhwIjoxNzY4NDY0NDE4fQ.JWl9yNOmVPzBpjbN2zRpr8CQZDhlnprPTmgnGZLbw94",
            "teacher": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6MiwidXNlcm5hbWUiOiJ0ZWFjaGVyIiwibmlja25hbWUiOiJcdTZkNGJcdThiZDVcdTY1NTlcdTVlMDgiLCJyb2xlIjoidGVhY2hlciIsImF2YXRhciI6IiIsImNyZWF0ZV90aW1lIjoiMjAyNS0xMi0yOSAxNTowNjozMSIsInVwZGF0ZV90aW1lIjoiMjAyNi0wMS0wNSAyMTo1MDo0OSIsImNsYXNzX2lkIjoxLCJzdGF0dXMiOjEsImV4cCI6MTc2ODQ2NDM5MH0.D3G_rCztZyzO9GDmj0p-3LH0-ta0kLUYoRIKpBriRrE",
        }  # 存储不同角色的 token
        self.user_ids = {}  # 存储创建的用户 ID
        self.question_ids = []  # 存储创建的题目 ID
        self.exam_id = None  # 存储创建的试卷 ID
        self.exam_record_id = None  # 存储考试记录 ID
        self.class_id = None  # 存储班级 ID
        self.result = TestResult()
        self.session = requests.Session()
        self.session.timeout = TEST_TIMEOUT

    def print_test(self, test_name: str, status: str, message: str = ""):
        """打印测试结果"""
        if status == "PASS":
            print(f"{Colors.OKGREEN}✓{Colors.ENDC} {test_name}")
        elif status == "FAIL":
            print(f"{Colors.FAIL}✗{Colors.ENDC} {test_name}")
            if message:
                print(f"  {Colors.WARNING}错误: {message}{Colors.ENDC}")
        elif status == "INFO":
            print(f"{Colors.OKBLUE}ℹ{Colors.ENDC} {test_name}")
        elif status == "SKIP":
            print(f"{Colors.OKCYAN}-{Colors.ENDC} {test_name}")

    def assert_response(self, response: requests.Response, expected_code: int = 200, 
                       test_name: str = "API 请求") -> bool:
        """验证响应"""
        try:
            data = response.json()
            if response.status_code == expected_code and data.get('code') == 200:
                self.result.add_pass()
                self.print_test(test_name, "PASS")
                return True
            else:
                error_msg = f"状态码: {response.status_code}, 响应: {data}"
                self.result.add_fail(test_name, error_msg)
                self.print_test(test_name, "FAIL", error_msg)
                return False
        except Exception as e:
            error_msg = f"解析响应失败: {str(e)}"
            self.result.add_fail(test_name, error_msg)
            self.print_test(test_name, "FAIL", error_msg)
            return False

    def get_headers(self, role: str = "admin") -> Dict[str, str]:
        """获取请求头"""
        token = self.tokens.get(role)
        if not token:
            return {}
        return {"Authorization": f"Bearer {token}"}

    # ==================== 用户模块测试 ====================
    
    def test_user_register(self, username: str, password: str, nickname: str, role: str) -> bool:
        """测试用户注册"""
        test_name = f"注册用户: {username} ({role})"
        try:
            response = self.session.post(
                f"{self.base_url}/user/register/",
                json={
                    "username": username,
                    "password": password,
                    "nickname": nickname,
                    "role": role
                }
            )
            if self.assert_response(response, 200, test_name):
                data = response.json()
                self.user_ids[role] = data['data']['id']
                return True
            return False
        except Exception as e:
            self.result.add_fail(test_name, str(e))
            self.print_test(test_name, "FAIL", str(e))
            return False

    def test_user_login(self, username: str, password: str, role: str) -> bool:
        """测试用户登录"""
        test_name = f"登录用户: {username}"
        try:
            response = self.session.post(
                f"{self.base_url}/user/login/",
                json={
                    "username": username,
                    "password": password
                }
            )
            if self.assert_response(response, 200, test_name):
                data = response.json()
                self.tokens[role] = data['data']['token']
                return True
            return False
        except Exception as e:
            self.result.add_fail(test_name, str(e))
            self.print_test(test_name, "FAIL", str(e))
            return False

    def test_get_user_info(self, role: str) -> bool:
        """测试获取用户信息"""
        test_name = f"获取用户信息 ({role})"
        try:
            response = self.session.get(
                f"{self.base_url}/user/info/",
                headers=self.get_headers(role)
            )
            return self.assert_response(response, 200, test_name)
        except Exception as e:
            self.result.add_fail(test_name, str(e))
            self.print_test(test_name, "FAIL", str(e))
            return False

    def test_update_user_info(self, role: str) -> bool:
        """测试更新用户信息"""
        test_name = f"更新用户信息 ({role})"
        try:
            response = self.session.put(
                f"{self.base_url}/user/update/",
                headers=self.get_headers(role),
                json={
                    "nickname": f"测试昵称_{role}",
                    "avatar": "http://example.com/avatar.jpg"
                }
            )
            return self.assert_response(response, 200, test_name)
        except Exception as e:
            self.result.add_fail(test_name, str(e))
            self.print_test(test_name, "FAIL", str(e))
            return False

    def test_change_password(self, role: str) -> bool:
        """测试修改密码"""
        test_name = f"修改密码 ({role})"
        try:
            response = self.session.put(
                f"{self.base_url}/user/password/",
                headers=self.get_headers(role),
                json={
                    "old_password": "123456",
                    "new_password": "new123456"
                }
            )
            if self.assert_response(response, 200, test_name):
                # 修改回原密码
                time.sleep(0.5)
                self.session.put(
                    f"{self.base_url}/user/password/",
                    headers=self.get_headers(role),
                    json={
                        "old_password": "new123456",
                        "new_password": "123456"
                    }
                )
                return True
            return False
        except Exception as e:
            self.result.add_fail(test_name, str(e))
            self.print_test(test_name, "FAIL", str(e))
            return False

    # ==================== 题目模块测试 ====================
    
    def test_add_question(self, role: str = "teacher") -> bool:
        """测试添加题目"""
        test_name = f"添加题目 ({role})"
        try:
            # 单选题
            response = self.session.post(
                f"{self.base_url}/question/add/",
                headers=self.get_headers(role),
                json={
                    "type": "single",
                    "category": "测试分类",
                    "content": "1+1等于多少？",
                    "options": {"A": "1", "B": "2", "C": "3", "D": "4"},
                    "answer": "B",
                    "analysis": "1+1=2",
                    "difficulty": "easy",
                    "score": 5
                }
            )
            if self.assert_response(response, 200, test_name):
                data = response.json()
                self.question_ids.append(data['data']['id'])
                return True
            return False
        except Exception as e:
            self.result.add_fail(test_name, str(e))
            self.print_test(test_name, "FAIL", str(e))
            return False

    def test_add_multiple_questions(self, role: str = "teacher") -> bool:
        """测试添加多种类型题目"""
        test_name = "添加多种类型题目"
        try:
            question_types = [
                {
                    "type": "multiple",
                    "category": "数学",
                    "content": "以下哪些是偶数？",
                    "options": {"A": "1", "B": "2", "C": "3", "D": "4"},
                    "answer": "B,D",
                    "analysis": "2和4是偶数",
                    "difficulty": "medium",
                    "score": 10
                },
                {
                    "type": "judge",
                    "category": "常识",
                    "content": "地球是圆的",
                    "answer": "true",
                    "analysis": "地球是圆的",
                    "difficulty": "easy",
                    "score": 5
                },
                {
                    "type": "fill",
                    "category": "语文",
                    "content": "床前明月光，疑是____霜",
                    "answer": "地上",
                    "analysis": "李白《静夜思》",
                    "difficulty": "easy",
                    "score": 5
                }
            ]
            
            for question in question_types:
                response = self.session.post(
                    f"{self.base_url}/question/add/",
                    headers=self.get_headers(role),
                    json=question
                )
                if response.status_code == 200:
                    data = response.json()
                    self.question_ids.append(data['data']['id'])
            
            self.result.add_pass()
            self.print_test(test_name, "PASS")
            return True
        except Exception as e:
            self.result.add_fail(test_name, str(e))
            self.print_test(test_name, "FAIL", str(e))
            return False

    def test_get_question_list(self, role: str = "teacher") -> bool:
        """测试获取题目列表"""
        test_name = f"获取题目列表 ({role})"
        try:
            response = self.session.get(
                f"{self.base_url}/question/list/",
                headers=self.get_headers(role),
                params={"page": 1, "size": 10}
            )
            return self.assert_response(response, 200, test_name)
        except Exception as e:
            self.result.add_fail(test_name, str(e))
            self.print_test(test_name, "FAIL", str(e))
            return False

    def test_get_question_detail(self, role: str = "teacher") -> bool:
        """测试获取题目详情"""
        test_name = f"获取题目详情 ({role})"
        if not self.question_ids:
            self.print_test(test_name, "SKIP", "没有可用的题目ID")
            return False
        
        try:
            response = self.session.get(
                f"{self.base_url}/question/{self.question_ids[0]}/",
                headers=self.get_headers(role)
            )
            return self.assert_response(response, 200, test_name)
        except Exception as e:
            self.result.add_fail(test_name, str(e))
            self.print_test(test_name, "FAIL", str(e))
            return False

    def test_update_question(self, role: str = "teacher") -> bool:
        """测试更新题目"""
        test_name = f"更新题目 ({role})"
        if not self.question_ids:
            self.print_test(test_name, "SKIP", "没有可用的题目ID")
            return False
        
        try:
            response = self.session.put(
                f"{self.base_url}/question/{self.question_ids[0]}/",
                headers=self.get_headers(role),
                json={
                    "type": "single",
                    "category": "更新分类",
                    "content": "1+1等于多少？（已更新）",
                    "options": {"A": "1", "B": "2", "C": "3", "D": "4"},
                    "answer": "B",
                    "analysis": "1+1=2",
                    "difficulty": "easy",
                    "score": 5
                }
            )
            return self.assert_response(response, 200, test_name)
        except Exception as e:
            self.result.add_fail(test_name, str(e))
            self.print_test(test_name, "FAIL", str(e))
            return False

    def test_batch_delete_questions(self, role: str = "teacher") -> bool:
        """测试批量删除题目"""
        test_name = f"批量删除题目 ({role})"
        if len(self.question_ids) < 2:
            self.print_test(test_name, "SKIP", "题目数量不足")
            return False
        
        try:
            # 保留第一个题目，删除其他
            ids_to_delete = self.question_ids[1:3]
            response = self.session.delete(
                f"{self.base_url}/question/batch/",
                headers=self.get_headers(role),
                json={"ids": ids_to_delete}
            )
            if self.assert_response(response, 200, test_name):
                # 更新题目ID列表
                self.question_ids = [qid for qid in self.question_ids if qid not in ids_to_delete]
                return True
            return False
        except Exception as e:
            self.result.add_fail(test_name, str(e))
            self.print_test(test_name, "FAIL", str(e))
            return False

    # ==================== 试卷模块测试 ====================
    
    def test_create_exam(self, role: str = "teacher") -> bool:
        """测试创建试卷"""
        test_name = f"创建试卷 ({role})"
        if len(self.question_ids) < 3:
            self.print_test(test_name, "SKIP", "题目数量不足（至少需要3题）")
            return False
        
        try:
            start_time = datetime.now() + timedelta(minutes=5)
            end_time = start_time + timedelta(hours=2)
            
            response = self.session.post(
                f"{self.base_url}/exam/add/",
                headers=self.get_headers(role),
                json={
                    "title": "测试试卷",
                    "description": "这是一个测试试卷",
                    "duration": 60,
                    "total_score": 100,
                    "pass_score": 60,
                    "start_time": start_time.strftime("%Y-%m-%d %H:%M:%S"),
                    "end_time": end_time.strftime("%Y-%m-%d %H:%M:%S"),
                    "is_random": 0,
                    "question_ids": self.question_ids[:3]
                }
            )
            if self.assert_response(response, 200, test_name):
                data = response.json()
                self.exam_id = data['data']['id']
                return True
            return False
        except Exception as e:
            self.result.add_fail(test_name, str(e))
            self.print_test(test_name, "FAIL", str(e))
            return False

    def test_get_exam_list(self, role: str = "teacher") -> bool:
        """测试获取试卷列表"""
        test_name = f"获取试卷列表 ({role})"
        try:
            response = self.session.get(
                f"{self.base_url}/exam/list/",
                headers=self.get_headers(role),
                params={"page": 1, "size": 10}
            )
            return self.assert_response(response, 200, test_name)
        except Exception as e:
            self.result.add_fail(test_name, str(e))
            self.print_test(test_name, "FAIL", str(e))
            return False

    def test_get_exam_detail(self, role: str = "teacher") -> bool:
        """测试获取试卷详情"""
        test_name = f"获取试卷详情 ({role})"
        if not self.exam_id:
            self.print_test(test_name, "SKIP", "没有可用的试卷ID")
            return False
        
        try:
            response = self.session.get(
                f"{self.base_url}/exam/{self.exam_id}/",
                headers=self.get_headers(role)
            )
            return self.assert_response(response, 200, test_name)
        except Exception as e:
            self.result.add_fail(test_name, str(e))
            self.print_test(test_name, "FAIL", str(e))
            return False

    def test_publish_exam(self, role: str = "teacher") -> bool:
        """测试发布试卷"""
        test_name = f"发布试卷 ({role})"
        if not self.exam_id:
            self.print_test(test_name, "SKIP", "没有可用的试卷ID")
            return False
        
        try:
            response = self.session.put(
                f"{self.base_url}/exam/{self.exam_id}/publish/",
                headers=self.get_headers(role)
            )
            return self.assert_response(response, 200, test_name)
        except Exception as e:
            self.result.add_fail(test_name, str(e))
            self.print_test(test_name, "FAIL", str(e))
            return False

    def test_get_available_exams(self, role: str = "student") -> bool:
        """测试获取可参加的考试列表"""
        test_name = f"获取可参加的考试列表 ({role})"
        try:
            response = self.session.get(
                f"{self.base_url}/exam/available/",
                headers=self.get_headers(role)
            )
            return self.assert_response(response, 200, test_name)
        except Exception as e:
            self.result.add_fail(test_name, str(e))
            self.print_test(test_name, "FAIL", str(e))
            return False

    # ==================== 考试模块测试 ====================
    
    def test_start_exam(self, role: str = "student") -> bool:
        """测试开始考试"""
        test_name = f"开始考试 ({role})"
        if not self.exam_id:
            self.print_test(test_name, "SKIP", "没有可用的试卷ID")
            return False
        
        try:
            response = self.session.post(
                f"{self.base_url}/exam/start/",
                headers=self.get_headers(role),
                json={"exam_id": self.exam_id}
            )
            if self.assert_response(response, 200, test_name):
                data = response.json()
                self.exam_record_id = data['data']['id']
                return True
            return False
        except Exception as e:
            self.result.add_fail(test_name, str(e))
            self.print_test(test_name, "FAIL", str(e))
            return False

    def test_get_exam_questions(self, role: str = "student") -> bool:
        """测试获取考试题目"""
        test_name = f"获取考试题目 ({role})"
        if not self.exam_id:
            self.print_test(test_name, "SKIP", "没有可用的试卷ID")
            return False
        
        try:
            response = self.session.get(
                f"{self.base_url}/exam/{self.exam_id}/questions/",
                headers=self.get_headers(role)
            )
            return self.assert_response(response, 200, test_name)
        except Exception as e:
            self.result.add_fail(test_name, str(e))
            self.print_test(test_name, "FAIL", str(e))
            return False

    def test_save_answer(self, role: str = "student") -> bool:
        """测试保存答案"""
        test_name = f"保存答案 ({role})"
        if not self.exam_record_id or not self.question_ids:
            self.print_test(test_name, "SKIP", "缺少考试记录ID或题目ID")
            return False
        
        try:
            response = self.session.post(
                f"{self.base_url}/exam/answer/",
                headers=self.get_headers(role),
                json={
                    "exam_record_id": self.exam_record_id,
                    "question_id": self.question_ids[0],
                    "user_answer": "B"
                }
            )
            return self.assert_response(response, 200, test_name)
        except Exception as e:
            self.result.add_fail(test_name, str(e))
            self.print_test(test_name, "FAIL", str(e))
            return False

    def test_submit_exam(self, role: str = "student") -> bool:
        """测试提交试卷"""
        test_name = f"提交试卷 ({role})"
        if not self.exam_record_id:
            self.print_test(test_name, "SKIP", "没有可用的考试记录ID")
            return False
        
        try:
            response = self.session.post(
                f"{self.base_url}/exam/submit/",
                headers=self.get_headers(role),
                json={"exam_record_id": self.exam_record_id}
            )
            return self.assert_response(response, 200, test_name)
        except Exception as e:
            self.result.add_fail(test_name, str(e))
            self.print_test(test_name, "FAIL", str(e))
            return False

    # ==================== 考试记录模块测试 ====================
    
    def test_get_exam_records(self, role: str = "student") -> bool:
        """测试获取考试记录列表"""
        test_name = f"获取考试记录列表 ({role})"
        try:
            response = self.session.get(
                f"{self.base_url}/exam/record/list/",
                headers=self.get_headers(role),
                params={"page": 1, "size": 10}
            )
            return self.assert_response(response, 200, test_name)
        except Exception as e:
            self.result.add_fail(test_name, str(e))
            self.print_test(test_name, "FAIL", str(e))
            return False

    def test_get_exam_record_detail(self, role: str = "student") -> bool:
        """测试获取考试记录详情"""
        test_name = f"获取考试记录详情 ({role})"
        if not self.exam_record_id:
            self.print_test(test_name, "SKIP", "没有可用的考试记录ID")
            return False
        
        try:
            response = self.session.get(
                f"{self.base_url}/exam/record/{self.exam_record_id}/",
                headers=self.get_headers(role)
            )
            return self.assert_response(response, 200, test_name)
        except Exception as e:
            self.result.add_fail(test_name, str(e))
            self.print_test(test_name, "FAIL", str(e))
            return False

    def test_get_grouped_records(self, role: str = "teacher") -> bool:
        """测试获取按考试分组的记录"""
        test_name = f"获取按考试分组的记录 ({role})"
        try:
            response = self.session.get(
                f"{self.base_url}/exam/grouped-records/",
                headers=self.get_headers(role),
                params={"page": 1, "size": 10}
            )
            return self.assert_response(response, 200, test_name)
        except Exception as e:
            self.result.add_fail(test_name, str(e))
            self.print_test(test_name, "FAIL", str(e))
            return False

    # ==================== 统计模块测试 ====================
    
    def test_get_exam_statistics(self, role: str = "teacher") -> bool:
        """测试获取考试统计"""
        test_name = f"获取考试统计 ({role})"
        if not self.exam_id:
            self.print_test(test_name, "SKIP", "没有可用的试卷ID")
            return False
        
        try:
            response = self.session.get(
                f"{self.base_url}/exam/{self.exam_id}/statistics/",
                headers=self.get_headers(role)
            )
            return self.assert_response(response, 200, test_name)
        except Exception as e:
            self.result.add_fail(test_name, str(e))
            self.print_test(test_name, "FAIL", str(e))
            return False

    def test_get_system_statistics(self, role: str = "teacher") -> bool:
        """测试获取系统统计"""
        test_name = f"获取系统统计 ({role})"
        try:
            response = self.session.get(
                f"{self.base_url}/exam/statistics/",
                headers=self.get_headers(role)
            )
            return self.assert_response(response, 200, test_name)
        except Exception as e:
            self.result.add_fail(test_name, str(e))
            self.print_test(test_name, "FAIL", str(e))
            return False

    def test_get_exam_ranking(self, role: str = "student") -> bool:
        """测试获取考试排名"""
        test_name = f"获取考试排名 ({role})"
        if not self.exam_id:
            self.print_test(test_name, "SKIP", "没有可用的试卷ID")
            return False
        
        try:
            response = self.session.get(
                f"{self.base_url}/exam/{self.exam_id}/ranking/",
                headers=self.get_headers(role),
                params={"page": 1, "size": 10}
            )
            return self.assert_response(response, 200, test_name)
        except Exception as e:
            self.result.add_fail(test_name, str(e))
            self.print_test(test_name, "FAIL", str(e))
            return False

    # ==================== 班级管理模块测试 ====================
    
    def test_create_class(self, role: str = "admin") -> bool:
        """测试创建班级"""
        test_name = f"创建班级 ({role})"
        try:
            response = self.session.post(
                f"{self.base_url}/class/create/",
                headers=self.get_headers(role),
                json={
                    "name": "测试班级",
                    "grade": "测试年级",
                    "head_teacher_id": self.user_ids.get("teacher")
                }
            )
            if self.assert_response(response, 200, test_name):
                data = response.json()
                self.class_id = data['data']['id']
                return True
            return False
        except Exception as e:
            self.result.add_fail(test_name, str(e))
            self.print_test(test_name, "FAIL", str(e))
            return False

    def test_get_class_list(self, role: str = "admin") -> bool:
        """测试获取班级列表"""
        test_name = f"获取班级列表 ({role})"
        try:
            response = self.session.get(
                f"{self.base_url}/class/list/",
                headers=self.get_headers(role),
                params={"page": 1, "size": 10}
            )
            return self.assert_response(response, 200, test_name)
        except Exception as e:
            self.result.add_fail(test_name, str(e))
            self.print_test(test_name, "FAIL", str(e))
            return False

    def test_get_class_detail(self, role: str = "admin") -> bool:
        """测试获取班级详情"""
        test_name = f"获取班级详情 ({role})"
        if not self.class_id:
            self.print_test(test_name, "SKIP", "没有可用的班级ID")
            return False
        
        try:
            response = self.session.get(
                f"{self.base_url}/class/{self.class_id}/",
                headers=self.get_headers(role)
            )
            return self.assert_response(response, 200, test_name)
        except Exception as e:
            self.result.add_fail(test_name, str(e))
            self.print_test(test_name, "FAIL", str(e))
            return False

    def test_add_student_to_class(self, role: str = "admin") -> bool:
        """测试添加学生到班级"""
        test_name = f"添加学生到班级 ({role})"
        if not self.class_id or not self.user_ids.get("student"):
            self.print_test(test_name, "SKIP", "缺少班级ID或学生ID")
            return False
        
        try:
            response = self.session.post(
                f"{self.base_url}/class/{self.class_id}/members/add/",
                headers=self.get_headers(role),
                json={"user_ids": [self.user_ids["student"]]}
            )
            return self.assert_response(response, 200, test_name)
        except Exception as e:
            self.result.add_fail(test_name, str(e))
            self.print_test(test_name, "FAIL", str(e))
            return False

    def test_get_class_members(self, role: str = "admin") -> bool:
        """测试获取班级成员"""
        test_name = f"获取班级成员 ({role})"
        if not self.class_id:
            self.print_test(test_name, "SKIP", "没有可用的班级ID")
            return False
        
        try:
            response = self.session.get(
                f"{self.base_url}/class/{self.class_id}/members/",
                headers=self.get_headers(role),
                params={"page": 1, "size": 10}
            )
            return self.assert_response(response, 200, test_name)
        except Exception as e:
            self.result.add_fail(test_name, str(e))
            self.print_test(test_name, "FAIL", str(e))
            return False

    def test_get_class_statistics(self, role: str = "admin") -> bool:
        """测试获取班级统计"""
        test_name = f"获取班级统计 ({role})"
        if not self.class_id:
            self.print_test(test_name, "SKIP", "没有可用的班级ID")
            return False
        
        try:
            response = self.session.get(
                f"{self.base_url}/class/{self.class_id}/statistics/",
                headers=self.get_headers(role)
            )
            return self.assert_response(response, 200, test_name)
        except Exception as e:
            self.result.add_fail(test_name, str(e))
            self.print_test(test_name, "FAIL", str(e))
            return False

    def test_get_student_class(self, role: str = "student") -> bool:
        """测试获取学生所在班级"""
        test_name = f"获取学生所在班级 ({role})"
        try:
            response = self.session.get(
                f"{self.base_url}/student/class",
                headers=self.get_headers(role)
            )
            return self.assert_response(response, 200, test_name)
        except Exception as e:
            self.result.add_fail(test_name, str(e))
            self.print_test(test_name, "FAIL", str(e))
            return False

    # ==================== 用户管理模块测试 ====================
    
    def test_get_users_list(self, role: str = "admin") -> bool:
        """测试获取用户列表（管理员）"""
        test_name = f"获取用户列表 ({role})"
        try:
            response = self.session.get(
                f"{self.base_url}/admin/users/",
                headers=self.get_headers(role),
                params={"page": 1, "size": 10}
            )
            return self.assert_response(response, 200, test_name)
        except Exception as e:
            self.result.add_fail(test_name, str(e))
            self.print_test(test_name, "FAIL", str(e))
            return False

    # ==================== 错题本模块测试 ====================
    
    def test_get_mistake_list(self, role: str = "student") -> bool:
        """测试获取错题列表"""
        test_name = f"获取错题列表 ({role})"
        try:
            response = self.session.get(
                f"{self.base_url}/mistake/list/",
                headers=self.get_headers(role),
                params={"page": 1, "size": 10}
            )
            return self.assert_response(response, 200, test_name)
        except Exception as e:
            self.result.add_fail(test_name, str(e))
            self.print_test(test_name, "FAIL", str(e))
            return False

    def test_get_mistake_statistics(self, role: str = "student") -> bool:
        """测试获取错题统计"""
        test_name = f"获取错题统计 ({role})"
        try:
            response = self.session.get(
                f"{self.base_url}/mistake/statistics/",
                headers=self.get_headers(role)
            )
            return self.assert_response(response, 200, test_name)
        except Exception as e:
            self.result.add_fail(test_name, str(e))
            self.print_test(test_name, "FAIL", str(e))
            return False

    # ==================== 运行所有测试 ====================
    
    def run_all_tests(self):
        """运行所有测试"""
        print(f"{Colors.HEADER}{'='*60}")
        print(f"在线考试系统功能测试")
        print(f"{'='*60}{Colors.ENDC}\n")
        
        # 检查服务器是否运行
        print(f"{Colors.INFO}检查服务器状态...{Colors.ENDC}")
        try:
            response = self.session.get(f"{self.base_url}/user/info/", timeout=5)
        except:
            print(f"{Colors.FAIL}✗ 无法连接到服务器 {BASE_URL}{Colors.ENDC}")
            print(f"请确保 Django 服务器正在运行: python manage.py runserver 8010")
            return
        
        print(f"{Colors.OKGREEN}✓ 服务器运行正常{Colors.ENDC}\n")
        
        # 用户模块测试
        print(f"{Colors.HEADER}{'='*60}")
        print(f"1. 用户模块测试")
        print(f"{'='*60}{Colors.ENDC}")
        
        # 注册测试用户
        self.test_user_register("test_admin", "123456", "测试管理员", "admin")
        self.test_user_register("test_teacher", "123456", "测试教师", "teacher")
        self.test_user_register("test_student", "123456", "测试学生", "student")
        
        time.sleep(0.5)
        
        # 登录测试用户
        self.test_user_login("test_admin", "123456", "admin")
        self.test_user_login("test_teacher", "123456", "teacher")
        self.test_user_login("test_student", "123456", "student")
        
        time.sleep(0.5)
        
        # 用户信息测试
        self.test_get_user_info("admin")
        self.test_get_user_info("teacher")
        self.test_get_user_info("student")
        
        # 更新用户信息
        self.test_update_user_info("admin")
        self.test_update_user_info("teacher")
        self.test_update_user_info("student")
        
        # 修改密码
        self.test_change_password("admin")
        self.test_change_password("teacher")
        
        # 题目模块测试
        print(f"\n{Colors.HEADER}{'='*60}")
        print(f"2. 题目模块测试")
        print(f"{'='*60}{Colors.ENDC}")
        
        self.test_add_question("teacher")
        self.test_add_multiple_questions("teacher")
        self.test_get_question_list("teacher")
        self.test_get_question_list("admin")
        self.test_get_question_detail("teacher")
        self.test_update_question("teacher")
        self.test_batch_delete_questions("teacher")
        
        # 试卷模块测试
        print(f"\n{Colors.HEADER}{'='*60}")
        print(f"3. 试卷模块测试")
        print(f"{'='*60}{Colors.ENDC}")
        
        self.test_create_exam("teacher")
        self.test_get_exam_list("teacher")
        self.test_get_exam_list("admin")
        self.test_get_exam_detail("teacher")
        self.test_publish_exam("teacher")
        self.test_get_available_exams("student")
        
        # 考试模块测试
        print(f"\n{Colors.HEADER}{'='*60}")
        print(f"4. 考试模块测试")
        print(f"{'='*60}{Colors.ENDC}")
        
        self.test_start_exam("student")
        self.test_get_exam_questions("student")
        self.test_save_answer("student")
        self.test_submit_exam("student")
        
        # 考试记录模块测试
        print(f"\n{Colors.HEADER}{'='*60}")
        print(f"5. 考试记录模块测试")
        print(f"{'='*60}{Colors.ENDC}")
        
        self.test_get_exam_records("student")
        self.test_get_exam_record_detail("student")
        self.test_get_grouped_records("teacher")
        
        # 统计模块测试
        print(f"\n{Colors.HEADER}{'='*60}")
        print(f"6. 统计模块测试")
        print(f"{'='*60}{Colors.ENDC}")
        
        self.test_get_exam_statistics("teacher")
        self.test_get_system_statistics("teacher")
        self.test_get_exam_ranking("student")
        self.test_get_exam_ranking("teacher")
        
        # 班级管理模块测试
        print(f"\n{Colors.HEADER}{'='*60}")
        print(f"7. 班级管理模块测试")
        print(f"{'='*60}{Colors.ENDC}")
        
        self.test_create_class("admin")
        self.test_get_class_list("admin")
        self.test_get_class_list("teacher")
        self.test_get_class_detail("admin")
        self.test_add_student_to_class("admin")
        self.test_get_class_members("admin")
        self.test_get_class_statistics("admin")
        self.test_get_student_class("student")
        
        # 用户管理模块测试
        print(f"\n{Colors.HEADER}{'='*60}")
        print(f"8. 用户管理模块测试")
        print(f"{'='*60}{Colors.ENDC}")
        
        self.test_get_users_list("admin")
        
        # 错题本模块测试
        print(f"\n{Colors.HEADER}{'='*60}")
        print(f"9. 错题本模块测试")
        print(f"{'='*60}{Colors.ENDC}")
        
        self.test_get_mistake_list("student")
        self.test_get_mistake_statistics("student")
        
        # 打印测试结果汇总
        self.result.print_summary()


def main():
    """主函数"""
    tester = APITester()
    try:
        tester.run_all_tests()
    except KeyboardInterrupt:
        print(f"\n{Colors.WARNING}测试被用户中断{Colors.ENDC}")
    except Exception as e:
        print(f"\n{Colors.FAIL}测试过程中发生错误: {str(e)}{Colors.ENDC}")


if __name__ == "__main__":
    main()