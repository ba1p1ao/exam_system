#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
在线考试系统快速测试脚本
快速验证核心功能是否正常
"""

import requests
import json
from datetime import datetime, timedelta

# 配置
BASE_URL = "http://localhost:8010/api"

class QuickTester:
    """快速测试器"""
    
    def __init__(self):
        self.base_url = BASE_URL
        self.admin_token = None
        self.teacher_token = None
        self.student_token = None
        self.test_user_ids = {}
        self.question_id = None
        self.exam_id = None
        self.exam_record_id = None
        self.class_id = None
        
    def print_status(self, test_name, success, message=""):
        """打印测试状态"""
        if success:
            print(f"✓ {test_name}")
        else:
            print(f"✗ {test_name}")
            if message:
                print(f"  错误: {message}")
    
    def check_response(self, response, expected_code=200):
        """检查响应"""
        try:
            if response.status_code == expected_code:
                data = response.json()
                return data.get('code') == 200
        except:
            pass
        return False
    
    # 1. 用户注册和登录测试
    def test_user_auth(self):
        """测试用户认证"""
        print("\n=== 用户认证测试 ===")
        
        # 注册管理员
        response = requests.post(f"{self.base_url}/user/register/", json={
            "username": "quick_test_admin",
            "password": "123456",
            "nickname": "快速测试管理员",
            "role": "admin"
        })
        success = self.check_response(response)
        self.print_status("注册管理员", success)
        if success:
            self.test_user_ids['admin'] = response.json()['data']['id']
        
        # 注册教师
        response = requests.post(f"{self.base_url}/user/register/", json={
            "username": "quick_test_teacher",
            "password": "123456",
            "nickname": "快速测试教师",
            "role": "teacher"
        })
        success = self.check_response(response)
        self.print_status("注册教师", success)
        if success:
            self.test_user_ids['teacher'] = response.json()['data']['id']
        
        # 注册学生
        response = requests.post(f"{self.base_url}/user/register/", json={
            "username": "quick_test_student",
            "password": "123456",
            "nickname": "快速测试学生",
            "role": "student"
        })
        success = self.check_response(response)
        self.print_status("注册学生", success)
        if success:
            self.test_user_ids['student'] = response.json()['data']['id']
        
        # 登录
        response = requests.post(f"{self.base_url}/user/login/", json={
            "username": "quick_test_admin",
            "password": "123456"
        })
        success = self.check_response(response)
        self.print_status("管理员登录", success)
        if success:
            self.admin_token = response.json()['data']['token']
        
        response = requests.post(f"{self.base_url}/user/login/", json={
            "username": "quick_test_teacher",
            "password": "123456"
        })
        success = self.check_response(response)
        self.print_status("教师登录", success)
        if success:
            self.teacher_token = response.json()['data']['token']
        
        response = requests.post(f"{self.base_url}/user/login/", json={
            "username": "quick_test_student",
            "password": "123456"
        })
        success = self.check_response(response)
        self.print_status("学生登录", success)
        if success:
            self.student_token = response.json()['data']['token']
        
        # 获取用户信息
        if self.admin_token:
            response = requests.get(f"{self.base_url}/user/info/", 
                                   headers={"Authorization": f"Bearer {self.admin_token}"})
            self.print_status("获取管理员信息", self.check_response(response))
        
        if self.teacher_token:
            response = requests.get(f"{self.base_url}/user/info/", 
                                   headers={"Authorization": f"Bearer {self.teacher_token}"})
            self.print_status("获取教师信息", self.check_response(response))
        
        if self.student_token:
            response = requests.get(f"{self.base_url}/user/info/", 
                                   headers={"Authorization": f"Bearer {self.student_token}"})
            self.print_status("获取学生信息", self.check_response(response))
    
    # 2. 题目管理测试
    def test_question_management(self):
        """测试题目管理"""
        print("\n=== 题目管理测试 ===")
        
        if not self.teacher_token:
            print("✗ 跳过题目管理测试（未登录教师）")
            return
        
        # 添加题目
        response = requests.post(f"{self.base_url}/question/add/", 
                                headers={"Authorization": f"Bearer {self.teacher_token}"},
                                json={
                                    "type": "single",
                                    "category": "测试分类",
                                    "content": "1+1等于多少？",
                                    "options": {"A": "1", "B": "2", "C": "3", "D": "4"},
                                    "answer": "B",
                                    "analysis": "1+1=2",
                                    "difficulty": "easy",
                                    "score": 5
                                })
        success = self.check_response(response)
        self.print_status("添加题目", success)
        if success:
            self.question_id = response.json()['data']['id']
        
        # 获取题目列表
        response = requests.get(f"{self.base_url}/question/list/", 
                               headers={"Authorization": f"Bearer {self.teacher_token}"})
        self.print_status("获取题目列表", self.check_response(response))
        
        # 获取题目详情
        if self.question_id:
            response = requests.get(f"{self.base_url}/question/{self.question_id}/", 
                                   headers={"Authorization": f"Bearer {self.teacher_token}"})
            self.print_status("获取题目详情", self.check_response(response))
            
            # 更新题目
            response = requests.put(f"{self.base_url}/question/{self.question_id}/", 
                                   headers={"Authorization": f"Bearer {self.teacher_token}"},
                                   json={
                                       "type": "single",
                                       "category": "测试分类",
                                       "content": "1+1等于多少？（已更新）",
                                       "options": {"A": "1", "B": "2", "C": "3", "D": "4"},
                                       "answer": "B",
                                       "analysis": "1+1=2",
                                       "difficulty": "easy",
                                       "score": 5
                                   })
            self.print_status("更新题目", self.check_response(response))
    
    # 3. 试卷管理测试
    def test_exam_management(self):
        """测试试卷管理"""
        print("\n=== 试卷管理测试 ===")
        
        if not self.teacher_token or not self.question_id:
            print("✗ 跳过试卷管理测试（缺少必要条件）")
            return
        
        # 添加更多题目用于创建试卷
        for i in range(2, 5):
            response = requests.post(f"{self.base_url}/question/add/", 
                                    headers={"Authorization": f"Bearer {self.teacher_token}"},
                                    json={
                                        "type": "single",
                                        "category": "测试分类",
                                        "content": f"测试题目 {i}",
                                        "options": {"A": "选项A", "B": "选项B", "C": "选项C", "D": "选项D"},
                                        "answer": "A",
                                        "analysis": f"解析 {i}",
                                        "difficulty": "easy",
                                        "score": 5
                                    })
            if self.check_response(response):
                pass  # 题目已添加
        
        # 获取题目列表以获取题目ID
        response = requests.get(f"{self.base_url}/question/list/", 
                               headers={"Authorization": f"Bearer {self.teacher_token}"})
        question_ids = []
        if self.check_response(response):
            questions = response.json()['data']['list']
            question_ids = [q['id'] for q in questions[:5]]
        
        # 创建试卷
        start_time = datetime.now() + timedelta(minutes=5)
        end_time = start_time + timedelta(hours=2)
        
        response = requests.post(f"{self.base_url}/exam/add/", 
                                headers={"Authorization": f"Bearer {self.teacher_token}"},
                                json={
                                    "title": "快速测试试卷",
                                    "description": "这是一个快速测试试卷",
                                    "duration": 60,
                                    "total_score": 100,
                                    "pass_score": 60,
                                    "start_time": start_time.strftime("%Y-%m-%d %H:%M:%S"),
                                    "end_time": end_time.strftime("%Y-%m-%d %H:%M:%S"),
                                    "is_random": 0,
                                    "question_ids": question_ids
                                })
        success = self.check_response(response)
        self.print_status("创建试卷", success)
        if success:
            self.exam_id = response.json()['data']['id']
        
        # 获取试卷列表
        response = requests.get(f"{self.base_url}/exam/list/", 
                               headers={"Authorization": f"Bearer {self.teacher_token}"})
        self.print_status("获取试卷列表", self.check_response(response))
        
        # 获取试卷详情
        if self.exam_id:
            response = requests.get(f"{self.base_url}/exam/{self.exam_id}/", 
                                   headers={"Authorization": f"Bearer {self.teacher_token}"})
            self.print_status("获取试卷详情", self.check_response(response))
            
            # 发布试卷
            response = requests.put(f"{self.base_url}/exam/{self.exam_id}/publish/", 
                                   headers={"Authorization": f"Bearer {self.teacher_token}"})
            self.print_status("发布试卷", self.check_response(response))
        
        # 学生获取可参加的考试
        if self.student_token:
            response = requests.get(f"{self.base_url}/exam/available/", 
                                   headers={"Authorization": f"Bearer {self.student_token}"})
            self.print_status("学生获取可参加的考试", self.check_response(response))
    
    # 4. 考试功能测试
    def test_exam_functionality(self):
        """测试考试功能"""
        print("\n=== 考试功能测试 ===")
        
        if not self.student_token or not self.exam_id:
            print("✗ 跳过考试功能测试（缺少必要条件）")
            return
        
        # 开始考试
        response = requests.post(f"{self.base_url}/exam/start/", 
                                headers={"Authorization": f"Bearer {self.student_token}"},
                                json={"exam_id": self.exam_id})
        success = self.check_response(response)
        self.print_status("开始考试", success)
        if success:
            self.exam_record_id = response.json()['data']['id']
        
        # 获取考试题目
        response = requests.get(f"{self.base_url}/exam/{self.exam_id}/questions/", 
                               headers={"Authorization": f"Bearer {self.student_token}"})
        self.print_status("获取考试题目", self.check_response(response))
        
        # 保存答案
        if self.exam_record_id:
            response = requests.post(f"{self.base_url}/exam/answer/", 
                                    headers={"Authorization": f"Bearer {self.student_token}"},
                                    json={
                                        "exam_record_id": self.exam_record_id,
                                        "question_id": self.question_id if self.question_id else 1,
                                        "user_answer": "B"
                                    })
            self.print_status("保存答案", self.check_response(response))
            
            # 提交试卷
            response = requests.post(f"{self.base_url}/exam/submit/", 
                                    headers={"Authorization": f"Bearer {self.student_token}"},
                                    json={"exam_record_id": self.exam_record_id})
            self.print_status("提交试卷", self.check_response(response))
    
    # 5. 考试记录测试
    def test_exam_records(self):
        """测试考试记录"""
        print("\n=== 考试记录测试 ===")
        
        # 学生获取考试记录
        if self.student_token:
            response = requests.get(f"{self.base_url}/exam/record/list/", 
                                   headers={"Authorization": f"Bearer {self.student_token}"})
            self.print_status("学生获取考试记录", self.check_response(response))
        
        # 教师获取分组记录
        if self.teacher_token:
            response = requests.get(f"{self.base_url}/exam/grouped-records/", 
                                   headers={"Authorization": f"Bearer {self.teacher_token}"})
            self.print_status("教师获取分组记录", self.check_response(response))
    
    # 6. 统计功能测试
    def test_statistics(self):
        """测试统计功能"""
        print("\n=== 统计功能测试 ===")
        
        # 获取系统统计
        if self.teacher_token:
            response = requests.get(f"{self.base_url}/exam/statistics/", 
                                   headers={"Authorization": f"Bearer {self.teacher_token}"})
            self.print_status("获取系统统计", self.check_response(response))
        
        # 获取考试统计
        if self.teacher_token and self.exam_id:
            response = requests.get(f"{self.base_url}/exam/{self.exam_id}/statistics/", 
                                   headers={"Authorization": f"Bearer {self.teacher_token}"})
            self.print_status("获取考试统计", self.check_response(response))
        
        # 获取考试排名
        if self.student_token and self.exam_id:
            response = requests.get(f"{self.base_url}/exam/{self.exam_id}/ranking/", 
                                   headers={"Authorization": f"Bearer {self.student_token}"})
            self.print_status("获取考试排名", self.check_response(response))
    
    # 7. 班级管理测试
    def test_class_management(self):
        """测试班级管理"""
        print("\n=== 班级管理测试 ===")
        
        if not self.admin_token:
            print("✗ 跳过班级管理测试（未登录管理员）")
            return
        
        # 创建班级
        response = requests.post(f"{self.base_url}/class/create/", 
                                headers={"Authorization": f"Bearer {self.admin_token}"},
                                json={
                                    "name": "快速测试班级",
                                    "grade": "测试年级",
                                    "head_teacher_id": self.test_user_ids.get('teacher')
                                })
        success = self.check_response(response)
        self.print_status("创建班级", success)
        if success:
            self.class_id = response.json()['data']['id']
        
        # 获取班级列表
        response = requests.get(f"{self.base_url}/class/list/", 
                               headers={"Authorization": f"Bearer {self.admin_token}"})
        self.print_status("获取班级列表", self.check_response(response))
        
        # 添加学生到班级
        if self.class_id and self.test_user_ids.get('student'):
            response = requests.post(f"{self.base_url}/class/{self.class_id}/members/add/", 
                                    headers={"Authorization": f"Bearer {self.admin_token}"},
                                    json={"user_ids": [self.test_user_ids['student']]})
            self.print_status("添加学生到班级", self.check_response(response))
            
            # 获取班级成员
            response = requests.get(f"{self.base_url}/class/{self.class_id}/members/", 
                                   headers={"Authorization": f"Bearer {self.admin_token}"})
            self.print_status("获取班级成员", self.check_response(response))
            
            # 获取班级统计
            response = requests.get(f"{self.base_url}/class/{self.class_id}/statistics/", 
                                   headers={"Authorization": f"Bearer {self.admin_token}"})
            self.print_status("获取班级统计", self.check_response(response))
        
        # 学生获取所在班级
        if self.student_token:
            response = requests.get(f"{self.base_url}/student/class", 
                                   headers={"Authorization": f"Bearer {self.student_token}"})
            self.print_status("学生获取所在班级", self.check_response(response))
    
    # 8. 错题本测试
    def test_mistake_book(self):
        """测试错题本"""
        print("\n=== 错题本测试 ===")
        
        if self.student_token:
            response = requests.get(f"{self.base_url}/mistake/list/", 
                                   headers={"Authorization": f"Bearer {self.student_token}"})
            self.print_status("获取错题列表", self.check_response(response))
            
            response = requests.get(f"{self.base_url}/mistake/statistics/", 
                                   headers={"Authorization": f"Bearer {self.student_token}"})
            self.print_status("获取错题统计", self.check_response(response))
    
    # 运行所有测试
    def run_all_tests(self):
        """运行所有快速测试"""
        print("="*50)
        print("在线考试系统快速功能测试")
        print("="*50)
        
        # 检查服务器状态
        try:
            response = requests.get(f"{self.base_url}/user/info/", timeout=5)
        except:
            print("✗ 无法连接到服务器")
            print(f"请确保 Django 服务器正在运行: python manage.py runserver 8010")
            return
        
        print("✓ 服务器运行正常")
        
        try:
            self.test_user_auth()
            self.test_question_management()
            self.test_exam_management()
            self.test_exam_functionality()
            self.test_exam_records()
            self.test_statistics()
            self.test_class_management()
            self.test_mistake_book()
            
            print("\n" + "="*50)
            print("快速测试完成")
            print("="*50)
            
        except Exception as e:
            print(f"\n✗ 测试过程中发生错误: {str(e)}")


def main():
    tester = QuickTester()
    tester.run_all_tests()


if __name__ == "__main__":
    main()