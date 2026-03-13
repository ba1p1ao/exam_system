<template>
  <div class="exam-detail-container">
    <el-card>
      <template #header>
        <div class="header-container">
          <el-button @click="goBack" :icon="ArrowLeft">返回</el-button>
          <span class="title">考试详情</span>
        </div>
      </template>

      <!-- 考试基本信息 -->
      <div class="exam-info-section">
        <h3>考试基本信息</h3>
        <el-descriptions :column="2" border>
          <el-descriptions-item label="试卷标题">{{ examInfo.title }}</el-descriptions-item>
          <el-descriptions-item label="试卷描述">{{ examInfo.description || '-' }}</el-descriptions-item>
          <el-descriptions-item label="总分">{{ examInfo.total_score }} 分</el-descriptions-item>
          <el-descriptions-item label="及格分">{{ examInfo.pass_score }} 分</el-descriptions-item>
          <el-descriptions-item label="考试时长">{{ examInfo.duration }} 分钟</el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="getExamStatusColor(examInfo.status) || undefined">{{ getExamStatusText(examInfo.status) }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="开始时间">{{ examInfo.start_time || '-' }}</el-descriptions-item>
          <el-descriptions-item label="结束时间">{{ examInfo.end_time || '-' }}</el-descriptions-item>
        </el-descriptions>
      </div>

      <!-- 考试统计信息 -->
      <div class="exam-statistics-section" v-if="statistics">
        <h3>考试统计</h3>
        <el-descriptions :column="3" border>
          <el-descriptions-item label="参加人数">{{ statistics.total_participants || 0 }}</el-descriptions-item>
          <el-descriptions-item label="未参加">{{ statistics.not_participated || 0 }}</el-descriptions-item>
          <el-descriptions-item label="及格率">{{ statistics.pass_rate !== null && statistics.pass_rate !== undefined ? (statistics.pass_rate * 100).toFixed(1) + '%' : '-' }}</el-descriptions-item>
          <el-descriptions-item label="平均分">{{ statistics.average_score !== null && statistics.average_score !== undefined ? statistics.average_score.toFixed(1) : '-' }}</el-descriptions-item>
          <el-descriptions-item label="最高分">{{ statistics.max_score !== null && statistics.max_score !== undefined ? statistics.max_score : '-' }}</el-descriptions-item>
          <el-descriptions-item label="最低分">{{ statistics.min_score !== null && statistics.min_score !== undefined ? statistics.min_score : '-' }}</el-descriptions-item>
        </el-descriptions>
      </div>

      <!-- 数据可视化图表 -->
      <div class="exam-charts-section" v-if="statistics && statistics.total_participants > 0">
        <h3>数据可视化</h3>
        <el-row :gutter="20">
          <!-- 成绩分布图 -->
          <el-col :span="12">
            <el-card>
              <template #header>
                <span>成绩分布</span>
              </template>
              <div ref="scoreDistributionChartRef" style="height: 400px"></div>
            </el-card>
          </el-col>
          <!-- 题目正确率图 -->
          <el-col :span="12">
            <el-card>
              <template #header>
                <span>题目正确率</span>
              </template>
              <div ref="questionCorrectnessChartRef" style="height: 400px"></div>
            </el-card>
          </el-col>
        </el-row>
      </div>

      <!-- 考试分析报告 -->
      <div class="exam-report-section" v-if="statistics && statistics.total_participants > 0">
        <h3>考试分析报告</h3>
        <el-row :gutter="20">
          <el-col :span="8">
            <el-button type="primary" @click="handleGenerateReport" :loading="reportGenerating">
              <el-icon><Document /></el-icon>
              生成报告
            </el-button>
          </el-col>
          <el-col :span="8">
            <el-button type="success" @click="handleExportReport" :loading="reportExporting">
              <el-icon><Download /></el-icon>
              导出报告（PDF）
            </el-button>
          </el-col>
        </el-row>
      </div>

      <!-- 学生成绩列表 -->
      <div class="student-records-section">
        <h3>学生成绩列表</h3>
        
        <!-- 学生成绩筛选表单 -->
        <el-form :inline="true" :model="searchForm" class="student-search-form">
          <el-form-item label="用户名">
            <el-input v-model="searchForm.username" placeholder="请输入用户名" clearable style="width: 150px" />
          </el-form-item>
          <el-form-item label="昵称">
            <el-input v-model="searchForm.nickname" placeholder="请输入昵称" clearable style="width: 150px" />
          </el-form-item>
          <el-form-item label="考试状态">
            <el-select v-model="searchForm.status" placeholder="请选择" clearable style="width: 150px">
              <el-option label="未开始" value="not_started" />
              <el-option label="进行中" value="in_progress" />
              <el-option label="已提交" value="submitted" />
              <el-option label="已阅卷" value="graded" />
            </el-select>
          </el-form-item>
          <el-form-item label="是否及格">
            <el-select v-model="searchForm.is_passed" placeholder="请选择" clearable style="width: 150px">
              <el-option label="是" :value="1" />
              <el-option label="否" :value="0" />
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="handleSearch">筛选</el-button>
            <el-button @click="handleReset">重置</el-button>
          </el-form-item>
        </el-form>

        <el-table :data="filteredStudentRecords" v-loading="loading" border>
          <el-table-column prop="user_id" label="学生ID" width="100" />
          <el-table-column prop="username" label="用户名" width="120" />
          <el-table-column prop="nickname" label="昵称" width="120" />
          <el-table-column prop="role" label="角色" width="100">
            <template #default="{ row }">
              <el-tag size="small">{{ getRoleText(row.role) }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="score" label="得分" width="100">
            <template #default="{ row }">
              <span v-if="row.score !== null" :style="{ color: row.is_passed ? '#67C23A' : '#F56C6C', fontWeight: 'bold' }">
                {{ row.score }} 分
              </span>
              <span v-else>-</span>
            </template>
          </el-table-column>
          <el-table-column prop="score_rate" label="得分率" width="100">
            <template #default="{ row }">
              <span v-if="row.score !== null && examInfo.total_score">
                {{ ((row.score / examInfo.total_score) * 100).toFixed(1) }}%
              </span>
              <span v-else>-</span>
            </template>
          </el-table-column>
          <el-table-column prop="is_passed" label="是否及格" width="100">
            <template #default="{ row }">
              <el-tag v-if="row.is_passed !== null" :type="row.is_passed ? 'success' : 'danger'" size="small">
                {{ row.is_passed ? '及格' : '不及格' }}
              </el-tag>
              <span v-else>-</span>
            </template>
          </el-table-column>
          <el-table-column prop="status" label="状态" width="100">
            <template #default="{ row }">
              <el-tag :type="getStatusColor(row.status) || undefined" size="small">{{ getStatusText(row.status) }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="start_time" label="开始时间" width="180" />
          <el-table-column prop="submit_time" label="提交时间" width="180" />
          <el-table-column label="操作" width="100" fixed="right">
            <template #default="{ row }">
              <el-button type="primary" size="small" @click="handleViewStudentRecord(row)">详情</el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed, nextTick, watch, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ArrowLeft, Document, Download } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getExamDetail, getExamStatistics, getGroupedExamRecords } from '@/api/exam'
import { getScoreDistributionChart, getQuestionCorrectnessChart } from '@/api/chart'
import { generateExamReport, exportExamReport } from '@/api/report'
import * as echarts from 'echarts'

const router = useRouter()
const route = useRoute()

const loading = ref(false)
const examInfo = ref({})
const statistics = ref(null)
const studentRecords = ref([])
const scoreDistributionChartRef = ref(null)
const questionCorrectnessChartRef = ref(null)
const reportGenerating = ref(false)
const reportExporting = ref(false)
let scoreDistributionChart = null
let questionCorrectnessChart = null

const searchForm = reactive({
  username: '',
  nickname: '',
  status: '',
  is_passed: ''
})

const getExamStatusText = (status) => {
  const statusMap = {
    draft: '草稿',
    published: '已发布',
    closed: '已关闭'
  }
  return statusMap[status] || status
}

const getExamStatusColor = (status) => {
  const colorMap = {
    draft: 'info',
    published: 'success',
    closed: 'danger'
  }
  return colorMap[status]
}

const getStatusText = (status) => {
  const statusMap = {
    not_started: '未开始',
    in_progress: '进行中',
    submitted: '已提交',
    graded: '已阅卷'
  }
  return statusMap[status] || status
}

const getStatusColor = (status) => {
  const colorMap = {
    not_started: 'info',
    in_progress: 'warning',
    submitted: 'primary',
    graded: 'success'
  }
  return colorMap[status]
}

const getRoleText = (role) => {
  const roleMap = {
    student: '学生',
    teacher: '教师',
    admin: '管理员'
  }
  return roleMap[role] || role
}

const goBack = () => {
  router.back()
}

const loadExamInfo = async () => {
  const examId = route.params.id
  loading.value = true
  try {
    const res = await getExamDetail(examId)
    examInfo.value = res.data
  } catch (error) {
    console.error('加载考试信息失败:', error)
  } finally {
    loading.value = false
  }
}

const loadStatistics = async () => {
  const examId = route.params.id
  try {
    const res = await getExamStatistics(examId)
    statistics.value = res.data
  } catch (error) {
    console.error('加载统计信息失败:', error)
  }
}

const loadStudentRecords = async () => {
  const examId = route.params.id
  loading.value = true
  try {
    const res = await getGroupedExamRecords({ page: 1, size: 100 })
    const exam = res.data.list.find(e => e.id === parseInt(examId))
    if (exam && exam.student_records) {
      studentRecords.value = exam.student_records
    }
  } catch (error) {
    console.error('加载学生记录失败:', error)
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  // 筛选逻辑在 computed 中处理
}

const handleReset = () => {
  searchForm.username = ''
  searchForm.nickname = ''
  searchForm.status = ''
  searchForm.is_passed = ''
}

const filteredStudentRecords = computed(() => {
  let records = studentRecords.value || []

  const { username, nickname, status, is_passed } = searchForm

  return records.filter(record => {
    // 用户名筛选
    if (username && !record.username?.toLowerCase().includes(username.toLowerCase())) {
      return false
    }
    // 昵称筛选
    if (nickname && !record.nickname?.toLowerCase().includes(nickname.toLowerCase())) {
      return false
    }
    // 状态筛选（当 status 为空字符串、null 或 undefined 时不过滤）
    if (status && status !== '' && status !== null && status !== undefined && record.status !== status) {
      return false
    }
    // 是否及格筛选（当 is_passed 为空字符串、null 或 undefined 时不过滤）
    if (is_passed !== '' && is_passed !== null && is_passed !== undefined && record.is_passed != is_passed) {
      return false
    }
    return true
  })
})

const handleViewStudentRecord = (studentRecord) => {
  router.push(`/exam-record/${studentRecord.id}`)
}

const loadScoreDistributionChart = async () => {
  const examId = route.params.id
  try {
    const res = await getScoreDistributionChart(examId)
    const data = res.data
    renderScoreDistributionChart(data)
  } catch (error) {
    console.error('加载成绩分布图失败:', error)
  }
}

const loadQuestionCorrectnessChart = async () => {
  const examId = route.params.id
  try {
    const res = await getQuestionCorrectnessChart(examId)
    const data = res.data
    renderQuestionCorrectnessChart(data)
  } catch (error) {
    console.error('加载题目正确率图失败:', error)
  }
}

const renderScoreDistributionChart = (data) => {
  if (!scoreDistributionChartRef.value) return
  
  scoreDistributionChart = echarts.init(scoreDistributionChartRef.value)
  
  const option = {
    title: {
      text: '成绩分布',
      left: 'center'
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      }
    },
    xAxis: {
      type: 'category',
      data: Object.keys(data.distribution || {}),
      axisLabel: {
        rotate: 45
      }
    },
    yAxis: {
      type: 'value',
      name: '人数'
    },
    series: [
      {
        name: '人数',
        type: 'bar',
        data: Object.values(data.distribution || {}),
        itemStyle: {
          color: function(params) {
            const colors = ['#5470C6', '#91CC75', '#FAC858', '#EE6666', '#73C0DE']
            return colors[params.dataIndex % colors.length]
          }
        },
        label: {
          show: true,
          position: 'top'
        }
      }
    ]
  }
  
  scoreDistributionChart.setOption(option)
}

const renderQuestionCorrectnessChart = (data) => {
  if (!questionCorrectnessChartRef.value) return
  
  questionCorrectnessChart = echarts.init(questionCorrectnessChartRef.value)
  
  const option = {
    title: {
      text: '题目正确率',
      left: 'center'
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      }
    },
    xAxis: {
      type: 'value',
      name: '正确率',
      max: 100,
      axisLabel: {
        formatter: '{value}%'
      }
    },
    yAxis: {
      type: 'category',
      data: data.questions?.map(q => `题目${q.question_id}`) || [],
      inverse: true
    },
    series: [
      {
        name: '正确率',
        type: 'bar',
        data: data.questions?.map(q => (q.correct_rate * 100).toFixed(1)) || [],
        itemStyle: {
          color: function(params) {
            const value = params.value
            if (value >= 80) return '#67C23A'
            if (value >= 60) return '#E6A23C'
            return '#F56C6C'
          }
        },
        label: {
          show: true,
          position: 'right',
          formatter: '{c}%'
        }
      }
    ]
  }
  
  questionCorrectnessChart.setOption(option)
}

const initCharts = () => {
  nextTick(() => {
    loadScoreDistributionChart()
    loadQuestionCorrectnessChart()
  })
}

const handleGenerateReport = async () => {
  const examId = route.params.id
  reportGenerating.value = true
  try {
    const res = await generateExamReport(examId, {
      include_charts: true,
      include_ranking: true
    })
    ElMessage.success('报告生成成功')
  } catch (error) {
    console.error('生成报告失败:', error)
    ElMessage.error('生成报告失败')
  } finally {
    reportGenerating.value = false
  }
}

const handleExportReport = async () => {
  const examId = route.params.id
  reportExporting.value = true
  try {
    const res = await exportExamReport(examId)
    const blob = new Blob([res], { type: 'application/pdf' })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `${examInfo.value.title}_分析报告.pdf`
    link.click()
    window.URL.revokeObjectURL(url)
    ElMessage.success('导出成功')
  } catch (error) {
    console.error('导出报告失败:', error)
    ElMessage.error('导出报告失败')
  } finally {
    reportExporting.value = false
  }
}

// 监听 statistics 变化，当有数据时初始化图表
watch(() => statistics.value, (newVal) => {
  if (newVal && newVal.total_participants > 0) {
    initCharts()
  }
})

onMounted(() => {
  loadExamInfo()
  loadStatistics()
  loadStudentRecords()
})

onUnmounted(() => {
  if (scoreDistributionChart) {
    scoreDistributionChart.dispose()
  }
  if (questionCorrectnessChart) {
    questionCorrectnessChart.dispose()
  }
})
</script>

<style scoped>
.exam-detail-container {
  padding: 20px;
}

.header-container {
  display: flex;
  align-items: center;
  gap: 15px;
}

.title {
  font-size: 18px;
  font-weight: 600;
}

.exam-info-section,
.exam-statistics-section,
.student-records-section {
  margin-top: 30px;
}

.exam-info-section h3,
.exam-statistics-section h3,
.student-records-section h3 {
  margin-bottom: 15px;
  color: #303133;
  font-weight: 600;
  font-size: 16px;
}

.student-search-form {
  margin-bottom: 20px;
  padding: 15px;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.student-search-form :deep(.el-form-item) {
  margin-bottom: 0;
}
</style>