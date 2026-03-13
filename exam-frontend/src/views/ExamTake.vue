<template>
  <div class="exam-take-container">
    <el-card v-if="!examStarted">
      <div class="exam-info">
        <h2>{{ examInfo.title }}</h2>
        <p>{{ examInfo.description }}</p>
        <el-descriptions :column="2" border>
          <el-descriptions-item label="考试时长">{{ examInfo.duration }} 分钟</el-descriptions-item>
          <el-descriptions-item label="总分">{{ examInfo.total_score }} 分</el-descriptions-item>
          <el-descriptions-item label="及格分数">{{ examInfo.pass_score }} 分</el-descriptions-item>
          <el-descriptions-item label="题目数量">{{ questions.length }} 道</el-descriptions-item>
        </el-descriptions>
        <div class="start-btn">
          <el-button type="primary" size="large" @click="handleStartExam" :loading="starting">
            开始考试
          </el-button>
        </div>
      </div>
    </el-card>

    <div v-else class="exam-content">
      <!-- 考试头部 -->
      <div class="exam-header">
        <div class="exam-title">{{ examInfo.title }}</div>
        <div class="exam-timer">
          <el-icon><Timer /></el-icon>
          <span>剩余时间：{{ formatTime(remainingTime) }}</span>
        </div>
      </div>

      <!-- 题目导航 -->
      <div class="question-nav">
        <div
          v-for="(q, index) in questions"
          :key="q.id"
          class="nav-item"
          :class="{
            active: currentQuestionIndex === index,
            answered: isAnswered(q)
          }"
          @click="currentQuestionIndex = index"
        >
          {{ index + 1 }}
        </div>
      </div>

      <!-- 题目内容 -->
      <el-card class="question-card">
        <div class="question-header">
          <el-tag :type="getTypeColor(questions[currentQuestionIndex].type)">
            {{ getTypeText(questions[currentQuestionIndex].type) }}
          </el-tag>
          <span class="question-score">（{{ questions[currentQuestionIndex].score }}分）</span>
        </div>
        <div class="question-content">
          {{ currentQuestionIndex + 1 }}. {{ questions[currentQuestionIndex].content }}
        </div>

        <!-- 单选题 -->
        <div v-if="currentQuestion.type === 'single'" class="options">
          <el-radio-group v-model="answers[currentQuestion.id]" @change="autoSaveAnswer">
            <el-radio
              v-for="(option, key) in currentQuestion.options"
              :key="key"
              :value="key"
            >
              {{ key }}. {{ option }}
            </el-radio>
          </el-radio-group>
        </div>

        <!-- 多选题 -->
        <div v-else-if="currentQuestion.type === 'multiple'" class="options">
          <el-checkbox-group 
            :key="`multiple-${currentQuestion.id}`"
            :model-value="multipleAnswers[currentQuestion.id] || []" 
            @update:model-value="(val) => { multipleAnswers[currentQuestion.id] = val; autoSaveAnswer() }"
          >
            <el-checkbox
              v-for="(option, key) in currentQuestion.options"
              :key="key"
              :value="key"
            >
              {{ key }}. {{ option }}
            </el-checkbox>
          </el-checkbox-group>
        </div>

        <!-- 判断题 -->
        <div v-else-if="currentQuestion.type === 'judge'" class="options">
          <el-radio-group v-model="answers[currentQuestion.id]" @change="autoSaveAnswer">
            <el-radio
              v-for="(option, key) in currentQuestion.options"
              :key="key"
              :value="key"
            >
              {{ key }}. {{ option }}
            </el-radio>
          </el-radio-group>
        </div>

        <!-- 填空题 -->
        <div v-else-if="currentQuestion.type === 'fill'" class="options">
          <el-input
            v-model="answers[currentQuestion.id]"
            placeholder="请输入答案"
            @input="autoSaveAnswer"
          />
        </div>

        <!-- 操作按钮 -->
        <div class="action-buttons">
          <el-button @click="currentQuestionIndex--" :disabled="currentQuestionIndex === 0">
            上一题
          </el-button>
          <el-button
            v-if="currentQuestionIndex < questions.length - 1"
            type="primary"
            @click="currentQuestionIndex++"
          >
            下一题
          </el-button>
          <el-button
            v-else
            type="success"
            @click="handleSubmit(false)"
            :loading="submitting"
          >
            提交试卷
          </el-button>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getExamDetail, startExam, getExamQuestions, saveAnswer, submitExam, checkExamTime } from '@/api/exam'

const route = useRoute()
const router = useRouter()

const examId = route.params.id

const loading = ref(false)
const starting = ref(false)
const submitting = ref(false)
const examStarted = ref(false)

const examInfo = ref({})
const questions = ref([])
const answers = reactive({})
const multipleAnswers = reactive({})
const examRecordId = ref(null)
const remainingTime = ref(0)
const timer = ref(null)

const currentQuestionIndex = ref(0)

const currentQuestion = computed(() => questions.value[currentQuestionIndex.value])

// 当前题目的多选答案（用于确保立即更新）
const currentMultipleAnswer = computed({
  get() {
    return multipleAnswers[currentQuestion.value?.id] || []
  },
  set(value) {
    if (currentQuestion.value?.id) {
      multipleAnswers[currentQuestion.value.id] = value
    }
  }
})

const isAnswered = (question) => {
  if (question.type === 'multiple') {
    return multipleAnswers[question.id] && multipleAnswers[question.id].length > 0
  }
  return answers[question.id] !== undefined && answers[question.id] !== ''
}

const getTypeText = (type) => {
  const typeMap = {
    single: '单选题',
    multiple: '多选题',
    judge: '判断题',
    fill: '填空题'
  }
  return typeMap[type] || type
}

const getTypeColor = (type) => {
  const colorMap = {
    single: 'primary',
    multiple: 'success',
    judge: 'warning',
    fill: 'info'
  }
  return colorMap[type] || ''
}

const formatTime = (seconds) => {
  if (seconds <= 0) {
    return '00:00'
  }
  const minutes = Math.floor(seconds / 60)
  const secs = seconds % 60
  return `${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
}

const loadExamInfo = async () => {
  loading.value = true
  try {
    const res = await getExamDetail(examId)
    examInfo.value = res.data
  } catch (error) {
    console.error(error)
  } finally {
    loading.value = false
  }
}

const handleStartExam = async () => {
  starting.value = true
  try {
    const res = await startExam(examId)
    examRecordId.value = res.data.id
    await loadQuestions(res.data.start_time, res.data.duration)
    // 只有成功加载题目后才开始考试
    if (questions.value.length > 0) {
      examStarted.value = true
      startTimer()
      ElMessage.success('考试开始，请认真答题')
    } else {
      ElMessage.error('试卷题目加载失败')
    }
  } catch (error) {
    console.error(error)
    ElMessage.error('开始考试失败')
  } finally {
    starting.value = false
  }
}

const loadQuestions = async (startTime, duration) => {
  try {
    const res = await getExamQuestions(examId)
    questions.value = res.data.questions || []

    // 如果返回了考试记录ID，更新它
    if (res.data.exam_record_id) {
      examRecordId.value = res.data.exam_record_id
    }

    // 为每个多选题初始化空数组（确保响应式）
    questions.value.forEach(q => {
      if (q.type === 'multiple' && !multipleAnswers[q.id]) {
        multipleAnswers[q.id] = []
      }
    })

    // 加载已保存的答案
    const savedAnswers = res.data.saved_answers || {}
    Object.keys(savedAnswers).forEach(questionId => {
      const question = questions.value.find(q => q.id == questionId)
      if (question) {
        if (question.type === 'multiple') {
          // 多选题：将逗号分隔的答案转换为数组
          multipleAnswers[questionId] = savedAnswers[questionId].split(',')
        } else {
          // 其他题型：直接赋值
          answers[questionId] = savedAnswers[questionId]
        }
      }
    })

    // 从服务器获取剩余时间
    if (examRecordId.value) {
      try {
        const timeRes = await checkExamTime(examRecordId.value)
        if (timeRes.data) {
          remainingTime.value = timeRes.data.remaining_time
          if (remainingTime.value <= 0) {
            handleSubmit(true)
            return
          }
        }
      } catch (error) {
        console.error('获取服务器时间失败:', error)
        // 降级方案：使用本地计算
        if (startTime && duration) {
          const start = new Date(startTime).getTime()
          const now = Date.now()
          const elapsedSeconds = Math.floor((now - start) / 1000)
          const totalSeconds = duration * 60
          remainingTime.value = Math.max(0, totalSeconds - elapsedSeconds)
          if (remainingTime.value <= 0) {
            handleSubmit(true)
          }
        }
      }
    }
  } catch (error) {
    console.error(error)
  }
}

const startTimer = () => {
  // 每10秒从服务器同步一次时间
  timer.value = setInterval(async () => {
    // 定期从服务器获取剩余时间
    try {
      const res = await checkExamTime(examRecordId.value)
      if (res.data && res.data.is_expired) {
        // 服务器判断已超时，强制提交
        clearInterval(timer.value)
        handleSubmit(true)
        return
      }

      // 使用服务器返回的剩余时间
      remainingTime.value = res.data.remaining_time

      // 如果剩余时间<=0，强制提交
      if (remainingTime.value <= 0) {
        clearInterval(timer.value)
        handleSubmit(true)
      }
    } catch (error) {
      console.error('获取服务器时间失败:', error)
      // 如果获取服务器时间失败，使用本地计时作为降级方案
      remainingTime.value--
      if (remainingTime.value <= 0) {
        clearInterval(timer.value)
        handleSubmit(true)
      }
    }
  }, 10000)  // 每10秒同步一次
}

// 防抖保存答案
let saveTimer = null
const autoSaveAnswer = () => {
  if (saveTimer) {
    clearTimeout(saveTimer)
  }
  saveTimer = setTimeout(() => {
    saveCurrentAnswer()
  }, 200) // 200ms防抖
}

const saveCurrentAnswer = async () => {
  const questionId = currentQuestion.value.id
  let answer = answers[questionId]

  // 处理多选题答案
  if (currentQuestion.value.type === 'multiple') {
    answer = (multipleAnswers[questionId] || []).sort().join(',')
  }

  if (!answer) return

  try {
    await saveAnswer({
      exam_record_id: examRecordId.value,
      question_id: questionId,
      user_answer: answer
    })
  } catch (error) {
    console.error('保存答案失败:', error)
  }
}

const handleSubmit = async (autoSubmit = false) => {
  // 如果不是自动提交，显示确认框
  if (!autoSubmit) {
    try {
      await ElMessageBox.confirm('确定要提交试卷吗？提交后无法修改！', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      })
    } catch (error) {
      if (error === 'cancel') {
        return
      }
    }
  }

  submitting.value = true
  clearInterval(timer.value)

  try {
    // 先保存当前答案
    await saveCurrentAnswer()

    // 提交试卷
    await submitExam(examRecordId.value)

    if (autoSubmit) {
      ElMessage.success('考试时间已到，试卷已自动提交')
    } else {
      ElMessage.success('试卷提交成功')
    }

    router.push(`/exam-record/${examRecordId.value}`)
  } catch (error) {
    console.error(error)
    ElMessage.error('提交失败，请重试')
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  loadExamInfo()
})

onUnmounted(() => {
  if (timer.value) {
    clearInterval(timer.value)
  }
})
</script>

<style scoped>
.exam-take-container {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.exam-info {
  padding: 20px;
}

.exam-info h2 {
  margin-bottom: 10px;
  color: #303133;
}

.exam-info p {
  margin-bottom: 20px;
  color: #606266;
}

.start-btn {
  margin-top: 30px;
  text-align: center;
}

.exam-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.exam-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 20px;
  background: #fff;
  border-radius: 4px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.exam-title {
  font-size: 18px;
  font-weight: bold;
  color: #303133;
}

.exam-timer {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 16px;
  color: #F56C6C;
  font-weight: bold;
}

.question-nav {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  padding: 15px;
  background: #fff;
  border-radius: 4px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.nav-item {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid #DCDFE6;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s;
}

.nav-item:hover {
  border-color: #409EFF;
  color: #409EFF;
}

.nav-item.active {
  background: #409EFF;
  color: #fff;
  border-color: #409EFF;
}

.nav-item.answered {
  background: #67C23A;
  color: #fff;
  border-color: #67C23A;
}

.question-card {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.question-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 20px;
}

.question-score {
  color: #909399;
}

.question-content {
  font-size: 16px;
  line-height: 1.8;
  margin-bottom: 20px;
  color: #303133;
}

.options {
  margin: 20px 0;
}

.options .el-radio,
.options .el-checkbox {
  display: flex;
  align-items: center;
  margin: 18px 0;
  padding: 12px 16px;
  border-radius: 6px;
  white-space: normal;
  transition: background-color 0.2s;
}

.options .el-radio:hover,
.options .el-checkbox:hover {
  background-color: #f5f7fa;
}

/* 确保单选和多选框组件内部样式正确 */
.options :deep(.el-radio__label),
.options :deep(.el-checkbox__label) {
  line-height: 1.6;
  padding-left: 8px;
}

.action-buttons {
  margin-top: 30px;
  display: flex;
  justify-content: center;
  gap: 20px;
}
</style>