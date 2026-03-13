<template>
  <div class="profile-container">
    <el-card>
      <template #header>
        <span>个人中心</span>
      </template>

      <el-tabs v-model="activeTab">
        <el-tab-pane label="基本信息" name="info">
          <el-form :model="form" :rules="rules" ref="formRef" label-width="100px" style="max-width: 500px">
            <el-form-item label="用户名">
              <el-input v-model="userInfo.username" disabled />
            </el-form-item>
            <el-form-item label="角色">
              <el-input :value="roleText" disabled />
            </el-form-item>
            <el-form-item label="昵称" prop="nickname">
              <el-input v-model="form.nickname" placeholder="请输入昵称" />
            </el-form-item>
            <el-form-item label="头像">
              <el-avatar :size="80" :src="form.avatar">
                {{ form.nickname?.charAt(0) }}
              </el-avatar>
              <el-button type="primary" size="small" style="margin-left: 10px" @click="handleUploadAvatar">
                上传头像
              </el-button>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="handleUpdateInfo" :loading="loading">
                保存修改
              </el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>

        <el-tab-pane label="修改密码" name="password">
          <el-form
            :model="passwordForm"
            :rules="passwordRules"
            ref="passwordFormRef"
            label-width="100px"
            style="max-width: 500px"
          >
            <el-form-item label="原密码" prop="old_password">
              <el-input v-model="passwordForm.old_password" type="password" placeholder="请输入原密码" />
            </el-form-item>
            <el-form-item label="新密码" prop="new_password">
              <el-input v-model="passwordForm.new_password" type="password" placeholder="请输入新密码" />
            </el-form-item>
            <el-form-item label="确认密码" prop="confirm_password">
              <el-input
                v-model="passwordForm.confirm_password"
                type="password"
                placeholder="请再次输入新密码"
              />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="handleChangePassword" :loading="passwordLoading">
                修改密码
              </el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>

        <el-tab-pane label="班级信息" name="class" v-if="userInfo.role === 'student'">
          <div v-loading="classLoading" class="class-info">
            <el-empty v-if="!classInfo" description="您还未加入班级" />
            <el-descriptions v-else :column="2" border>
              <el-descriptions-item label="班级名称">{{ classInfo.name }}</el-descriptions-item>
              <el-descriptions-item label="年级">{{ classInfo.grade }}</el-descriptions-item>
              <el-descriptions-item label="班主任">{{ classInfo.head_teacher_name }}</el-descriptions-item>
              <el-descriptions-item label="学生人数">{{ classInfo.student_count }}人</el-descriptions-item>
              <el-descriptions-item label="加入时间" :span="2">{{ classInfo.join_time }}</el-descriptions-item>
            </el-descriptions>
          </div>
        </el-tab-pane>

        <el-tab-pane label="成绩对比" name="comparison" v-if="userInfo.role === 'student'">
          <StudentScoreComparisonChart ref="comparisonChartRef" />
        </el-tab-pane>

        </el-tabs>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'
import { updateUserInfo, changePassword } from '@/api/user'
import { getStudentClass } from '@/api/class'
import StudentScoreComparisonChart from '@/components/StudentScoreComparisonChart.vue'

const userStore = useUserStore()

const activeTab = ref('info')
const formRef = ref(null)
const passwordFormRef = ref(null)
const loading = ref(false)
const passwordLoading = ref(false)
const classLoading = ref(false)
const classInfo = ref(null)

const userInfo = computed(() => userStore.userInfo || {})

const roleText = computed(() => {
  const roleMap = {
    student: '学生',
    teacher: '教师',
    admin: '管理员'
  }
  return roleMap[userInfo.value.role] || '未知'
})

const form = reactive({
  nickname: '',
  avatar: ''
})

const passwordForm = reactive({
  old_password: '',
  new_password: '',
  confirm_password: ''
})

const rules = {
  nickname: [{ required: true, message: '请输入昵称', trigger: 'blur' }]
}

const validateConfirmPassword = (rule, value, callback) => {
  if (value !== passwordForm.new_password) {
    callback(new Error('两次输入密码不一致'))
  } else {
    callback()
  }
}

const passwordRules = {
  old_password: [{ required: true, message: '请输入原密码', trigger: 'blur' }],
  new_password: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6位', trigger: 'blur' }
  ],
  confirm_password: [
    { required: true, message: '请确认新密码', trigger: 'blur' },
    { validator: validateConfirmPassword, trigger: 'blur' }
  ]
}

const handleUpdateInfo = async () => {
  await formRef.value.validate()
  loading.value = true
  try {
    await updateUserInfo(form)
    await userStore.getUserInfo()
    ElMessage.success('修改成功')
  } catch (error) {
    console.error(error)
  } finally {
    loading.value = false
  }
}

const handleUploadAvatar = () => {
  const input = document.createElement('input')
  input.type = 'file'
  input.accept = 'image/*'
  input.onchange = async (e) => {
    const file = e.target.files[0]
    if (!file) return

    // 验证文件大小（限制为 2MB）
    if (file.size > 2 * 1024 * 1024) {
      ElMessage.error('图片大小不能超过 2MB')
      return
    }

    // 验证文件类型
    if (!file.type.startsWith('image/')) {
      ElMessage.error('请上传图片文件')
      return
    }

    // 创建 FormData
    const formData = new FormData()
    formData.append('avatar', file)

    try {
      // 调用上传接口（需要后端支持）
      const res = await updateUserInfo({ avatar: formData })
      form.avatar = res.data.avatar
      await userStore.getUserInfo()
      ElMessage.success('头像上传成功')
    } catch (error) {
      console.error('上传头像失败:', error)
      ElMessage.error('头像上传失败，请重试')
    }
  }
  input.click()
}

const handleChangePassword = async () => {
  await passwordFormRef.value.validate()
  passwordLoading.value = true
  try {
    await changePassword({
      old_password: passwordForm.old_password,
      new_password: passwordForm.new_password
    })
    ElMessage.success('密码修改成功，请重新登录')
    userStore.logout()
    window.location.href = '/login'
  } catch (error) {
    console.error(error)
  } finally {
    passwordLoading.value = false
  }
}

onMounted(() => {
  if (userInfo.value) {
    form.nickname = userInfo.value.nickname || ''
    form.avatar = userInfo.value.avatar || ''
    
    // 如果是学生，加载班级信息
    if (userInfo.value.role === 'student') {
      loadClassInfo()
    }
  }
})

const loadClassInfo = async () => {
  classLoading.value = true
  try {
    const res = await getStudentClass()
    classInfo.value = res.data
  } catch (error) {
    console.error(error)
  } finally {
    classLoading.value = false
  }
}
</script>

<style scoped>
.profile-container {
  max-width: 800px;
  margin: 0 auto;
}
</style>