<template>
  <el-dialog
    v-model="dialogVisible"
    :title="dialogTitle"
    width="800px"
    @close="handleClose"
  >
    <el-tabs v-model="activeTab">
      <!-- 成员列表 -->
      <el-tab-pane label="班级成员" name="members">
        <div class="member-header">
          <el-form :inline="true" :model="searchForm">
            <el-form-item label="角色">
              <el-select v-model="searchForm.role" @change="loadMembers" style="width: 100px;">
                <el-option label="全部" value="" />
                <el-option label="学生" value="student" />
                <el-option label="教师" value="teacher" />
              </el-select>
            </el-form-item>
          </el-form>
          <el-button type="primary" @click="showAddDialog">添加成员</el-button>
        </div>

        <el-table :data="memberList" border v-loading="loading">
          <el-table-column type="index" label="序号" width="60" />
          <el-table-column prop="username" label="用户名" width="120" />
          <el-table-column prop="nickname" label="昵称" width="120" />
          <el-table-column prop="role" label="角色" width="100">
            <template #default="{ row }">
              <el-tag :type="row.role === 'student' ? 'success' : 'warning'" size="small">
                {{ row.role === 'student' ? '学生' : '教师' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="status" label="状态" width="80">
            <template #default="{ row }">
              <el-tag :type="row.status === 1 ? 'success' : 'danger'" size="small">
                {{ row.status === 1 ? '正常' : '禁用' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="join_time" label="加入时间" width="180" />
          <el-table-column label="操作" width="100" fixed="right">
            <template #default="{ row }">
              <el-button
                type="danger"
                size="small"
                link
                @click="handleRemoveMember(row)"
              >
                移除
              </el-button>
            </template>
          </el-table-column>
        </el-table>

        <div class="pagination-container">
          <el-pagination
            v-model:current-page="pagination.page"
            v-model:page-size="pagination.size"
            :page-sizes="[10, 20, 50]"
            :total="pagination.total"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="loadMembers"
            @current-change="loadMembers"
          />
        </div>
      </el-tab-pane>

      <!-- 班级统计 -->
      <el-tab-pane label="班级统计" name="statistics">
        <div v-loading="statisticsLoading" class="statistics-container">
          <el-row :gutter="20">
            <el-col :span="6">
              <div class="stat-card">
                <div class="stat-value">{{ statistics.student_count }}</div>
                <div class="stat-label">学生人数</div>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="stat-card">
                <div class="stat-value">{{ statistics.exam_count }}</div>
                <div class="stat-label">考试次数</div>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="stat-card">
                <div class="stat-value">{{ statistics.average_score }}</div>
                <div class="stat-label">平均分</div>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="stat-card">
                <div class="stat-value">{{ (statistics.pass_rate * 100).toFixed(0) }}%</div>
                <div class="stat-label">及格率</div>
              </div>
            </el-col>
          </el-row>

          <div class="score-distribution">
            <div class="section-title">成绩分布</div>
            <el-row :gutter="20">
              <el-col :span="4" v-for="(count, range) in statistics.score_distribution" :key="range">
                <div class="distribution-item">
                  <div class="range">{{ range }}分</div>
                  <div class="count">{{ count }}人</div>
                </div>
              </el-col>
            </el-row>
          </div>

          <!-- 班级考试排名 -->
          <div class="class-exam-ranking">
            <div class="section-title">班级考试排名</div>
            <el-form :inline="true">
              <el-form-item label="选择考试">
                <el-select
                  v-model="selectedExamId"
                  placeholder="请选择考试"
                  clearable
                  style="width: 250px"
                  @change="loadClassExamRanking"
                >
                  <el-option
                    v-for="exam in examList"
                    :key="exam.id"
                    :label="exam.title"
                    :value="exam.id"
                  />
                </el-select>
              </el-form-item>
            </el-form>
            <el-table :data="classExamRanking" v-loading="rankingLoading" border>
              <el-table-column type="index" label="排名" width="80" />
              <el-table-column prop="username" label="用户名" width="120" />
              <el-table-column prop="nickname" label="昵称" width="120" />
              <el-table-column prop="score" label="得分" width="100">
                <template #default="{ row }">
                  <span :style="{ color: row.is_passed ? '#67C23A' : '#F56C6C', fontWeight: 'bold' }">
                    {{ row.score }}
                  </span>
                </template>
              </el-table-column>
              <el-table-column prop="is_passed" label="是否及格" width="100">
                <template #default="{ row }">
                  <el-tag :type="row.is_passed ? 'success' : 'danger'" size="small">
                    {{ row.is_passed ? '及格' : '不及格' }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="submit_time" label="提交时间" width="180" />
            </el-table>
          </div>

          <!-- 班级成绩趋势 -->
          <div class="class-score-trend">
            <div class="section-title">班级成绩趋势</div>
            <el-form :inline="true">
              <el-form-item label="统计天数">
                <el-select v-model="trendDays" placeholder="请选择" @change="loadClassScoreTrend" style="width: 120px">
                  <el-option label="最近7天" :value="7" />
                  <el-option label="最近15天" :value="15" />
                  <el-option label="最近30天" :value="30" />
                  <el-option label="最近60天" :value="60" />
                  <el-option label="最近90天" :value="90" />
                </el-select>
              </el-form-item>
            </el-form>
            <div ref="classTrendChartRef" style="height: 400px"></div>
          </div>
        </div>
      </el-tab-pane>
    </el-tabs>

    <!-- 添加成员对话框 -->
    <el-dialog
      v-model="addDialogVisible"
      title="添加成员"
      width="600px"
      append-to-body
    >
      <el-form :inline="true">
        <el-form-item>
          <el-input
            v-model="searchKeyword"
            placeholder="搜索用户名或昵称"
            clearable
            @input="loadAvailableStudents"
          />
        </el-form-item>
      </el-form>
      <el-table
        :data="availableStudents"
        border
        max-height="400"
        @selection-change="handleSelectionChange"
        v-loading="availableLoading"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column prop="username" label="用户名" width="120" />
        <el-table-column prop="nickname" label="昵称" width="120" />
        <el-table-column prop="role" label="角色" width="100">
          <template #default="{ row }">
            <el-tag :type="row.role === 'student' ? 'success' : 'warning'" size="small">
              {{ row.role === 'student' ? '学生' : '教师' }}
            </el-tag>
          </template>
        </el-table-column>
      </el-table>
      <template #footer>
        <el-button @click="addDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleAddMembers" :loading="addLoading">
          确定 ({{ selectedStudents.length }})
        </el-button>
      </template>
    </el-dialog>

    <template #footer>
      <el-button @click="handleClose">关闭</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, reactive, watch, computed, nextTick, onUnmounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  getClassMembers,
  addClassMembers,
  removeClassMembers,
  getAvailableStudents,
  getClassStatistics,
  getClassExamRanking,
  getClassScoreTrend
} from '@/api/class'
import { getAvailableExamList, getExamList } from '@/api/exam'
import * as echarts from 'echarts'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  classId: {
    type: Number,
    required: true
  },
  className: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['update:modelValue', 'refresh'])

const dialogVisible = ref(false)
const activeTab = ref('members')
const loading = ref(false)
const statisticsLoading = ref(false)
const availableLoading = ref(false)
const addLoading = ref(false)
const rankingLoading = ref(false)
const trendLoading = ref(false)

const searchForm = reactive({
  role: ''
})

const pagination = reactive({
  page: 1,
  size: 10,
  total: 0
})

const memberList = ref([])
const statistics = ref({
  student_count: 0,
  exam_count: 0,
  average_score: 0,
  highest_score: 0,
  lowest_score: 0,
  pass_rate: 0,
  excellent_rate: 0,
  score_distribution: {}
})

const addDialogVisible = ref(false)
const searchKeyword = ref('')
const availableStudents = ref([])
const selectedStudents = ref([])

// 班级考试排名相关
const examList = ref([])
const selectedExamId = ref(null)
const classExamRanking = ref([])

// 班级成绩趋势相关
const trendDays = ref(30)
const classTrendChartRef = ref(null)
let classTrendChart = null

const loadMembers = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      size: pagination.size,
      role: searchForm.role || undefined
    }
    const res = await getClassMembers(props.classId, params)
    memberList.value = res.data.list || []
    pagination.total = res.data.total || 0
  } catch (error) {
    console.error(error)
  } finally {
    loading.value = false
  }
}

const loadStatistics = async () => {
  statisticsLoading.value = true
  try {
    const res = await getClassStatistics(props.classId)
    statistics.value = res.data
  } catch (error) {
    console.error(error)
  } finally {
    statisticsLoading.value = false
  }
}

const loadExamList = async () => {
  try {
    const res = await getExamList({ page: 1, size: 1000, status: 'published' })
    examList.value = res.data.list || []
  } catch (error) {
    console.error(error)
  }
}

const loadClassExamRanking = async () => {
  if (!selectedExamId.value) {
    classExamRanking.value = []
    return
  }
  
  rankingLoading.value = true
  try {
    const res = await getClassExamRanking(props.classId, {
      exam_id: selectedExamId.value,
      page: 1,
      size: 100
    })
    classExamRanking.value = res.data.list || []
  } catch (error) {
    console.error(error)
    ElMessage.error('加载班级考试排名失败')
  } finally {
    rankingLoading.value = false
  }
}

const loadClassScoreTrend = async () => {
  trendLoading.value = true
  try {
    const res = await getClassScoreTrend(props.classId, {
      days: trendDays.value
    })
    const data = res.data
    renderClassTrendChart(data)
  } catch (error) {
    console.error(error)
    ElMessage.error('加载班级成绩趋势失败')
  } finally {
    trendLoading.value = false
  }
}

const renderClassTrendChart = (data) => {
  if (!classTrendChartRef.value) return
  
  classTrendChart = echarts.init(classTrendChartRef.value)
  
  const option = {
    title: {
      text: '班级成绩趋势',
      left: 'center'
    },
    tooltip: {
      trigger: 'axis'
    },
    legend: {
      data: ['平均分', '及格率'],
      top: 30
    },
    xAxis: {
      type: 'category',
      data: data.trend?.map(t => t.date) || [],
      axisLabel: {
        rotate: 45
      }
    },
    yAxis: [
      {
        type: 'value',
        name: '分数',
        min: 0,
        max: 100,
        position: 'left'
      },
      {
        type: 'value',
        name: '及格率',
        min: 0,
        max: 100,
        position: 'right',
        axisLabel: {
          formatter: '{value}%'
        }
      }
    ],
    series: [
      {
        name: '平均分',
        type: 'line',
        yAxisIndex: 0,
        data: data.trend?.map(t => t.average_score) || [],
        smooth: true,
        itemStyle: {
          color: '#409EFF'
        }
      },
      {
        name: '及格率',
        type: 'line',
        yAxisIndex: 1,
        data: data.trend?.map(t => (t.pass_rate * 100).toFixed(1)) || [],
        smooth: true,
        itemStyle: {
          color: '#67C23A'
        }
      }
    ]
  }
  
  classTrendChart.setOption(option)
}

const loadAvailableStudents = async () => {
  availableLoading.value = true
  try {
    const params = {}
    if (searchKeyword.value) {
      params.keyword = searchKeyword.value
    }
    const res = await getAvailableStudents(props.classId, params)
    availableStudents.value = res.data || []
  } catch (error) {
    console.error(error)
  } finally {
    availableLoading.value = false
  }
}

const showAddDialog = () => {
  addDialogVisible.value = true
  searchKeyword.value = ''
  selectedStudents.value = []
  loadAvailableStudents()
}

const handleSelectionChange = (selection) => {
  selectedStudents.value = selection
}

const handleAddMembers = async () => {
  if (selectedStudents.value.length === 0) {
    ElMessage.warning('请选择要添加的成员')
    return
  }

  addLoading.value = true
  try {
    const user_ids = selectedStudents.value.map(item => item.id)
    const res = await addClassMembers(props.classId, { user_ids })
    ElMessage.success(`成功添加 ${res.data.success_count} 人`)
    addDialogVisible.value = false
    loadMembers()
    emit('refresh')
  } catch (error) {
    console.error(error)
  } finally {
    addLoading.value = false
  }
}

const handleRemoveMember = async (row) => {
  try {
    await ElMessageBox.confirm(
      `确定要移除成员 ${row.nickname || row.username} 吗？`,
      '提示',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    const res = await removeClassMembers(props.classId, { user_ids: [row.id] })
    ElMessage.success('移除成功')
    loadMembers()
    emit('refresh')
  } catch (error) {
    if (error !== 'cancel') {
      console.error(error)
    }
  }
}

const handleClose = () => {
  dialogVisible.value = false
}

watch(
  () => props.modelValue,
  (val) => {
    dialogVisible.value = val
    if (val) {
      loadMembers()
      loadStatistics()
      loadExamList()
    }
  },
  { immediate: true }
)

watch(dialogVisible, (val) => {
  emit('update:modelValue', val)
})

onUnmounted(() => {
  if (classTrendChart) {
    classTrendChart.dispose()
  }
})
</script>

<style scoped>
.member-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.statistics-container {
  padding: 20px 0;
}

.stat-card {
  padding: 30px 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 8px;
  text-align: center;
  color: #fff;
  margin-bottom: 20px;
}

.stat-value {
  font-size: 36px;
  font-weight: bold;
  margin-bottom: 8px;
}

.stat-label {
  font-size: 14px;
  opacity: 0.9;
}

.score-distribution {
  margin-top: 30px;
}

.section-title {
  font-size: 18px;
  font-weight: bold;
  color: #303133;
  margin-bottom: 20px;
}

.distribution-item {
  padding: 20px;
  background: #f5f7fa;
  border-radius: 8px;
  text-align: center;
}

.range {
  font-size: 16px;
  font-weight: bold;
  color: #606266;
  margin-bottom: 10px;
}

.count {
  font-size: 24px;
  font-weight: bold;
  color: #409eff;
}
</style>