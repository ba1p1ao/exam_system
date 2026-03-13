<template>
  <div class="home-container">
    <!-- 欢迎卡片 -->
    <el-card class="welcome-card">
      <div class="welcome-content">
        <h2>👋 欢迎，{{ userStore.userInfo?.nickname }}</h2>
        <p>今天是 {{ currentDate }}，{{ getGreeting() }}</p>
      </div>
    </el-card>

    <!-- 系统统计数据 (管理员和教师可见) -->
    <el-row :gutter="20" v-if="isTeacherOrAdmin" style="margin-top: 20px">
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-item">
            <div class="stat-icon" style="background-color: #409EFF">
              <el-icon><Document /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-title">题目总数</div>
              <div class="stat-value">{{ stats.questionCount }}</div>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-item">
            <div class="stat-icon" style="background-color: #67C23A">
              <el-icon><Notebook /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-title">试卷总数</div>
              <div class="stat-value">{{ stats.examCount }}</div>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-item">
            <div class="stat-icon" style="background-color: #E6A23C">
              <el-icon><Edit /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-title">考试记录</div>
              <div class="stat-value">{{ stats.recordCount }}</div>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-item">
            <div class="stat-icon" style="background-color: #F56C6C">
              <el-icon><User /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-title">用户总数</div>
              <div class="stat-value">{{ stats.userCount }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 学生个人统计 -->
    <el-row :gutter="20" v-if="isStudent" style="margin-top: 20px">
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-item">
            <div class="stat-icon" style="background-color: #409EFF">
              <el-icon><Document /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-title">已参加考试</div>
              <div class="stat-value">{{ studentStats.examCount }}</div>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-item">
            <div class="stat-icon" style="background-color: #67C23A">
              <el-icon><TrendCharts /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-title">平均分</div>
              <div class="stat-value">{{ studentStats.avgScore }}</div>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-item">
            <div class="stat-icon" style="background-color: #E6A23C">
              <el-icon><Warning /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-title">错题数量</div>
              <div class="stat-value">{{ studentStats.mistakeCount }}</div>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-item">
            <div class="stat-icon" style="background-color: #F56C6C">
              <el-icon><Trophy /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-title">班级排名</div>
              <div class="stat-value">{{ studentStats.classRank || '-' }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 待参加考试 (学生) -->
    <el-row :gutter="20" v-if="isStudent" style="margin-top: 20px">
      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>📚 待参加的考试</span>
              <el-button type="primary" size="small" @click="$router.push('/exam-list')">
                查看全部
              </el-button>
            </div>
          </template>
          <div v-if="availableExams.length > 0">
            <div
              v-for="exam in availableExams.slice(0, 3)"
              :key="exam.id"
              class="exam-item"
              @click="$router.push(`/exam-take/${exam.id}`)"
            >
              <div class="exam-info">
                <div class="exam-title">{{ exam.title }}</div>
                <div class="exam-desc">{{ exam.description }}</div>
              </div>
              <div class="exam-meta">
                <el-tag size="small">{{ exam.duration }}分钟</el-tag>
                <el-tag size="small" type="success">{{ exam.total_score }}分</el-tag>
              </div>
            </div>
          </div>
          <el-empty v-else description="暂无待参加的考试" />
        </el-card>
      </el-col>

      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>📝 最近考试记录</span>
              <el-button type="primary" size="small" @click="$router.push('/records')">
                查看全部
              </el-button>
            </div>
          </template>
          <div v-if="recentRecords.length > 0">
            <div
              v-for="record in recentRecords.slice(0, 3)"
              :key="record.id"
              class="record-item"
              @click="$router.push(`/exam-record/${record.id}`)"
            >
              <div class="record-info">
                <div class="record-title">{{ record.exam_title }}</div>
                <div class="record-time">{{ record.submit_time }}</div>
              </div>
              <div class="record-score">
                <span :class="record.is_passed ? 'pass' : 'fail'">
                  {{ record.score }}分
                </span>
              </div>
            </div>
          </div>
          <el-empty v-else description="暂无考试记录" />
        </el-card>
      </el-col>
    </el-row>

    <!-- 教师班级统计 -->
    <el-row :gutter="20" v-if="isTeacher" style="margin-top: 20px">
      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>🏫 我管理的班级</span>
              <el-button type="primary" size="small" @click="$router.push('/class-management')">
                管理班级
              </el-button>
            </div>
          </template>
          <div v-if="teacherClasses.length > 0">
            <div
              v-for="cls in teacherClasses.slice(0, 3)"
              :key="cls.id"
              class="class-item"
              @click="$router.push(`/class-management`)"
            >
              <div class="class-info">
                <div class="class-name">{{ cls.name }}</div>
                <div class="class-grade">{{ cls.grade }}</div>
              </div>
              <div class="class-stats">
                <el-tag size="small">{{ cls.student_count }}名学生</el-tag>
              </div>
            </div>
          </div>
          <el-empty v-else description="暂无管理的班级" />
        </el-card>
      </el-col>

      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>📋 最近创建的试卷</span>
              <el-button type="primary" size="small" @click="$router.push('/exams')">
                创建试卷
              </el-button>
            </div>
          </template>
          <div v-if="recentExams.length > 0">
            <div
              v-for="exam in recentExams.slice(0, 3)"
              :key="exam.id"
              class="exam-item"
              @click="$router.push(`/exam-detail/${exam.id}`)"
            >
              <div class="exam-info">
                <div class="exam-title">{{ exam.title }}</div>
                <div class="exam-desc">{{ exam.description }}</div>
              </div>
              <div class="exam-meta">
                <el-tag :type="getStatusType(exam.status)" size="small">
                  {{ getStatusText(exam.status) }}
                </el-tag>
              </div>
            </div>
          </div>
          <el-empty v-else description="暂无试卷" />
        </el-card>
      </el-col>
    </el-row>

    <!-- 管理员统计 -->
    <el-row :gutter="20" v-if="isAdmin" style="margin-top: 20px">
      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>🏫 班级统计</span>
              <el-button type="primary" size="small" @click="$router.push('/class-management')">
                管理班级
              </el-button>
            </div>
          </template>
          <div v-if="classList.length > 0">
            <div
              v-for="cls in classList.slice(0, 3)"
              :key="cls.id"
              class="class-item"
              @click="$router.push(`/class-management`)"
            >
              <div class="class-info">
                <div class="class-name">{{ cls.name }}</div>
                <div class="class-grade">{{ cls.grade }}</div>
              </div>
              <div class="class-stats">
                <el-tag size="small">{{ cls.student_count }}名学生</el-tag>
              </div>
            </div>
          </div>
          <el-empty v-else description="暂无班级" />
        </el-card>
      </el-col>

      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>👥 用户统计</span>
              <el-button type="primary" size="small" @click="$router.push('/users')">
                管理用户
              </el-button>
            </div>
          </template>
          <div class="user-stats">
            <div class="user-stat-item">
              <div class="user-stat-label">学生</div>
              <div class="user-stat-value">{{ userStats.studentCount }}</div>
            </div>
            <div class="user-stat-item">
              <div class="user-stat-label">教师</div>
              <div class="user-stat-value">{{ userStats.teacherCount }}</div>
            </div>
            <div class="user-stat-item">
              <div class="user-stat-label">管理员</div>
              <div class="user-stat-value">{{ userStats.adminCount }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 快捷操作 -->
    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="24">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>⚡ 快捷操作</span>
            </div>
          </template>
          <div class="quick-actions">
            <el-button v-if="isStudent" type="primary" size="large" @click="$router.push('/exam-list')">
              <el-icon><Document /></el-icon>
              参加考试
            </el-button>
            <el-button v-if="isStudent" type="warning" size="large" @click="$router.push('/mistake-book')">
              <el-icon><Warning /></el-icon>
              错题本
            </el-button>
            <el-button v-if="isStudent" type="success" size="large" @click="$router.push('/ranking')">
              <el-icon><Trophy /></el-icon>
              成绩排名
            </el-button>
            <el-button v-if="isTeacherOrAdmin" type="success" size="large" @click="$router.push('/questions')">
              <el-icon><Document /></el-icon>
              管理题库
            </el-button>
            <el-button v-if="isTeacherOrAdmin" type="warning" size="large" @click="$router.push('/exams')">
              <el-icon><Edit /></el-icon>
              创建试卷
            </el-button>
            <el-button v-if="isTeacherOrAdmin" type="info" size="large" @click="$router.push('/class-management')">
              <el-icon><School /></el-icon>
              班级管理
            </el-button>
            <el-button v-if="isAdmin" type="danger" size="large" @click="$router.push('/users')">
              <el-icon><User /></el-icon>
              用户管理
            </el-button>
            <el-button type="primary" size="large" @click="$router.push('/records')">
              <el-icon><Notebook /></el-icon>
              考试记录
            </el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useUserStore } from '@/stores/user'
import {
  getSystemStatistics,
  getExamList,
  getExamRecordList,
  getAvailableExamList
} from '@/api/exam'
import { getMistakeListWithStatistics } from '@/api/mistake'
import { getTeacherClasses, getClassList, getStudentClass } from '@/api/class'
import { getUserStatistics } from '@/api/admin'
import {
  Document,
  Notebook,
  Edit,
  User,
  TrendCharts,
  Warning,
  Trophy,
  School
} from '@element-plus/icons-vue'

const userStore = useUserStore()

const stats = ref({
  questionCount: 0,
  examCount: 0,
  recordCount: 0,
  userCount: 0
})

const studentStats = ref({
  examCount: 0,
  avgScore: 0,
  mistakeCount: 0,
  classRank: null
})

const userStats = ref({
  studentCount: 0,
  teacherCount: 0,
  adminCount: 0
})

const availableExams = ref([])
const recentRecords = ref([])
const recentExams = ref([])
const teacherClasses = ref([])
const classList = ref([])

const currentDate = ref('')

const isStudent = computed(() => userStore.userInfo?.role === 'student')
const isTeacher = computed(() => userStore.userInfo?.role === 'teacher')
const isAdmin = computed(() => userStore.userInfo?.role === 'admin')
const isTeacherOrAdmin = computed(() => ['teacher', 'admin'].includes(userStore.userInfo?.role))

const getGreeting = () => {
  const hour = new Date().getHours()
  if (hour < 12) return '早上好'
  if (hour < 18) return '下午好'
  return '晚上好'
}

const getStatusType = (status) => {
  const typeMap = {
    draft: 'info',
    published: 'success',
    closed: 'danger'
  }
  return typeMap[status] || 'info'
}

const getStatusText = (status) => {
  const textMap = {
    draft: '草稿',
    published: '已发布',
    closed: '已关闭'
  }
  return textMap[status] || '未知'
}

const loadSystemStatistics = async () => {
  try {
    const res = await getSystemStatistics()
    if (res && res.data) {
      stats.value = {
        questionCount: res.data.question_count || 0,
        examCount: res.data.exam_count || 0,
        recordCount: res.data.record_count || 0,
        userCount: res.data.user_count || 0
      }
    }
  } catch (error) {
    console.error('获取系统统计数据失败:', error)
    ElMessage.error('加载统计数据失败，请刷新页面重试')
  }
}

const loadStudentStatistics = async () => {
  try {
    console.log('=== loadStudentStatistics 已更新 (2026-01-08) ===')
    // 获取考试记录
    const recordRes = await getExamRecordList({ page: 1, size: 100 })
    const records = recordRes.data.list || []
    console.log('考试记录数量:', records.length)
    studentStats.value.examCount = records.length

    if (records.length > 0) {
      const totalScore = records.reduce((sum, r) => sum + (r.score || 0), 0)
      studentStats.value.avgScore = (totalScore / records.length).toFixed(1)
    }

    // 获取错题统计
    const mistakeRes = await getMistakeListWithStatistics({ page: 1, size: 1 })
    studentStats.value.mistakeCount = mistakeRes.data.statistics?.total_mistakes || 0

    // 获取班级信息
    const classRes = await getStudentClass()
    if (classRes.data) {
      studentStats.value.classRank = classRes.data.my_rank
    }

    // 获取待参加的考试
    const examRes = await getAvailableExamList()
    availableExams.value = examRes.data || []

    // 获取最近考试记录
    recentRecords.value = records.slice(0, 5)
  } catch (error) {
    console.error('获取学生统计数据失败:', error)
  }
}

const loadTeacherStatistics = async () => {
  try {
    // 获取管理的班级
    const classRes = await getTeacherClasses({ page: 1, size: 100 })
    teacherClasses.value = classRes.data.list || []

    // 获取最近创建的试卷
    const examRes = await getExamList({ page: 1, size: 100 })
    recentExams.value = examRes.data.list || []
  } catch (error) {
    console.error('获取教师统计数据失败:', error)
  }
}

const loadAdminStatistics = async () => {
  try {
    // 获取班级列表
    const classRes = await getClassList({ page: 1, size: 100 })
    classList.value = classRes.data.list || []

    // 获取最近创建的试卷
    const examRes = await getExamList({ page: 1, size: 100 })
    recentExams.value = examRes.data.list || []

    // 获取用户统计数据
    const userStatsRes = await getUserStatistics()
    if (userStatsRes && userStatsRes.data) {
      userStats.value = {
        studentCount: userStatsRes.data.student_count || 0,
        teacherCount: userStatsRes.data.teacher_count || 0,
        adminCount: userStatsRes.data.admin_count || 0
      }
    }
  } catch (error) {
    console.error('获取管理员统计数据失败:', error)
  }
}

const updateCurrentDate = () => {
  const now = new Date()
  const year = now.getFullYear()
  const month = String(now.getMonth() + 1).padStart(2, '0')
  const day = String(now.getDate()).padStart(2, '0')
  const weekDays = ['日', '一', '二', '三', '四', '五', '六']
  const weekDay = weekDays[now.getDay()]
  currentDate.value = `${year}年${month}月${day}日 星期${weekDay}`
}

onMounted(() => {
  updateCurrentDate()

  if (isTeacherOrAdmin.value) {
    loadSystemStatistics()
  }

  if (isStudent.value) {
    loadStudentStatistics()
  } else if (isTeacher.value) {
    loadTeacherStatistics()
  } else if (isAdmin.value) {
    loadAdminStatistics()
  }
})
</script>

<style scoped>
.home-container {
  padding: 0;
}

.welcome-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  margin-bottom: 20px;
}

.welcome-card :deep(.el-card__body) {
  padding: 30px;
}

.welcome-content h2 {
  margin: 0 0 10px 0;
  font-size: 28px;
  font-weight: 600;
}

.welcome-content p {
  margin: 0;
  font-size: 16px;
  opacity: 0.9;
}

.stat-card {
  margin-bottom: 20px;
  transition: transform 0.3s;
  cursor: pointer;
}

.stat-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.stat-item {
  display: flex;
  align-items: center;
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 20px;
}

.stat-icon .el-icon {
  font-size: 30px;
  color: #fff;
}

.stat-content {
  flex: 1;
}

.stat-title {
  font-size: 14px;
  color: #909399;
  margin-bottom: 8px;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #303133;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: bold;
  color: #303133;
}

.exam-item,
.record-item,
.class-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px;
  border-bottom: 1px solid #f0f0f0;
  cursor: pointer;
  transition: background-color 0.3s;
}

.exam-item:hover,
.record-item:hover,
.class-item:hover {
  background-color: #f5f7fa;
}

.exam-item:last-child,
.record-item:last-child,
.class-item:last-child {
  border-bottom: none;
}

.exam-info,
.record-info,
.class-info {
  flex: 1;
}

.exam-title,
.record-title,
.class-name {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 5px;
}

.exam-desc,
.record-time,
.class-grade {
  font-size: 14px;
  color: #909399;
}

.exam-meta,
.record-score,
.class-stats {
  display: flex;
  gap: 8px;
  align-items: center;
}

.record-score .pass {
  color: #67C23A;
  font-weight: bold;
  font-size: 18px;
}

.record-score .fail {
  color: #F56C6C;
  font-weight: bold;
  font-size: 18px;
}

.user-stats {
  display: flex;
  justify-content: space-around;
  padding: 20px 0;
}

.user-stat-item {
  text-align: center;
}

.user-stat-label {
  font-size: 14px;
  color: #909399;
  margin-bottom: 10px;
}

.user-stat-value {
  font-size: 32px;
  font-weight: bold;
  color: #409EFF;
}

.quick-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
}

.quick-actions .el-button {
  margin: 0;
  min-width: 140px;
}

.quick-actions .el-button .el-icon {
  margin-right: 5px;
}
</style>