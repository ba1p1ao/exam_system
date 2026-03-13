<template>
  <el-container class="layout-container">
    <el-aside width="200px">
      <div class="logo">在线考试系统</div>
      <el-menu
        :default-active="activeMenu"
        router
        background-color="#304156"
        text-color="#bfcbd9"
        active-text-color="#409EFF"
      >
        <el-menu-item index="/home">
          <el-icon><HomeFilled /></el-icon>
          <span>首页</span>
        </el-menu-item>

        <!-- 教师和管理员菜单 -->
        <template v-if="isTeacherOrAdmin">
          <el-menu-item index="/questions">
            <el-icon><Document /></el-icon>
            <span>题库管理</span>
          </el-menu-item>
          <el-menu-item index="/exams">
            <el-icon><Notebook /></el-icon>
            <span>试卷管理</span>
          </el-menu-item>
          <el-menu-item index="/class-management">
            <el-icon><School /></el-icon>
            <span>班级管理</span>
          </el-menu-item>
        </template>

        <!-- 管理员专属菜单 -->
        <template v-if="isAdmin">
          <el-menu-item index="/users">
            <el-icon><UserFilled /></el-icon>
            <span>用户管理</span>
          </el-menu-item>
        </template>

        <!-- 学生菜单 -->
        <template v-if="isStudent">
          <el-menu-item index="/exam-list">
            <el-icon><Edit /></el-icon>
            <span>参加考试</span>
          </el-menu-item>
          <el-menu-item index="/mistake-book">
            <el-icon><Collection /></el-icon>
            <span>错题本</span>
          </el-menu-item>
        </template>

        <!-- 所有角色 -->
        <el-menu-item index="/records">
          <el-icon><List /></el-icon>
          <span>考试记录</span>
        </el-menu-item>
        <el-menu-item index="/ranking">
          <el-icon><Trophy /></el-icon>
          <span>成绩排名</span>
        </el-menu-item>
        <el-menu-item index="/profile">
          <el-icon><User /></el-icon>
          <span>个人中心</span>
        </el-menu-item>
      </el-menu>
    </el-aside>

    <el-container>
      <el-header>
        <div class="header-left">
          <span>{{ currentTitle }}</span>
        </div>
        <div class="header-right">
          <el-dropdown @command="handleCommand">
            <span class="user-info">
              <el-avatar :size="32" :src="userStore.userInfo?.avatar">
                {{ userStore.userInfo?.nickname?.charAt(0) }}
              </el-avatar>
              <span class="username">{{ userStore.userInfo?.nickname }}</span>
              <el-icon><ArrowDown /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">个人中心</el-dropdown-item>
                <el-dropdown-item divided command="logout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>

      <el-main>
        <router-view :key="route.fullPath" />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { ElMessageBox } from 'element-plus'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const activeMenu = computed(() => route.path)
const currentTitle = computed(() => route.meta.title || '首页')

const isStudent = computed(() => userStore.userInfo?.role === 'student')
const isTeacherOrAdmin = computed(() => ['teacher', 'admin'].includes(userStore.userInfo?.role))
const isAdmin = computed(() => userStore.userInfo?.role === 'admin')

const handleCommand = async (command) => {
  if (command === 'logout') {
    try {
      await ElMessageBox.confirm('确定要退出登录吗？', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      })
      userStore.logout()
      router.push('/login')
    } catch (error) {
      // 用户取消
    }
  } else if (command === 'profile') {
    router.push('/profile')
  }
}
</script>

<style scoped>
.layout-container {
  height: 100vh;
}

.el-aside {
  background-color: #304156;
  color: #fff;
}

.logo {
  height: 60px;
  line-height: 60px;
  text-align: center;
  font-size: 18px;
  font-weight: bold;
  color: #fff;
  background-color: #2b3a4a;
}

.el-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: #fff;
  box-shadow: 0 1px 4px rgba(0, 21, 41, 0.08);
}

.header-left {
  font-size: 18px;
  font-weight: bold;
  color: #333;
}

.header-right {
  display: flex;
  align-items: center;
}

.user-info {
  display: flex;
  align-items: center;
  cursor: pointer;
}

.username {
  margin: 0 10px;
  font-size: 14px;
  color: #333;
}

.el-main {
  background-color: #f0f2f5;
  padding: 20px;
}
</style>