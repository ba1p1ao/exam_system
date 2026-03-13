<template>
  <div class="questions-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>题库管理</span>
          <div class="header-actions">
            <el-button type="success" @click="handleExport">
              <el-icon><Download /></el-icon>
              导出题目
            </el-button>
            <el-button type="primary" @click="handleAdd">
              <el-icon><Plus /></el-icon>
              添加题目
            </el-button>
            <el-button type="warning" @click="handleImport">
              <el-icon><Upload /></el-icon>
              批量导入
            </el-button>
          </div>
        </div>
      </template>

      <!-- 搜索表单 -->
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="题目名称">
          <el-input v-model="searchForm.content" placeholder="请输入题目名称" clearable style="width: 200px" />
        </el-form-item>
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
        <el-form-item label="难度">
          <el-select v-model="searchForm.difficulty" placeholder="请选择" clearable style="width: 150px">
            <el-option label="简单" value="easy" />
            <el-option label="中等" value="medium" />
            <el-option label="困难" value="hard" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">搜索</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>

      <!-- 题目列表 -->
      <el-table
        :data="tableData"
        v-loading="loading"
        border
        style="width: 100%"
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="type" label="题型" width="100">
          <template #default="{ row }">
            <el-tag :type="getTypeColor(row.type)">{{ getTypeText(row.type) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="category" label="分类" width="120" />
        <el-table-column prop="content" label="题目内容" show-overflow-tooltip />
        <el-table-column prop="difficulty" label="难度" width="80">
          <template #default="{ row }">
            <el-tag :type="getDifficultyColor(row.difficulty)">{{ getDifficultyText(row.difficulty) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="score" label="分值" width="80" />
        <el-table-column prop="create_time" label="创建时间" width="180" />
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="handleEdit(row)">编辑</el-button>
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

      <!-- 批量操作 -->
      <div class="batch-actions" v-if="selectedRows.length > 0">
        <el-button type="danger" @click="handleBatchDelete">批量删除</el-button>
      </div>
    </el-card>

    <!-- 导入对话框 -->
    <QuestionImportDialog 
      v-model="importDialogVisible" 
      @success="handleImportSuccess"
    />
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onActivated, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Download, Upload } from '@element-plus/icons-vue'
import { getQuestionList, deleteQuestion, batchDeleteQuestions } from '@/api/question'
import { exportQuestions } from '@/api/import-export'
import QuestionImportDialog from '@/components/QuestionImportDialog.vue'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()
const userInfo = computed(() => userStore.userInfo || {})


const importDialogVisible = ref(false)

const loading = ref(false)
const tableData = ref([])
const selectedRows = ref([])

const searchForm = reactive({
  content: '',
  type: '',
  category: '',
  difficulty: ''
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

const getDifficultyText = (difficulty) => {
  const difficultyMap = {
    easy: '简单',
    medium: '中等',
    hard: '困难'
  }
  return difficultyMap[difficulty] || difficulty
}

const getDifficultyColor = (difficulty) => {
  const colorMap = {
    easy: 'success',
    medium: 'warning',
    hard: 'danger'
  }
  return colorMap[difficulty] || ''
}

const loadData = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      size: pagination.size,
      ...searchForm
    }
    const res = await getQuestionList(params)
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
  searchForm.content = ''
  searchForm.type = ''
  searchForm.category = ''
  searchForm.difficulty = ''
  handleSearch()
}

const handleAdd = () => {
  router.push('/questions/add')
}

const handleImport = () => {
  importDialogVisible.value = true
}

const handleExport = async () => {
  if (selectedRows.value.length === 0) {
    ElMessage.warning('请先选择要导出的题目')
    return
  }

  try {
    const ids = selectedRows.value.map(item => item.id)
    const res = await exportQuestions({ ids })
    const blob = new Blob([res], { 
      type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' 
    })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `题目导出_${new Date().getTime()}.xlsx`
    link.click()
    window.URL.revokeObjectURL(url)
    ElMessage.success('导出成功')
  } catch (error) {
    console.error(error)
    ElMessage.error('导出失败')
  }
}

const handleImportSuccess = () => {
  loadData()
}

const handleEdit = (row) => {
  router.push(`/questions/edit/${row.id}`)
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm('确定要删除该题目吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await deleteQuestion(row.id)
    ElMessage.success('删除成功')
    loadData()
  } catch (error) {
    if (error !== 'cancel') {
      console.error(error)
    }
  }
}

const handleSelectionChange = (selection) => {
  selectedRows.value = selection
}

const handleBatchDelete = async () => {
  try {
    await ElMessageBox.confirm(`确定要删除选中的 ${selectedRows.value.length} 道题目吗？`, '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    const ids = selectedRows.value.map(item => item.id)
    await batchDeleteQuestions(ids)
    ElMessage.success('批量删除成功')
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
  // 等待用户信息加载完成后再检查权限
  const checkPermission = () => {
    if (userInfo.value.role && !['teacher', 'admin'].includes(userInfo.value.role)) {
      ElMessage.error('您没有权限访问此页面')
      router.push('/home')
      return false
    }
    return true
  }

  // 如果用户信息已加载，立即检查
  if (userInfo.value.role) {
    if (checkPermission()) {
      loadData()
    }
  } else {
    // 否则等待用户信息加载
    const unwatch = watch(userInfo, (newVal) => {
      if (newVal.role) {
        unwatch()
        if (checkPermission()) {
          loadData()
        }
      }
    })
  }
})

onActivated(() => {
  loadData()
})
</script>

<style scoped>
.questions-container {
  height: 100%;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.search-form {
  margin-bottom: 20px;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.batch-actions {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #ebeef5;
}
</style>