<template>
  <div class="records-container">
    <el-card>
      <template #header>
        <div class="header-container">
          <span>考试记录</span>
          <div class="view-switch" v-if="isTeacherOrAdmin">
            <el-radio-group v-model="viewMode" size="small">
              <el-radio-button value="grouped">按考试分组</el-radio-button>
              <el-radio-button value="list">列表视图</el-radio-button>
            </el-radio-group>
          </div>
        </div>
      </template> 
      
      <!-- 搜索表单 -->
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="试卷标题">
          <el-input v-model="searchForm.title" placeholder="请输入标题" clearable />
        </el-form-item>
        <el-form-item label="考试状态" v-if="viewMode === 'list' || !isTeacherOrAdmin">
          <el-select v-model="searchForm.status" placeholder="请选择" clearable style="width: 100px">
            <el-option label="未开始" value="not_started" />
            <el-option label="进行中" value="in_progress" />
            <el-option label="已提交" value="submitted" />
            <el-option label="已阅卷" value="graded" />
          </el-select>
        </el-form-item>
        <el-form-item label="考试状态" v-if="viewMode === 'grouped' && isTeacherOrAdmin">
          <el-select v-model="searchForm.exam_status" placeholder="请选择" clearable style="width: 100px">
            <el-option label="草稿" value="draft" />
            <el-option label="已发布" value="published" />
            <el-option label="已关闭" value="closed" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">搜索</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>

      <!-- 按考试分组的视图（管理员/老师） -->
      <div v-if="viewMode === 'grouped' && isTeacherOrAdmin">
        <el-table :data="groupedTableData" v-loading="loading" border style="width: 100%">
          <el-table-column prop="id" label="试卷ID" width="70" />
          <el-table-column prop="title" label="试卷标题" show-overflow-tooltip min-width="150" />
          <el-table-column prop="description" label="试卷描述" show-overflow-tooltip min-width="150" />
          <el-table-column prop="total_score" label="总分" width="70">
            <template #default="{ row }">{{ row.total_score }} 分</template>
          </el-table-column>
          <el-table-column prop="pass_score" label="及格分" width="70">
            <template #default="{ row }">{{ row.pass_score }} 分</template>
          </el-table-column>
          <el-table-column prop="duration" label="时长" width="90">
            <template #default="{ row }">{{ row.duration }} 分钟</template>
          </el-table-column>
          <el-table-column prop="participant_count" label="参加人数" width="90">
            <template #default="{ row }">{{ row.participant_count || 0 }} 人</template>
          </el-table-column>
          <el-table-column prop="average_score" label="平均分" width="90">
            <template #default="{ row }">
              <span v-if="row.average_score !== null">{{ row.average_score.toFixed(1) }} 分</span>
              <span v-else>-</span>
            </template>
          </el-table-column>
          <el-table-column prop="pass_rate" label="及格率" width="90">
            <template #default="{ row }">
              <span v-if="row.pass_rate !== null">{{ (row.pass_rate * 100).toFixed(1) }}%</span>
              <span v-else>-</span>
            </template>
          </el-table-column>
          <el-table-column prop="status" label="状态" width="80">
            <template #default="{ row }">
              <el-tag :type="getExamStatusColor(row.status)">{{ getExamStatusText(row.status) }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="start_time" label="开始时间" width="180" />
          <el-table-column prop="end_time" label="结束时间" width="180" />
          <el-table-column label="操作" width="100" fixed="right">
            <template #default="{ row }">
              <el-button type="primary" size="small" @click="handleViewExam(row)">查看</el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <!-- 列表视图（学生或管理员/老师的列表模式） -->
      <div v-else>
        <el-table :data="tableData" v-loading="loading" border style="width: 100%">
          <el-table-column type="expand">
            <template #default="{ row }">
              <div class="expand-content">
                <el-descriptions :column="2" border>
                  <el-descriptions-item label="试卷标题">{{ row.exam_title }}</el-descriptions-item>
                  <el-descriptions-item label="总分">{{ row.exam_total_score || '-' }} 分</el-descriptions-item>
                  <el-descriptions-item label="及格分数">{{ row.exam_pass_score || '-' }} 分</el-descriptions-item>
                  <el-descriptions-item label="考试时长">{{ row.exam_duration || '-' }} 分钟</el-descriptions-item>
                  <el-descriptions-item label="得分">
                    <span v-if="row.score !== null" :style="{ color: row.is_passed ? '#67C23A' : '#F56C6C', fontWeight: 'bold' }">
                      {{ row.score }} 分
                    </span>
                    <span v-else>-</span>
                  </el-descriptions-item>
                  <el-descriptions-item label="得分率">
                    <span v-if="row.score !== null && row.exam_total_score">
                      {{ ((row.score / row.exam_total_score) * 100).toFixed(1) }}%
                    </span>
                    <span v-else>-</span>
                  </el-descriptions-item>
                  <el-descriptions-item label="是否及格">
                    <el-tag v-if="row.is_passed !== null" :type="row.is_passed ? 'success' : 'danger'">
                      {{ row.is_passed ? '及格' : '不及格' }}
                    </el-tag>
                    <span v-else>-</span>
                  </el-descriptions-item>
                  <el-descriptions-item label="考试用时">
                    <span v-if="row.start_time && row.submit_time">
                      {{ calculateDuration(row.start_time, row.submit_time) }}
                    </span>
                    <span v-else>-</span>
                  </el-descriptions-item>
                </el-descriptions>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="id" label="记录ID" width="100" />
          <el-table-column prop="exam_title" label="试卷标题" show-overflow-tooltip min-width="150" />
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
              <span v-if="row.score !== null && row.exam_total_score">
                {{ ((row.score / row.exam_total_score) * 100).toFixed(1) }}%
              </span>
              <span v-else>-</span>
            </template>
          </el-table-column>
          <el-table-column prop="is_passed" label="是否及格" width="100">
            <template #default="{ row }">
              <el-tag v-if="row.is_passed !== null" :type="row.is_passed ? 'success' : 'danger'">
                {{ row.is_passed ? '及格' : '不及格' }}
              </el-tag>
              <span v-else>-</span>
            </template>
          </el-table-column>
          <el-table-column prop="status" label="状态" width="100">
            <template #default="{ row }">
              <el-tag :type="getStatusColor(row.status)">{{ getStatusText(row.status) }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="start_time" label="开始时间" width="180" />
          <el-table-column prop="submit_time" label="提交时间" width="180" />
          <el-table-column label="操作" width="120" fixed="right">
            <template #default="{ row }">
              <el-button type="primary" size="small" @click="handleView(row)">查看</el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <!-- 分页 -->
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.size"
          :page-sizes="[10, 20, 50, 100]"
          :total="pagination.total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { getExamRecordList, getGroupedExamRecords, getExamStatistics } from '@/api/exam'

const router = useRouter()
const userStore = useUserStore()

const loading = ref(false)
const tableData = ref([])
const groupedTableData = ref([])

// 判断用户是否为老师或管理员
const isTeacherOrAdmin = computed(() => {
  const role = userStore.userInfo?.role
  return role === 'teacher' || role === 'admin'
})

// 视图模式：grouped（按考试分组）或 list（列表视图）
const viewMode = ref(isTeacherOrAdmin.value ? 'grouped' : 'list')

const searchForm = reactive({
  title: '',
  status: '',
  exam_status: ''
})

const pagination = reactive({
  page: 1,
  size: 10,
  total: 0
})

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
  return colorMap[status] || ''
}

const calculateDuration = (startTime, endTime) => {
  if (!startTime || !endTime) return '-'
  const start = new Date(startTime)
  const end = new Date(endTime)
  const diff = Math.floor((end - start) / 1000) // 秒
  const hours = Math.floor(diff / 3600)
  const minutes = Math.floor((diff % 3600) / 60)
  const seconds = diff % 60
  
  if (hours > 0) {
    return `${hours}小时${minutes}分钟${seconds}秒`
  } else if (minutes > 0) {
    return `${minutes}分钟${seconds}秒`
  } else {
    return `${seconds}秒`
  }
}

// 加载数据（根据视图模式选择不同的API）
const loadData = async () => {
  loading.value = true
  try {
    if (viewMode.value === 'grouped' && isTeacherOrAdmin.value) {
      await loadGroupedData()
    } else {
      await loadListData()
    }
  } catch (error) {
    console.error('加载数据失败:', error)
  } finally {
    loading.value = false
  }
}

// 加载列表数据（原有逻辑）
const loadListData = async () => {
  const params = {
    page: pagination.page,
    size: pagination.size,
    title: searchForm.title,
    status: searchForm.status
  }
  // 如果是学生，不需要传递额外的过滤条件，后端会自动过滤
  const res = await getExamRecordList(params)
  tableData.value = res.data.list || []
  pagination.total = res.data.total || 0
}

// 加载分组数据（新功能）
const loadGroupedData = async () => {
  const params = {
    page: pagination.page,
    size: pagination.size,
    title: searchForm.title,
    status: searchForm.exam_status
  }
  const res = await getGroupedExamRecords(params)
  groupedTableData.value = res.data.list || []
  pagination.total = res.data.total || 0
}

const handleSearch = () => {
  pagination.page = 1
  loadData()
}

const handleReset = () => {
  searchForm.title = ''
  searchForm.status = ''
  searchForm.exam_status = ''
  handleSearch()
}

// 查看单个考试记录（学生或列表视图）
const handleView = (row) => {
  router.push(`/exam-record/${row.id}`)
}

// 查看学生考试记录详情（分组视图）
const handleViewStudentRecord = (studentRecord) => {
  router.push(`/exam-record/${studentRecord.id}`)
}

// 查看试卷详情（分组视图）- 跳转到考试详情页面
const handleViewExam = (exam) => {
  router.push(`/exams/detail/${exam.id}`)
}

const handleSizeChange = (val) => {
  pagination.size = val
  loadData()
}

const handleCurrentChange = (val) => {
  pagination.page = val
  loadData()
}

// 视图模式切换时重新加载数据
const handleViewModeChange = () => {
  pagination.page = 1
  loadData()
}

// 添加 watch 监听 viewMode 变化
watch(viewMode, () => {
  handleViewModeChange()
})

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.records-container {
  height: 100%;
}

.header-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.view-switch {
  margin-left: 20px;
}

.search-form {
  margin-bottom: 20px;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.expand-content {
  padding: 20px;
}

:deep(.el-descriptions__label) {
  font-weight: 600;
  background: #f5f7fa;
}
</style>