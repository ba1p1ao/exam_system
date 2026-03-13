<template>
  <div class="users-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>用户管理</span>
          <div class="statistics">
            <el-tag type="info">总用户: {{ statistics.total_users }}</el-tag>
            <el-tag type="success">学生: {{ statistics.student_count }}</el-tag>
            <el-tag type="warning">教师: {{ statistics.teacher_count }}</el-tag>
            <el-tag type="danger">管理员: {{ statistics.admin_count }}</el-tag>
          </div>
        </div>
      </template>

      <!-- 搜索表单 -->
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="用户名">
          <el-input v-model="searchForm.username" placeholder="请输入用户名" clearable style="width: 200px" />
        </el-form-item>
        <el-form-item label="昵称">
          <el-input v-model="searchForm.nickname" placeholder="请输入昵称" clearable style="width: 200px" />
        </el-form-item>
        <el-form-item label="角色">
          <el-select v-model="searchForm.role" placeholder="请选择" clearable style="width: 120px">
            <el-option label="学生" value="student" />
            <el-option label="教师" value="teacher" />
            <el-option label="管理员" value="admin" />
          </el-select>
        </el-form-item>
        <el-form-item label="班级">
          <el-select v-model="searchForm.class_id" placeholder="请选择班级" clearable style="width: 150px" filterable>
            <el-option
              v-for="cls in classList"
              :key="cls.id"
              :label="cls.name"
              :value="cls.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="searchForm.status" placeholder="请选择" clearable style="width: 120px">
            <el-option label="正常" :value="1" />
            <el-option label="禁用" :value="0" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">搜索</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>

      <!-- 用户列表 -->
      <el-table :data="tableData" v-loading="loading" border style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="username" label="用户名" width="150" />
        <el-table-column prop="nickname" label="昵称" width="150" />
        <el-table-column prop="role" label="角色" width="100">
          <template #default="{ row }">
            <el-tag :type="getRoleColor(row.role)">{{ getRoleText(row.role) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="class_name" label="班级" width="150">
          <template #default="{ row }">
            <el-tag v-if="row.class_name" type="info">{{ row.class_name }}</el-tag>
            <span v-else style="color: #909399">-</span>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 1 ? 'success' : 'danger'">
              {{ row.status === 1 ? '正常' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="create_time" label="注册时间" width="180" />
        <el-table-column label="操作" width="320" fixed="right">
          <template #default="{ row }">
            <div class="action-buttons">
              <el-button type="primary" size="small" @click="handleViewDetail(row)">详情</el-button>
              <el-button 
                :type="row.status === 1 ? 'warning' : 'success'" 
                size="small" 
                @click="handleToggleStatus(row)"
              >
                {{ row.status === 1 ? '禁用' : '启用' }}
              </el-button>
              <el-dropdown @command="(cmd) => handleRoleCommand(cmd, row)">
                <el-button type="info" size="small">
                  角色<el-icon class="el-icon--right"><arrow-down /></el-icon>
                </el-button>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item command="student">设为学生</el-dropdown-item>
                    <el-dropdown-item command="teacher">设为教师</el-dropdown-item>
                    <el-dropdown-item command="admin">设为管理员</el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
              <el-button type="danger" size="small" @click="handleDelete(row)">删除</el-button>
            </div>
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

    <!-- 用户详情对话框 -->
    <el-dialog v-model="detailDialogVisible" title="用户详情" width="600px">
      <el-descriptions v-if="currentUser" :column="2" border>
        <el-descriptions-item label="用户ID">{{ currentUser.id }}</el-descriptions-item>
        <el-descriptions-item label="用户名">{{ currentUser.username }}</el-descriptions-item>
        <el-descriptions-item label="昵称">{{ currentUser.nickname }}</el-descriptions-item>
        <el-descriptions-item label="角色">
          <el-tag :type="getRoleColor(currentUser.role)">{{ getRoleText(currentUser.role) }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="currentUser.status === 1 ? 'success' : 'danger'">
            {{ currentUser.status === 1 ? '正常' : '禁用' }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="注册时间">{{ currentUser.create_time }}</el-descriptions-item>
        <el-descriptions-item label="创建试卷数">{{ currentUser.exam_count || 0 }}</el-descriptions-item>
        <el-descriptions-item label="创建题目数">{{ currentUser.question_count || 0 }}</el-descriptions-item>
        <el-descriptions-item label="考试记录数">{{ currentUser.record_count || 0 }}</el-descriptions-item>
      </el-descriptions>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useUserStore } from '@/stores/user'
import {
  getUserList,
  getUserDetail,
  updateUserStatus,
  updateUserRole,
  deleteUser,
  getUserStatistics
} from '@/api/admin'
import { getClassOptions } from '@/api/class'

const userStore = useUserStore()
const userInfo = computed(() => userStore.userInfo || {})

// 检查是否为管理员
if (userInfo.value.role !== 'admin') {
  ElMessage.error('您没有权限访问此页面')
  router.push('/home')
}

const loading = ref(false)
const tableData = ref([])
const classList = ref([])
const statistics = ref({
  total_users: 0,
  student_count: 0,
  teacher_count: 0,
  admin_count: 0,
  active_users: 0,
  disabled_users: 0
})
const detailDialogVisible = ref(false)
const currentUser = ref(null)

const searchForm = reactive({
  username: '',
  nickname: '',
  role: '',
  class_id: '',
  status: ''
})

const pagination = reactive({
  page: 1,
  size: 10,
  total: 0
})

const getRoleText = (role) => {
  const roleMap = {
    student: '学生',
    teacher: '教师',
    admin: '管理员'
  }
  return roleMap[role] || role
}

const getRoleColor = (role) => {
  const colorMap = {
    student: 'success',
    teacher: 'warning',
    admin: 'danger'
  }
  return colorMap[role] || ''
}

const loadData = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      size: pagination.size,
      ...searchForm
    }
    const res = await getUserList(params)
    tableData.value = res.data.list || []
    pagination.total = res.data.total || 0
  } catch (error) {
    console.error(error)
  } finally {
    loading.value = false
  }
}

const loadStatistics = async () => {
  try {
    const res = await getUserStatistics()
    statistics.value = res.data
  } catch (error) {
    console.error(error)
  }
}

const handleSearch = () => {
  pagination.page = 1
  loadData()
}

const handleReset = () => {
  searchForm.username = ''
  searchForm.nickname = ''
  searchForm.role = ''
  searchForm.class_id = ''
  searchForm.status = ''
  handleSearch()
}

const loadClassList = async () => {
  try {
    const res = await getClassOptions()
    classList.value = res.data || []
  } catch (error) {
    console.error(error)
  }
}

const handleViewDetail = async (row) => {
  try {
    const res = await getUserDetail(row.id)
    currentUser.value = res.data
    detailDialogVisible.value = true
  } catch (error) {
    console.error(error)
  }
}

const handleToggleStatus = async (row) => {
  const newStatus = row.status === 1 ? 0 : 1
  const action = newStatus === 1 ? '启用' : '禁用'
  
  try {
    await ElMessageBox.confirm(`确定要${action}用户"${row.username}"吗？`, '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await updateUserStatus(row.id, { status: newStatus })
    ElMessage.success(`${action}成功`)
    loadData()
    loadStatistics()
  } catch (error) {
    if (error !== 'cancel') {
      console.error(error)
    }
  }
}

const handleRoleCommand = async (command, row) => {
  const roleText = getRoleText(command)
  
  try {
    await ElMessageBox.confirm(`确定要将用户"${row.username}"的角色设置为"${roleText}"吗？`, '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await updateUserRole(row.id, { role: command })
    ElMessage.success('角色设置成功')
    loadData()
    loadStatistics()
  } catch (error) {
    if (error !== 'cancel') {
      console.error(error)
    }
  }
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(`确定要删除用户"${row.username}"吗？删除后无法恢复！`, '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await deleteUser(row.id)
    ElMessage.success('删除成功')
    loadData()
    loadStatistics()
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
  // 检查是否为管理员
  if (userInfo.value.role !== 'admin') {
    ElMessage.error('您没有权限访问此页面')
    router.push('/home')
    return
  }
  loadData()
  loadStatistics()
  loadClassList()
})
</script>

<style scoped>
.users-container {
  height: 100%;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.statistics {
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

.action-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
  align-items: center;
}

.action-buttons .el-button {
  margin: 0;
}
</style>