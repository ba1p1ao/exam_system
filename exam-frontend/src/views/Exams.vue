<template>
  <div class="exams-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>试卷管理</span>
          <el-button type="primary" @click="handleAdd">
            <el-icon><Plus /></el-icon>
            创建试卷
          </el-button>
        </div>
      </template>

      <!-- 搜索表单 -->
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="试卷标题">
          <el-input v-model="searchForm.title" placeholder="请输入标题" clearable style="width: 250px" />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="searchForm.status" placeholder="请选择" clearable style="width: 100px">
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

      <!-- 试卷列表 -->
      <el-table :data="tableData" v-loading="loading" border style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="title" label="试卷标题" show-overflow-tooltip />
        <el-table-column prop="duration" label="时长(分钟)" width="100" />
        <el-table-column prop="total_score" label="总分" width="80" />
        <el-table-column prop="pass_score" label="及格分" width="80" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusColor(row.status)">{{ getStatusText(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="start_time" label="开始时间" width="180" />
        <el-table-column prop="end_time" label="结束时间" width="180" />
        <el-table-column label="操作" width="280" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="handleEdit(row)">编辑</el-button>
            <el-button
              v-if="row.status === 'draft'"
              type="success"
              size="small"
              @click="handlePublish(row)"
            >
              发布
            </el-button>
            <el-button
              v-if="row.status === 'published'"
              type="warning"
              size="small"
              @click="handleClose(row)"
            >
              关闭
            </el-button>
            <el-button type="danger" size="small" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

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
import { ref, reactive, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useUserStore } from '@/stores/user'
import {
  getExamList,
  deleteExam,
  publishExam,
  closeExam
} from '@/api/exam'

const userStore = useUserStore()
const userInfo = computed(() => userStore.userInfo || {})
const router = useRouter()

const loading = ref(false)
const tableData = ref([])

const searchForm = reactive({
  title: '',
  status: ''
})

const pagination = reactive({
  page: 1,
  size: 10,
  total: 0
})

const getStatusText = (status) => {
  const statusMap = {
    draft: '草稿',
    published: '已发布',
    closed: '已关闭'
  }
  return statusMap[status] || status
}

const getStatusColor = (status) => {
  const colorMap = {
    draft: 'info',
    published: 'success',
    closed: 'danger'
  }
  return colorMap[status] || ''
}

const loadData = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      size: pagination.size,
      ...searchForm
    }
    const res = await getExamList(params)
    tableData.value = res.data.list || []
    pagination.total = res.data.total || 0
  } catch (error) {
    console.error(error)
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  pagination.page = 1
  loadData()
}

const handleReset = () => {
  searchForm.title = ''
  searchForm.status = ''
  handleSearch()
}

const handleAdd = () => {
  console.log('点击创建试卷按钮')
  console.log('当前用户角色:', userInfo.value?.role)
  router.push('/exams/add')
}

const handleEdit = (row) => {
  router.push(`/exams/edit/${row.id}`)
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm('确定要删除该试卷吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await deleteExam(row.id)
    ElMessage.success('删除成功')
    loadData()
  } catch (error) {
    if (error !== 'cancel') {
      console.error(error)
    }
  }
}

const handlePublish = async (row) => {
  try {
    await ElMessageBox.confirm('确定要发布该试卷吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await publishExam(row.id)
    ElMessage.success('发布成功')
    loadData()
  } catch (error) {
    if (error !== 'cancel') {
      console.error(error)
    }
  }
}

const handleClose = async (row) => {
  try {
    await ElMessageBox.confirm('确定要关闭该试卷吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await closeExam(row.id)
    ElMessage.success('关闭成功')
    loadData()
  } catch (error) {
    if (error !== 'cancel') {
      console.error(error)
    }
  }
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
  // 检查是否为教师或管理员
  const userRole = userInfo.value?.role
  if (!userRole || !['teacher', 'admin'].includes(userRole)) {
    ElMessage.error('您没有权限访问此页面')
    router.push('/home')
    return
  }
  loadData()
})
</script>

<style scoped>
.exams-container {
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

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style>