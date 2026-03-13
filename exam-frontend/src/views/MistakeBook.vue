<template>
  <div class="mistake-book-container">
    <el-row :gutter="20">
      <!-- 左侧：错题统计 -->
      <el-col :span="4">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>错题统计</span>
            </div>
          </template>
          <div class="statistics">
            <div class="stat-item">
              <div class="stat-value">{{ statistics.total_mistakes }}</div>
              <div class="stat-label">错题总数</div>
            </div>
            <div class="stat-item">
              <div class="stat-value">{{ statistics.unique_questions }}</div>
              <div class="stat-label">错题数量</div>
            </div>
          </div>
          
          <el-divider />
          
          <div class="chart-section">
            <div class="chart-title">题型分布</div>
            <div class="type-distribution">
              <div class="type-item" v-for="(count, type) in statistics.type_distribution" :key="type">
                <span class="type-name">{{ getTypeText(type) }}</span>
                <el-progress :percentage="getPercentage(count, statistics.total_mistakes)" :color="getTypeColor(type)" />
                <span class="type-count">{{ count }}题</span>
              </div>
            </div>
          </div>
          
          <el-divider />
          
          <div class="chart-section">
            <div class="chart-title">科目分布</div>
            <div class="category-distribution">
              <div class="category-item" v-for="(count, category) in statistics.category_distribution" :key="category">
                <span class="category-name">{{ category }}</span>
                <el-progress :percentage="getPercentage(count, statistics.total_mistakes)" />
                <span class="category-count">{{ count }}题</span>
              </div>
            </div>
          </div>
          
          <el-button type="primary" style="width: 100%; margin-top: 20px" @click="handleExport">
            <el-icon><Download /></el-icon>
            导出错题本
          </el-button>
        </el-card>
      </el-col>
      
      <!-- 右侧：错题列表 -->
      <el-col :span="20">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>我的错题</span>
              <el-button type="primary" size="small" @click="handlePractice">
                <el-icon><Edit /></el-icon>
                开始练习
              </el-button>
            </div>
          </template>
          
          <!-- 搜索表单 -->
          <el-form :inline="true" :model="searchForm" class="search-form">
            <el-form-item label="题目类型">
              <el-select v-model="searchForm.type" placeholder="请选择" clearable style="width: 150px">
                <el-option label="单选题" value="single" />
                <el-option label="多选题" value="multiple" />
                <el-option label="判断题" value="judge" />
                <el-option label="填空题" value="fill" />
              </el-select>
            </el-form-item>
            <el-form-item label="题目分类">
              <el-select v-model="searchForm.category" placeholder="请选择" clearable filterable style="width: 150px">
                <el-option label="数学" value="数学" />
                <el-option label="语文" value="语文" />
                <el-option label="英语" value="英语" />
                <el-option label="物理" value="物理" />
                <el-option label="化学" value="化学" />
                <el-option label="生物" value="生物" />
                <el-option label="历史" value="历史" />
                <el-option label="地理" value="地理" />
                <el-option label="政治" value="政治" />
                <el-option label="常识" value="常识" />
                <el-option label="音乐" value="音乐" />
                <el-option label="计算机" value="计算机" />
              </el-select>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="handleSearch">搜索</el-button>
              <el-button @click="handleReset">重置</el-button>
            </el-form-item>
          </el-form>
          
          <!-- 错题列表 -->
          <div class="mistake-list">
            <el-empty v-if="tableData.length === 0" description="暂无错题" />
            <div v-else class="mistake-item" v-for="item in tableData" :key="item.id">
              <div class="mistake-header">
                <el-tag :type="getTypeColor(item.type)">{{ getTypeText(item.type) }}</el-tag>
                <span class="mistake-category">{{ item.category }}</span>
                <el-tag type="danger">错误{{ item.mistake_count }}次</el-tag>
                <span class="mistake-time">{{ item.last_mistake_time }}</span>
              </div>
              <div class="mistake-content">
                <div class="question-text">{{ item.content }}</div>
                <div v-if="item.options" class="question-options">
                  <div v-for="(option, key) in item.options" :key="key" class="option-item">
                    <span class="option-key">{{ key }}.</span>
                    <span class="option-value">{{ option }}</span>
                  </div>
                </div>
              </div>
              <div class="mistake-answer">
                <div class="answer-item">
                  <span class="answer-label">你的答案：</span>
                  <span class="answer-value wrong">{{ item.user_answer }}</span>
                </div>
                <div class="answer-item">
                  <span class="answer-label">正确答案：</span>
                  <span class="answer-value correct">{{ item.correct_answer }}</span>
                </div>
              </div>
              <div v-if="item.analysis" class="mistake-analysis">
                <div class="analysis-label">解析：</div>
                <div class="analysis-content">{{ item.analysis }}</div>
              </div>
              <div class="mistake-footer">
                <span class="mistake-source">来源：{{ item.exam_title }}</span>
                <el-button type="success" size="small" @click="handleMarkMastered(item)">
                  <el-icon><Check /></el-icon>
                  标记为已掌握
                </el-button>
              </div>
            </div>
          </div>
          
          <!-- 分页 -->
          <div class="pagination-container">
            <el-pagination
              v-model:current-page="pagination.page"
              v-model:page-size="pagination.size"
              :page-sizes="[10, 20, 50]"
              :total="pagination.total"
              layout="total, sizes, prev, pager, next, jumper"
              @size-change="handleSizeChange"
              @current-change="handleCurrentChange"
            />
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useUserStore } from '@/stores/user'
import { getMistakeListWithStatistics, markMistakeAsMastered, exportMistakeQuestions } from '@/api/mistake'

const userStore = useUserStore()
const userInfo = computed(() => userStore.userInfo || {})
const router = useRouter()

const loading = ref(false)
const tableData = ref([])
const statistics = ref({
  total_mistakes: 0,
  unique_questions: 0,
  type_distribution: {},
  category_distribution: {}
})

const searchForm = reactive({
  type: '',
  category: ''
})

const pagination = reactive({
  page: 1,
  size: 10,
  total: 0
})

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

const getPercentage = (value, total) => {
  if (!total || total === 0) return 0
  return Math.round((value / total) * 100)
}

const loadData = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      size: pagination.size,
      ...searchForm
    }
    const res = await getMistakeListWithStatistics(params)
    
    // 处理列表数据
    tableData.value = res.data.list || []
    pagination.total = res.data.total || 0
    
    // 处理统计数据
    statistics.value = res.data.statistics || {
      total_mistakes: 0,
      unique_questions: 0,
      type_distribution: {},
      category_distribution: {},
      recent_mistakes: []
    }
  } catch (error) {
    // console.error(error)
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  pagination.page = 1
  loadData()
}

const handleReset = () => {
  searchForm.type = ''
  searchForm.category = ''
  handleSearch()
}

const handleMarkMastered = async (item) => {
  try {
    await ElMessageBox.confirm('确定要标记这道错题为已掌握吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'success'
    })
    
    await markMistakeAsMastered(item.id)
    ElMessage.success('标记成功')
    loadData()
  } catch (error) {
    if (error !== 'cancel') {
      // console.error(error)
    }
  }
}

const handleExport = async () => {
  try {
    const res = await exportMistakeQuestions()

    // 检查响应是否是有效的 Excel 文件
    if (res.type === 'application/json') {
      const reader = new FileReader()
      reader.onload = (e) => {
        try {
          const errorData = JSON.parse(e.target.result)
          ElMessage.error(errorData.message || '导出失败')
        } catch (parseError) {
          ElMessage.error('导出失败：无法解析错误信息')
        }
      }
      reader.onerror = () => {
        ElMessage.error('导出失败：读取响应数据出错')
      }
      reader.readAsText(res)
      return
    }

    // 检查是否为有效的文件类型
    if (res.size === 0) {
      ElMessage.error('导出失败：返回的文件为空')
      return
    }

    if (res.type === 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' ||
        res.type === 'application/octet-stream') {
      const blob = new Blob([res], { type: res.type })
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = `错题本_${new Date().getTime()}.xlsx`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)
      ElMessage.success('导出成功')
    } else {
      ElMessage.error(`导出失败：不支持的文件类型 ${res.type}`)
    }
  } catch (error) {
    // console.error('导出错题本失败:', error)
    ElMessage.error(error.message || '导出失败，请稍后重试')
  }
}

const handlePractice = () => {
  ElMessage.info('练习功能开发中...')
}

const handleSizeChange = (val) => {
  pagination.size = val
  loadData()
}

const handleCurrentChange = (val) => {
  pagination.page = val
  loadData()
}

onMounted(() => {
  // 检查是否为学生
  if (userInfo.value.role !== 'student') {
    ElMessage.error('此页面仅供学生使用')
    router.push('/home')
    return
  }
  loadData()
})
</script>

<style scoped>
.mistake-book-container {
  height: 100%;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.statistics {
  padding: 20px 0;
}

.stat-item {
  text-align: center;
  margin-bottom: 20px;
}

.stat-value {
  font-size: 36px;
  font-weight: bold;
  color: #409EFF;
  margin-bottom: 8px;
}

.stat-label {
  font-size: 14px;
  color: #909399;
}

.chart-section {
  margin-bottom: 20px;
}

.chart-title {
  font-size: 16px;
  font-weight: bold;
  color: #303133;
  margin-bottom: 15px;
}

.type-distribution,
.category-distribution {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.type-item,
.category-item {
  display: flex;
  align-items: center;
  gap: 10px;
}

.type-name,
.category-name {
  width: 60px;
  font-size: 14px;
  color: #606266;
}

.type-count,
.category-count {
  width: 50px;
  text-align: right;
  font-size: 14px;
  color: #909399;
}

.search-form {
  margin-bottom: 20px;
}

.mistake-list {
  max-height: 600px;
  overflow-y: auto;
}

.mistake-item {
  border: 1px solid #EBEEF5;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 20px;
  background: #fff;
  transition: all 0.3s;
}

.mistake-item:hover {
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.mistake-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 15px;
}

.mistake-category {
  font-size: 14px;
  color: #909399;
}

.mistake-time {
  margin-left: auto;
  font-size: 12px;
  color: #C0C4CC;
}

.mistake-content {
  margin-bottom: 15px;
}

.question-text {
  font-size: 16px;
  line-height: 1.8;
  color: #303133;
  margin-bottom: 15px;
}

.question-options {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-left: 20px;
}

.option-item {
  display: flex;
  align-items: flex-start;
  gap: 8px;
}

.option-key {
  font-weight: bold;
  color: #606266;
}

.option-value {
  flex: 1;
  color: #303133;
}

.mistake-answer {
  display: flex;
  gap: 30px;
  padding: 15px;
  background: #F5F7FA;
  border-radius: 4px;
  margin-bottom: 15px;
}

.answer-item {
  display: flex;
  align-items: center;
  gap: 10px;
}

.answer-label {
  font-weight: bold;
  color: #606266;
}

.answer-value {
  font-size: 16px;
  font-weight: bold;
}

.answer-value.wrong {
  color: #F56C6C;
}

.answer-value.correct {
  color: #67C23A;
}

.mistake-analysis {
  padding: 15px;
  background: #ECF5FF;
  border-left: 4px solid #409EFF;
  border-radius: 4px;
  margin-bottom: 15px;
}

.analysis-label {
  font-weight: bold;
  color: #409EFF;
  margin-bottom: 8px;
}

.analysis-content {
  color: #606266;
  line-height: 1.8;
}

.mistake-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.mistake-source {
  font-size: 14px;
  color: #909399;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style>