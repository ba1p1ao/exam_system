<template>
  <div class="ranking-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>成绩排名</span>
          <el-radio-group v-model="viewMode" size="small" v-if="userInfo.role === 'student'">
            <el-radio-button value="exam">考试排名</el-radio-button>
            <el-radio-button value="trend">成绩趋势</el-radio-button>
          </el-radio-group>
        </div>
      </template>
      
      <!-- 考试排名视图 -->
      <div v-if="viewMode === 'exam'">
        <el-form :inline="true" :model="searchForm" class="search-form">
          <el-form-item label="选择考试">
            <el-select
              v-model="searchForm.exam_id"
              placeholder="请选择考试"
              filterable
              style="width: 250px"
              @change="handleExamChange"
            >
              <el-option
                v-for="exam in examList"
                :key="exam.id"
                :label="exam.title"
                :value="exam.id"
              />
            </el-select>
          </el-form-item>
          <el-form-item label="选择班级" v-if="userInfo.role !== 'student'">
            <el-select
              v-model="searchForm.class_id"
              placeholder="请选择班级"
              clearable
              filterable
              style="width: 200px"
              @change="handleClassChange"
            >
              <el-option
                v-for="cls in classList"
                :key="cls.id"
                :label="cls.name"
                :value="cls.id"
              />
            </el-select>
          </el-form-item>
        </el-form>
        
        <div v-if="!searchForm.exam_id" class="empty-tip">
          <el-empty description="请选择考试查看排名" />
        </div>
        
        <div v-else>
          <!-- 我的排名（仅学生显示） -->
          <div v-if="userInfo.role === 'student'" class="my-ranking-card">
            <div class="ranking-badge">
              <el-icon :size="40" :color="getRankingColor(rankingData.my_rank)">
                <Medal />
              </el-icon>
            </div>
            <div class="ranking-info">
              <div class="rank-number">第 {{ rankingData.my_rank || '-' }} 名</div>
              <div class="rank-score">{{ rankingData.my_score || '-' }} 分</div>
              <div class="rank-detail">
                共 {{ rankingData.total_participants }} 人参加
              </div>
            </div>
          </div>

          <!-- 考试统计（教师/管理员显示） -->
          <div v-else class="my-ranking-card">
            <div class="ranking-badge">
              <el-icon :size="40" color="#fff">
                <Medal />
              </el-icon>
            </div>
            <div class="ranking-info">
              <div class="rank-number">考试统计</div>
              <div class="rank-score">{{ rankingData.total_participants }} 人</div>
              <div class="rank-detail">
                参加本次考试
              </div>
            </div>
          </div>
          
          <!-- 排名列表 -->
          <div class="ranking-list">
            <div
              v-for="(item, index) in rankingData.list"
              :key="item.user_id"
              class="ranking-item"
              :class="{ 'my-rank': userInfo.role === 'student' && item.user_id === currentUserId }"
            >
              <div class="rank-number" :class="`rank-${index + 1}`">
                {{ index + 1 }}
              </div>
              <div class="user-info">
                <el-avatar :size="40">{{ item.nickname?.charAt(0) || item.username?.charAt(0) }}</el-avatar>
                <div class="user-detail">
                  <div class="user-name">{{ item.nickname || item.username }}</div>
                  <div class="submit-time">提交时间：{{ item.submit_time }}</div>
                </div>
              </div>
              <div class="score-info">
                <div class="score" :class="{ passed: item.is_passed }">
                  {{ item.score }} 分
                </div>
                <el-tag :type="item.is_passed ? 'success' : 'danger'" size="small">
                  {{ item.is_passed ? '及格' : '不及格' }}
                </el-tag>
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
        </div>
      </div>
      
      <!-- 成绩趋势视图 -->
      <div v-else>
        <el-form :inline="true" class="search-form">
          <el-form-item label="统计天数" style="width: 180px;">
            <el-select v-model="trendDays" placeholder="请选择" @change="loadTrendData">
              <el-option label="最近7天" :value="7" />
              <el-option label="最近15天" :value="15" />
              <el-option label="最近30天" :value="30" />
              <el-option label="最近60天" :value="60" />
              <el-option label="最近90天" :value="90" />
            </el-select>
          </el-form-item>
        </el-form>
        
        <div class="trend-summary">
          <el-row :gutter="20">
            <el-col :span="6">
              <div class="summary-item">
                <div class="summary-value">{{ trendData.total_exams }}</div>
                <div class="summary-label">考试次数</div>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="summary-item">
                <div class="summary-value">{{ trendData.average_score }}</div>
                <div class="summary-label">平均分</div>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="summary-item">
                <div class="summary-value">{{ trendData.highest_score }}</div>
                <div class="summary-label">最高分</div>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="summary-item">
                <div class="summary-value">{{ (trendData.pass_rate * 100).toFixed(0) }}%</div>
                <div class="summary-label">及格率</div>
              </div>
            </el-col>
          </el-row>
        </div>
        
        <div class="trend-chart">
          <div class="chart-title">成绩趋势图</div>
          <ScoreTrendChart ref="trendChartRef" :days="trendDays" />
        </div>
        
        <div class="trend-list">
          <div class="list-title">历史成绩</div>
          <el-table :data="trendData.trend" border>
            <el-table-column prop="date" label="考试日期" width="180" />
            <el-table-column prop="exam_title" label="考试名称" />
            <el-table-column prop="score" label="得分" width="100">
              <template #default="{ row }">
                <span :style="{ color: row.score >= 60 ? '#67C23A' : '#F56C6C', fontWeight: 'bold' }">
                  {{ row.score }}
                </span>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { Medal } from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'
import { getAvailableExamList, getExamRecordList, getExamList } from '@/api/exam'
import { getExamRanking } from '@/api/ranking'
import { getStudentScoreTrend } from '@/api/ranking'
import { getClassOptions } from '@/api/class'
import ScoreTrendChart from '@/components/ScoreTrendChart.vue'

const userStore = useUserStore()
const currentUserId = computed(() => userStore.userInfo?.id)
const userInfo = computed(() => userStore.userInfo || {})

const viewMode = ref('exam')
const loading = ref(false)
const examList = ref([])
const classList = ref([])
const trendDays = ref(30)
const trendChartRef = ref(null)

const searchForm = reactive({
  exam_id: null,
  class_id: null
})

const rankingData = ref({
  exam_id: null,
  exam_title: '',
  total_participants: 0,
  my_rank: 0,
  my_score: 0,
  list: []
})

const trendData = ref({
  total_exams: 0,
  average_score: 0,
  highest_score: 0,
  lowest_score: 0,
  pass_rate: 0,
  trend: []
})

const pagination = reactive({
  page: 1,
  size: 10,
  total: 0
})

const getRankingColor = (rank) => {
  if (rank === 1) return '#FFD700'
  if (rank === 2) return '#C0C0C0'
  if (rank === 3) return '#CD7F32'
  return '#909399'
}

const loadExamList = async () => {
  try {
    if (userInfo.value.role === 'student') {
      // 学生：获取已参加的考试记录
      const recordRes = await getExamRecordList({ page: 1, size: 1000 })
      const takenExamIds = new Set()
      const takenExams = []

      if (recordRes.data && recordRes.data.list) {
        recordRes.data.list.forEach(record => {
          if (!takenExamIds.has(record.exam_id)) {
            takenExamIds.add(record.exam_id)
            takenExams.push({
              id: record.exam_id,
              title: record.exam_title
            })
          }
        })
      }

      examList.value = takenExams
    } else {
      // 教师/管理员：获取所有已发布的考试
      const res = await getExamList({ page: 1, size: 1000, status: 'published' })
      examList.value = res.data.list || []
    }
  } catch (error) {
    console.error(error)
  }
}

const loadRankingData = async () => {
  if (!searchForm.exam_id) return

  loading.value = true
  try {
    const params = {
      page: pagination.page,
      size: pagination.size
    }
    if (searchForm.class_id) {
      params.class_id = searchForm.class_id
    }
    const res = await getExamRanking(searchForm.exam_id, params)
    rankingData.value = res.data
    pagination.total = res.data.total || 0
  } catch (error) {
    console.error(error)
  } finally {
    loading.value = false
  }
}

const loadTrendData = async () => {
  try {
    const res = await getStudentScoreTrend({ days: trendDays.value })
    if (res.data) {
      trendData.value = res.data
      // 创建新数组进行排序，不修改原数据
      if (trendData.value.trend && trendData.value.trend.length > 0) {
        trendData.value.trend = [...trendData.value.trend].sort((a, b) => {
          return new Date(b.date) - new Date(a.date)
        })
      }
      if (trendChartRef.value) {
        trendChartRef.value.refresh()
      }
    }
  } catch (error) {
    console.error('加载成绩趋势数据失败:', error)
  }
}

const handleExamChange = () => {
  pagination.page = 1
  loadRankingData()
}

const handleClassChange = () => {
  pagination.page = 1
  loadRankingData()
}

const loadClassList = async () => {
  // 只有教师和管理员才需要加载班级列表
  if (userInfo.value.role === 'student') {
    return
  }
  try {
    const res = await getClassOptions()
    classList.value = res.data || []
  } catch (error) {
    console.error(error)
  }
}

const handleSizeChange = (val) => {
  pagination.size = val
  loadRankingData()
}

const handleCurrentChange = (val) => {
  pagination.page = val
  loadRankingData()
}

onMounted(() => {
  loadExamList()
  loadClassList()
  // 只有学生才加载成绩趋势数据
  if (userInfo.value.role === 'student') {
    loadTrendData()
  }
})
</script>

<style scoped>
.ranking-container {
  height: 100%;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.search-form {
  margin-bottom: 20px;
}

.empty-tip {
  padding: 40px 0;
}

.my-ranking-card {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 30px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
  margin-bottom: 30px;
  color: #fff;
}

.ranking-badge {
  width: 80px;
  height: 80px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.ranking-info {
  flex: 1;
}

.rank-number {
  font-size: 32px;
  font-weight: bold;
  margin-bottom: 8px;
}

.rank-score {
  font-size: 48px;
  font-weight: bold;
  margin-bottom: 8px;
}

.rank-detail {
  font-size: 14px;
  opacity: 0.9;
}

.ranking-list {
  margin-bottom: 20px;
}

.ranking-item {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 20px;
  background: #fff;
  border: 1px solid #EBEEF5;
  border-radius: 8px;
  margin-bottom: 15px;
  transition: all 0.3s;
}

.ranking-item:hover {
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.ranking-item.my-rank {
  border: 2px solid #409EFF;
  background: #ECF5FF;
}

.ranking-item .rank-number {
  width: 50px;
  height: 50px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  font-weight: bold;
  background: #F5F7FA;
  border-radius: 50%;
  color: #909399;
}

.ranking-item .rank-number.rank-1 {
  background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%);
  color: #fff;
}

.ranking-item .rank-number.rank-2 {
  background: linear-gradient(135deg, #C0C0C0 0%, #A0A0A0 100%);
  color: #fff;
}

.ranking-item .rank-number.rank-3 {
  background: linear-gradient(135deg, #CD7F32 0%, #A0522D 100%);
  color: #fff;
}

.user-info {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 15px;
}

.user-detail {
  flex: 1;
}

.user-name {
  font-size: 16px;
  font-weight: bold;
  color: #303133;
  margin-bottom: 5px;
}

.submit-time {
  font-size: 12px;
  color: #C0C4CC;
}

.score-info {
  display: flex;
  align-items: center;
  gap: 15px;
}

.score {
  font-size: 28px;
  font-weight: bold;
  color: #F56C6C;
}

.score.passed {
  color: #67C23A;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.trend-summary {
  margin-bottom: 30px;
}

.summary-item {
  padding: 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 8px;
  text-align: center;
  color: #fff;
}

.summary-value {
  font-size: 36px;
  font-weight: bold;
  margin-bottom: 8px;
}

.summary-label {
  font-size: 14px;
  opacity: 0.9;
}

.trend-chart {
  margin-bottom: 30px;
}

.chart-title {
  font-size: 18px;
  font-weight: bold;
  color: #303133;
  margin-bottom: 20px;
}

.trend-list {
  margin-top: 30px;
}

.list-title {
  font-size: 18px;
  font-weight: bold;
  color: #303133;
  margin-bottom: 15px;
}
</style>