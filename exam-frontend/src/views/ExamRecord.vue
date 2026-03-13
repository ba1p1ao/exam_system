<template>
  <div class="exam-record-container">
    <el-card v-loading="loading">
      <template #header>
        <div class="card-header">
          <span>考试结果</span>
          <el-button @click="$router.back()">返回</el-button>
        </div>
      </template>

      <div v-if="record">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="试卷标题">{{ examInfo.title }}</el-descriptions-item>
          <el-descriptions-item label="考试状态">
            <el-tag :type="getStatusColor(record.status)">{{ getStatusText(record.status) }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="得分">
            <span :style="{ color: record.is_passed ? '#67C23A' : '#F56C6C', fontSize: '20px', fontWeight: 'bold' }">
              {{ record.score }} 分
            </span>
          </el-descriptions-item>
          <el-descriptions-item label="是否及格">
            <el-tag :type="record.is_passed ? 'success' : 'danger'">
              {{ record.is_passed ? '及格' : '不及格' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="开始时间">{{ record.start_time }}</el-descriptions-item>
          <el-descriptions-item label="提交时间">{{ record.submit_time }}</el-descriptions-item>
        </el-descriptions>

        <el-divider>答题详情</el-divider>

        <div class="answers-list">
          <el-card
            v-for="(answer, index) in answers"
            :key="answer.id"
            class="answer-item"
            shadow="hover"
          >
            <div class="answer-header">
              <span class="question-index">第 {{ index + 1 }} 题</span>
              <el-tag :type="getTypeColor(answer.question.type)">
                {{ getTypeText(answer.question.type) }}
              </el-tag>
              <span class="question-score">{{ answer.question.score }}分</span>
              <el-tag :type="answer.is_correct ? 'success' : 'danger'">
                {{ answer.is_correct ? '正确' : '错误' }}
              </el-tag>
              <span class="answer-score">得分：{{ answer.score || 0 }} 分</span>
            </div>
            <div class="answer-content">
              <div class="question-text">{{ answer.question.content }}</div>

              <!-- 选项 -->
              <div v-if="answer.question.options" class="options">
                <div
                  v-for="(option, key) in answer.question.options"
                  :key="key"
                  class="option-item"
                  :class="{
                    'correct': isCorrectOption(answer, key),
                    'user-selected': isUserSelected(answer, key)
                  }"
                >
                  {{ key }}. {{ option }}
                </div>
              </div>

              <!-- 用户答案 -->
              <div class="user-answer">
                <span class="label">你的答案：</span>
                <span :class="{ correct: answer.is_correct, wrong: !answer.is_correct }">
                  {{ formatAnswer(answer.user_answer, answer.question.type, answer.question) }}
                </span>
              </div>

              <!-- 正确答案 -->
              <div class="correct-answer">
                <span class="label">正确答案：</span>
                <span class="correct-text">{{ formatAnswer(answer.question.answer, answer.question.type, answer.question) }}</span>
              </div>

              <!-- 解析 -->
              <div v-if="answer.question.analysis" class="analysis">
                <span class="label">解析：</span>
                <span>{{ answer.question.analysis }}</span>
              </div>
            </div>
          </el-card>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { getExamRecordDetail } from '@/api/exam'

const route = useRoute()

const loading = ref(false)
const record = ref(null)
const examInfo = ref({})
const answers = ref([])

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
  return colorMap[status] || ''
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

const isCorrectOption = (answer, key) => {
  const correctAnswers = answer.question.answer.split(',')
  return correctAnswers.includes(key)
}

const isUserSelected = (answer, key) => {
  const userAnswers = (answer.user_answer || '').split(',')
  return userAnswers.includes(key)
}

const formatAnswer = (answer, type, question) => {
  if (!answer) return '未作答'
  if (type === 'judge' && question && question.options) {
    // 判断题：返回选项对应的文字描述
    return question.options[answer] || answer
  }
  return answer
}

const loadRecordDetail = async () => {
  loading.value = true
  try {
    const res = await getExamRecordDetail(route.params.id)
    record.value = res.data
    examInfo.value = res.data.exam
    answers.value = res.data.answers || []
  } catch (error) {
    console.error(error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadRecordDetail()
})
</script>

<style scoped>
.exam-record-container {
  height: 100%;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.answers-list {
  margin-top: 20px;
}

.answer-item {
  margin-bottom: 20px;
}

.answer-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 15px;
  padding-bottom: 10px;
  border-bottom: 1px solid #ebeef5;
}

.question-index {
  font-weight: bold;
  color: #303133;
}

.question-score {
  color: #909399;
  font-size: 14px;
}

.answer-score {
  margin-left: auto;
  color: #303133;
  font-weight: bold;
}

.answer-content {
  padding: 10px 0;
}

.question-text {
  font-size: 16px;
  line-height: 1.8;
  margin-bottom: 15px;
  color: #303133;
}

.options {
  margin: 15px 0;
}

.option-item {
  padding: 8px 12px;
  margin: 8px 0;
  border-radius: 4px;
  background: #f5f7fa;
}

.option-item.correct {
  background: #f0f9ff;
  border: 1px solid #67C23A;
}

.option-item.user-selected {
  background: #ecf5ff;
  border: 1px solid #409EFF;
}

.user-answer,
.correct-answer,
.analysis {
  margin: 10px 0;
  padding: 10px;
  background: #f5f7fa;
  border-radius: 4px;
}

.label {
  font-weight: bold;
  color: #606266;
  margin-right: 8px;
}

.user-answer .correct {
  color: #67C23A;
  font-weight: bold;
}

.user-answer .wrong {
  color: #F56C6C;
  font-weight: bold;
}

.correct-text {
  color: #67C23A;
  font-weight: bold;
}
</style>