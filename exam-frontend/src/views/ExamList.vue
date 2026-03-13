<template>
  <div class="exam-list-container">
    <el-card>
      <template #header>
        <span>考试列表</span>
      </template>

      <el-table :data="examList" v-loading="loading" border style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="title" label="试卷标题" show-overflow-tooltip />
        <el-table-column prop="description" label="描述" show-overflow-tooltip />
        <el-table-column prop="duration" label="时长(分钟)" width="120" />
        <el-table-column prop="total_score" label="总分" width="80" />
        <el-table-column prop="pass_score" label="及格分" width="80" />
        <el-table-column prop="start_time" label="开始时间" width="180" />
        <el-table-column prop="end_time" label="结束时间" width="180" />
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button
              type="primary"
              size="small"
              @click="handleTakeExam(row)"
              :disabled="!canTakeExam(row)"
              :title="getDisabledMessage(row)"
            >
              参加考试
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'
import { getAvailableExamList, getExamRecordList } from '@/api/exam'

const userStore = useUserStore()
const userInfo = computed(() => userStore.userInfo || {})
const router = useRouter()

const loading = ref(false)
const examList = ref([])
const userExamRecords = ref([])

const canTakeExam = (exam) => {
  const now = new Date()
  const startTime = new Date(exam.start_time)
  const endTime = new Date(exam.end_time)

  const inTimeRange = now >= startTime && now <= endTime
  if (!inTimeRange) {
    return false
  }

  // 添加默认值检查
  const allowRetake = exam.allow_retake !== undefined ? exam.allow_retake : 0
  if (allowRetake === 0) {
    const hasTaken = userExamRecords.value.some(
      record => record.exam_id === exam.id
    )
    if (hasTaken) {
      return false
    }
  }

  return true
}

const getDisabledMessage = (exam) => {
  const now = new Date()
  const startTime = new Date(exam.start_time)
  const endTime = new Date(exam.end_time)
  
  // 检查考试时间
  if (now < startTime) {
    return '考试尚未开始'
  }
  if (now > endTime) {
    return '考试已结束'
  }
  
  // 检查是否已参加
  if (exam.allow_retake === 0) {
    const hasTaken = userExamRecords.value.some(
      record => record.exam_id === exam.id
    )
    if (hasTaken) {
      return '该考试不允许重复作答'
    }
  }
  
  return ''
}

const loadExamList = async () => {
  loading.value = true
  try {
    const res = await getAvailableExamList()
    examList.value = res.data || []
    
    // 加载用户的考试记录
    const recordsRes = await getExamRecordList({ page: 1, size: 1000 })
    userExamRecords.value = recordsRes.data.list || []
  } catch (error) {
    console.error(error)
  } finally {
    loading.value = false
  }
}

const handleTakeExam = async (exam) => {
  if (!canTakeExam(exam)) {
    ElMessage.warning('当前不在考试时间内')
    return
  }
  router.push(`/exam-take/${exam.id}`)
}

onMounted(() => {
  // 检查是否为学生
  if (userInfo.value.role !== 'student') {
    ElMessage.error('此页面仅供学生使用')
    router.push('/home')
    return
  }
  loadExamList()
})
</script>

<style scoped>
.exam-list-container {
  height: 100%;
}
</style>