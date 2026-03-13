<template>
  <div class="class-management-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>班级管理</span>
          <el-button type="primary" @click="handleCreate" v-if="userInfo.role === 'admin'">
            创建班级
          </el-button>
        </div>
      </template>

      <!-- 搜索表单 -->
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="班级名称">
          <el-input
            v-model="searchForm.name"
            placeholder="请输入班级名称"
            clearable
            style="width: 200px"
          />
        </el-form-item>
        <el-form-item label="年级">
          <el-select
            v-model="searchForm.grade"
            placeholder="请选择年级"
            clearable
            style="width: 150px"
          >
            <el-option label="一年级" value="一年级" />
            <el-option label="二年级" value="二年级" />
            <el-option label="三年级" value="三年级" />
            <el-option label="四年级" value="四年级" />
            <el-option label="五年级" value="五年级" />
            <el-option label="六年级" value="六年级" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select
            v-model="searchForm.status"
            placeholder="请选择状态"
            clearable
            style="width: 120px"
          >
            <el-option label="正常" :value="1" />
            <el-option label="禁用" :value="0" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadClassList">查询</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>

      <!-- 班级列表 -->
      <el-table :data="classList" border v-loading="loading">
        <el-table-column type="index" label="序号" width="60" />
        <el-table-column prop="name" label="班级名称" width="150" />
        <el-table-column prop="grade" label="年级" width="100" />
        <el-table-column prop="head_teacher_name" label="班主任" width="120" />
        <el-table-column prop="student_count" label="学生人数" width="100" align="center">
          <template #default="{ row }">
            <el-tag type="info">{{ row.student_count }}人</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="80" align="center">
          <template #default="{ row }">
            <el-tag :type="row.status === 1 ? 'success' : 'danger'" size="small">
              {{ row.status === 1 ? '正常' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="create_time" label="创建时间" width="180" />
        <el-table-column label="操作" width="280" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" size="small" link @click="handleViewMembers(row)">
              成员管理
            </el-button>
            <el-button
              type="primary"
              size="small"
              link
              @click="handleEdit(row)"
              v-if="userInfo.role === 'admin'"
            >
              编辑
            </el-button>
            <el-button
              type="warning"
              size="small"
              link
              @click="handleToggleStatus(row)"
              v-if="userInfo.role === 'admin'"
            >
              {{ row.status === 1 ? '禁用' : '启用' }}
            </el-button>
            <el-button
              type="danger"
              size="small"
              link
              @click="handleDelete(row)"
              v-if="userInfo.role === 'admin'"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.size"
          :page-sizes="[10, 20, 50]"
          :total="pagination.total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="loadClassList"
          @current-change="loadClassList"
        />
      </div>
    </el-card>

    <!-- 创建/编辑班级对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="500px"
      @close="handleCloseDialog"
    >
      <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="班级名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入班级名称" />
        </el-form-item>
        <el-form-item label="年级" prop="grade">
          <el-select v-model="form.grade" placeholder="请选择年级" style="width: 100%">
            <el-option label="一年级" value="一年级" />
            <el-option label="二年级" value="二年级" />
            <el-option label="三年级" value="三年级" />
            <el-option label="四年级" value="四年级" />
            <el-option label="五年级" value="五年级" />
            <el-option label="六年级" value="六年级" />
          </el-select>
        </el-form-item>
        <el-form-item label="班主任" prop="head_teacher_id">
          <el-select
            v-model="form.head_teacher_id"
            placeholder="请选择班主任"
            filterable
            clearable
            style="width: 100%"
          >
            <el-option
              v-for="teacher in teacherList"
              :key="teacher.id"
              :label="teacher.nickname || teacher.username"
              :value="teacher.id"
            />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitLoading">
          确定
        </el-button>
      </template>
    </el-dialog>

    <!-- 班级成员管理对话框 -->
    <ClassMemberDialog
      v-if="memberDialogVisible && currentClass.id"
      v-model="memberDialogVisible"
      :class-id="currentClass.id"
      :class-name="currentClass.name"
      @refresh="loadClassList"
    />
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onActivated, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useUserStore } from '@/stores/user'
import {
  getClassList,
  createClass,
  updateClass,
  deleteClass,
  updateClassStatus,
  getTeacherClasses
} from '@/api/class'
import { getUserList } from '@/api/admin'
import ClassMemberDialog from '@/components/ClassMemberDialog.vue'

const userStore = useUserStore()
const userInfo = computed(() => userStore.userInfo || {})
const router = useRouter()

const loading = ref(false)
const submitLoading = ref(false)
const dialogVisible = ref(false)
const memberDialogVisible = ref(false)
const formRef = ref(null)

const searchForm = reactive({
  name: '',
  grade: '',
  status: ''
})

const pagination = reactive({
  page: 1,
  size: 10,
  total: 0
})

const classList = ref([])
const teacherList = ref([])
const currentClass = ref({})

const form = reactive({
  id: null,
  name: '',
  grade: '',
  head_teacher_id: null
})

const rules = {
  name: [{ required: true, message: '请输入班级名称', trigger: 'blur' }],
  grade: [{ required: true, message: '请选择年级', trigger: 'change' }]
}

const dialogTitle = computed(() => (form.id ? '编辑班级' : '创建班级'))

const loadClassList = async () => {
  loading.value = true
  try {
    // 如果是教师角色，使用教师班级查询接口
    if (userInfo.value.role === 'teacher') {
      const params = {
        page: pagination.page,
        size: pagination.size,
        name: searchForm.name || undefined,
        grade: searchForm.grade || undefined,
        status: searchForm.status !== '' ? searchForm.status : undefined
      }
      const res = await getTeacherClasses(params)
      classList.value = res.data.list || []
      pagination.total = res.data.total || 0
    } else {
      // 管理员使用原有的班级列表接口
      const params = {
        page: pagination.page,
        size: pagination.size,
        name: searchForm.name || undefined,
        grade: searchForm.grade || undefined,
        status: searchForm.status !== '' ? searchForm.status : undefined
      }
      const res = await getClassList(params)
      classList.value = res.data.list || []
      pagination.total = res.data.total || 0
    }
  } catch (error) {
    console.error(error)
  } finally {
    loading.value = false
  }
}

const loadTeacherList = async () => {
  try {
    // 使用更大的 size 或实现分页加载
    const res = await getUserList({ role: 'teacher', size: 1000 })
    teacherList.value = res.data.list || []
  } catch (error) {
    console.error('加载教师列表失败:', error)
    ElMessage.error('加载教师列表失败')
  }
}

const handleCreate = () => {
  form.id = null
  form.name = ''
  form.grade = ''
  form.head_teacher_id = null
  dialogVisible.value = true
}

const handleEdit = (row) => {
  form.id = row.id
  form.name = row.name
  form.grade = row.grade
  form.head_teacher_id = row.head_teacher_id
  dialogVisible.value = true
}

const handleSubmit = async () => {
  await formRef.value.validate()
  submitLoading.value = true
  try {
    if (form.id) {
      await updateClass(form.id, {
        name: form.name,
        grade: form.grade,
        head_teacher_id: form.head_teacher_id
      })
      ElMessage.success('班级更新成功')
    } else {
      await createClass({
        name: form.name,
        grade: form.grade,
        head_teacher_id: form.head_teacher_id
      })
      ElMessage.success('班级创建成功')
    }
    dialogVisible.value = false
    loadClassList()
  } catch (error) {
    console.error(error)
  } finally {
    submitLoading.value = false
  }
}

const handleToggleStatus = async (row) => {
  try {
    const newStatus = row.status === 1 ? 0 : 1
    const action = newStatus === 1 ? '启用' : '禁用'
    await ElMessageBox.confirm(`确定要${action}班级 ${row.name} 吗？`, '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    await updateClassStatus(row.id, { status: newStatus })
    ElMessage.success(`${action}成功`)
    loadClassList()
  } catch (error) {
    if (error !== 'cancel') {
      console.error(error)
    }
  }
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除班级 ${row.name} 吗？删除后班级成员将被移除班级。`,
      '警告',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    await deleteClass(row.id)
    ElMessage.success('删除成功')
    loadClassList()
  } catch (error) {
    if (error !== 'cancel') {
      console.error(error)
    }
  }
}

const handleViewMembers = (row) => {
  currentClass.value = row
  nextTick(() => {
    memberDialogVisible.value = true
  })
}

const handleReset = () => {
  searchForm.name = ''
  searchForm.grade = ''
  searchForm.status = ''
  pagination.page = 1
  loadClassList()
}

const handleCloseDialog = () => {
  dialogVisible.value = false
  formRef.value?.resetFields()
}

onMounted(() => {
  // 检查是否为教师或管理员
  if (!['teacher', 'admin'].includes(userInfo.value.role)) {
    ElMessage.error('您没有权限访问此页面')
    router.push('/home')
    return
  }
  
  loadClassList()
  if (userInfo.value.role === 'admin') {
    loadTeacherList()
  }
})

onActivated(() => {
  loadClassList()
  if (userInfo.value.role === 'admin') {
    loadTeacherList()
  }
})
</script>

<style scoped>
.class-management-container {
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