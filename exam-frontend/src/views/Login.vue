<template>
  <div class="login-container">
    <div class="login-box">
      <h2>在线考试系统</h2>
      <el-form :model="loginForm" :rules="rules" ref="loginFormRef" label-width="0">
        <el-form-item prop="username">
          <el-input v-model="loginForm.username" placeholder="请输入用户名" prefix-icon="User" />
        </el-form-item>
        <el-form-item prop="password">
          <el-input v-model="loginForm.password" type="password" placeholder="请输入密码" prefix-icon="Lock" @keyup.enter="handleLogin" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleLogin" :loading="loading" style="width: 100%">登录</el-button>
        </el-form-item>
        <el-form-item>
          <div class="login-footer">
            <span>还没有账号？</span>
            <el-link type="primary" @click="showRegister = true">立即注册</el-link>
          </div>
        </el-form-item>
      </el-form>
    </div>

    <!-- 注册弹窗 -->
    <el-dialog v-model="showRegister" title="用户注册" width="400px">
      <el-form :model="registerForm" :rules="registerRules" ref="registerFormRef" label-width="80px">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="registerForm.username" placeholder="请输入用户名" />
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input v-model="registerForm.password" type="password" placeholder="请输入密码" />
        </el-form-item>
        <el-form-item label="确认密码" prop="confirmPassword">
          <el-input v-model="registerForm.confirmPassword" type="password" placeholder="请再次输入密码" />
        </el-form-item>
        <el-form-item label="昵称" prop="nickname">
          <el-input v-model="registerForm.nickname" placeholder="请输入昵称" />
        </el-form-item>
        <el-form-item label="角色" prop="role">
          <el-select v-model="registerForm.role" placeholder="请选择角色" style="width: 100%">
            <el-option label="学生" value="student" />
            <el-option label="教师" value="teacher" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showRegister = false">取消</el-button>
        <el-button type="primary" @click="handleRegister" :loading="registerLoading">注册</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'
import { register as registerApi } from '@/api/user'

const router = useRouter()
const userStore = useUserStore()

const loginFormRef = ref(null)
const registerFormRef = ref(null)
const loading = ref(false)
const registerLoading = ref(false)
const showRegister = ref(false)

const loginForm = reactive({
  username: '',
  password: ''
})

const registerForm = reactive({
  username: '',
  password: '',
  confirmPassword: '',
  nickname: '',
  role: 'student'
})

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
}

const validateConfirmPassword = (rule, value, callback) => {
  if (value !== registerForm.password) {
    callback(new Error('两次输入密码不一致'))
  } else {
    callback()
  }
}

const registerRules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
  confirmPassword: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    { validator: validateConfirmPassword, trigger: 'blur' }
  ],
  nickname: [{ required: true, message: '请输入昵称', trigger: 'blur' }],
  role: [{ required: true, message: '请选择角色', trigger: 'change' }]
}

const handleLogin = async () => {
  await loginFormRef.value.validate()
  loading.value = true
  try {
    await userStore.login(loginForm)
    ElMessage.success('登录成功')
    router.push('/')
  } catch (error) {
    console.error(error)
  } finally {
    loading.value = false
  }
}

const handleRegister = async () => {
  await registerFormRef.value.validate()
  registerLoading.value = true
  try {
    await registerApi(registerForm)
    ElMessage.success('注册成功，请登录')
    showRegister.value = false
    // 自动填充登录表单
    loginForm.username = registerForm.username
    loginForm.password = registerForm.password
  } catch (error) {
    console.error(error)
  } finally {
    registerLoading.value = false
  }
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.login-box {
  width: 400px;
  padding: 40px;
  background: white;
  border-radius: 10px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.login-box h2 {
  text-align: center;
  margin-bottom: 30px;
  color: #333;
}

.login-footer {
  width: 100%;
  text-align: center;
  font-size: 14px;
  color: #666;
}

.login-footer span {
  margin-right: 5px;
}
</style>