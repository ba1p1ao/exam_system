<template>
  <div class="question-form-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>{{ isEdit ? '编辑题目' : '添加题目' }}</span>
          <el-button @click="handleBack">返回</el-button>
        </div>
      </template>

      <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="题目类型" prop="type">
          <el-select v-model="form.type" placeholder="请选择题目类型" @change="handleTypeChange">
            <el-option label="单选题" value="single" />
            <el-option label="多选题" value="multiple" />
            <el-option label="判断题" value="judge" />
            <el-option label="填空题" value="fill" />
          </el-select>
        </el-form-item>

        <el-form-item label="题目分类" prop="category">
          <el-input v-model="form.category" placeholder="请输入题目分类" />
        </el-form-item>

        <el-form-item label="题目内容" prop="content">
          <el-input
            v-model="form.content"
            type="textarea"
            :rows="4"
            placeholder="请输入题目内容"
          />
        </el-form-item>

        <!-- 选项 -->
        <template v-if="form.type === 'single' || form.type === 'multiple'">
          <el-form-item label="选项A" prop="options.A">
            <el-input v-model="form.options.A" placeholder="请输入选项A" />
          </el-form-item>
          <el-form-item label="选项B" prop="options.B">
            <el-input v-model="form.options.B" placeholder="请输入选项B" />
          </el-form-item>
          <el-form-item label="选项C" prop="options.C">
            <el-input v-model="form.options.C" placeholder="请输入选项C" />
          </el-form-item>
          <el-form-item label="选项D" prop="options.D">
            <el-input v-model="form.options.D" placeholder="请输入选项D" />
          </el-form-item>
        </template>

        <el-form-item label="正确答案" prop="answer">
          <template v-if="form.type === 'single'">
            <el-radio-group v-model="form.answer">
              <el-radio value="A">A</el-radio>
              <el-radio value="B">B</el-radio>
              <el-radio value="C">C</el-radio>
              <el-radio value="D">D</el-radio>
            </el-radio-group>
          </template>
          <template v-else-if="form.type === 'multiple'">
            <el-checkbox-group v-model="multipleAnswers">
              <el-checkbox label="A">A</el-checkbox>
              <el-checkbox label="B">B</el-checkbox>
              <el-checkbox label="C">C</el-checkbox>
              <el-checkbox label="D">D</el-checkbox>
            </el-checkbox-group>
          </template>
          <template v-else-if="form.type === 'judge'">
            <el-radio-group v-model="form.answer">
              <el-radio value="true">正确</el-radio>
              <el-radio value="false">错误</el-radio>
            </el-radio-group>
          </template>
          <template v-else-if="form.type === 'fill'">
            <el-input v-model="form.answer" placeholder="请输入正确答案" />
          </template>
        </el-form-item>

        <el-form-item label="题目解析">
          <el-input
            v-model="form.analysis"
            type="textarea"
            :rows="4"
            placeholder="请输入题目解析"
          />
        </el-form-item>

        <el-form-item label="难度" prop="difficulty">
          <el-select v-model="form.difficulty" placeholder="请选择难度">
            <el-option label="简单" value="easy" />
            <el-option label="中等" value="medium" />
            <el-option label="困难" value="hard" />
          </el-select>
        </el-form-item>

        <el-form-item label="分值" prop="score">
          <el-input-number v-model="form.score" :min="1" :max="100" />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="handleSubmit" :loading="loading">保存</el-button>
          <el-button @click="handleBack">取消</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getQuestionDetail, addQuestion, updateQuestion } from '@/api/question'

const router = useRouter()
const route = useRoute()

const formRef = ref(null)
const loading = ref(false)
const multipleAnswers = ref([])

const isEdit = computed(() => !!route.params.id)

const form = reactive({
  type: 'single',
  category: '',
  content: '',
  options: {
    A: '',
    B: '',
    C: '',
    D: ''
  },
  answer: '',
  analysis: '',
  difficulty: 'medium',
  score: 5
})

const rules = {
  type: [{ required: true, message: '请选择题目类型', trigger: 'change' }],
  category: [{ required: true, message: '请输入题目分类', trigger: 'blur' }],
  content: [{ required: true, message: '请输入题目内容', trigger: 'blur' }],
  answer: [
    {
      required: true,
      validator: (rule, value, callback) => {
        if (form.type === 'multiple') {
          if (multipleAnswers.value.length === 0) {
            callback(new Error('请选择正确答案'))
          } else {
            callback()
          }
        } else {
          if (!value || value.trim() === '') {
            callback(new Error('请选择或输入正确答案'))
          } else {
            callback()
          }
        }
      },
      trigger: 'change'
    }
  ],
  difficulty: [{ required: true, message: '请选择难度', trigger: 'change' }],
  score: [{ required: true, message: '请输入分值', trigger: 'blur' }]
}

const handleTypeChange = () => {
  form.answer = ''
  multipleAnswers.value = []
  if (form.type === 'judge') {
    form.options = { A: '', B: '', C: '', D: '' }
  }
}

const handleSubmit = async () => {
  await formRef.value.validate()

  // 处理多选题答案
  if (form.type === 'multiple') {
    form.answer = multipleAnswers.value.sort().join(',')
  } else if (form.type === 'judge') {
    // 将判断题的答案从 true/false 转换为 A/B
    if (form.answer === 'true') {
      form.answer = 'A'
    } else if (form.answer === 'false') {
      form.answer = 'B'
    }
  }

  loading.value = true
  try {
    if (isEdit.value) {
      // 打印发送的数据
      console.log('发送更新请求的数据:', JSON.stringify(form, null, 2))
      await updateQuestion(route.params.id, form)
      ElMessage.success('更新成功')
    } else {
      await addQuestion(form)
      ElMessage.success('添加成功')
    }
    router.push('/questions')
  } catch (error) {
    console.error(error)
    // 显示错误消息给用户
    if (error.response) {
      ElMessage.error(error.response.data?.message || error.message || '请求失败')
    } else if (error.message) {
      ElMessage.error(error.message)
    } else {
      ElMessage.error('操作失败，请重试')
    }
  } finally {
    loading.value = false
  }
}

const handleBack = () => {
  router.back()
}

const loadDetail = async () => {
  try {
    const res = await getQuestionDetail(route.params.id)
    const data = res.data
    Object.assign(form, data)
    if (data.options) {
      form.options = data.options
    }
    if (data.type === 'multiple') {
      multipleAnswers.value = data.answer.split(',')
    } else if (data.type === 'judge') {
      // 判断题的答案可能是 A（正确）或 B（错误），需要转换为 true/false
      if (data.answer === 'A' || data.answer === '正确') {
        form.answer = 'true'
      } else if (data.answer === 'B' || data.answer === '错误') {
        form.answer = 'false'
      } else {
        form.answer = data.answer
      }
    }
  } catch (error) {
    console.error(error)
  }
}

onMounted(() => {
  if (isEdit.value) {
    loadDetail()
  }
})
</script>

<style scoped>
.question-form-container {
  max-width: 800px;
  margin: 0 auto;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>