<template>
  <el-dialog
    v-model="visible"
    title="批量导入题目"
    width="600px"
    @close="handleClose"
  >
    <div class="import-dialog">
      <el-alert
        title="导入说明"
        type="info"
        :closable="false"
        show-icon
        style="margin-bottom: 20px"
      >
        <template #default>
          <div style="line-height: 1.8;">
            <p><strong>步骤：</strong></p>
            <ol style="margin-left: 20px;">
              <li>点击下方"下载导入模板"按钮</li>
              <li>按照模板格式填写题目信息（可参考示例数据）</li>
              <li>保存为 .xlsx 或 .xls 格式</li>
              <li>拖拽或点击上传文件</li>
            </ol>
            <p style="margin-top: 10px;"><strong>注意事项：</strong></p>
            <ul style="margin-left: 20px;">
              <li>题目类型：单选题、多选题、判断题、填空题</li>
              <li>难度：easy（简单）、medium（中等）、hard（困难）</li>
              <li>单选题答案填写选项字母（如：A、B、C、D）</li>
              <li>多选题答案用逗号分隔（如：A,B,D）</li>
              <li>判断题答案填写：A 或 B</li>
              <li>填空题答案直接填写内容</li>
              <li>文件大小限制：10MB</li>
            </ul>
          </div>
        </template>
      </el-alert>

      <div class="download-section">
        <el-button type="primary" @click="handleDownloadTemplate">
          <el-icon><Download /></el-icon>
          下载导入模板
        </el-button>
      </div>

      <el-divider />

      <el-upload
        ref="uploadRef"
        class="upload-demo"
        drag
        :auto-upload="false"
        :limit="1"
        :on-change="handleFileChange"
        :on-exceed="handleExceed"
        accept=".xlsx,.xls"
      >
        <el-icon class="el-icon--upload"><upload-filled /></el-icon>
        <div class="el-upload__text">
          拖拽文件到此处或 <em>点击上传</em>
        </div>
        <template #tip>
          <div class="el-upload__tip">
            只能上传 .xlsx/.xls 文件，且不超过 10MB
          </div>
        </template>
      </el-upload>

      <div v-if="importResult" class="import-result">
        <el-alert
          :title="`导入完成：成功 ${importResult.success} 条，失败 ${importResult.failed} 条`"
          :type="importResult.failed > 0 ? 'warning' : 'success'"
          :closable="false"
          show-icon
        />
        <div v-if="importResult.failed_list && importResult.failed_list.length > 0" class="failed-list">
          <div class="failed-title">失败详情：</div>
          <el-table :data="importResult.failed_list" border size="small" max-height="200">
            <el-table-column prop="row" label="行号" width="80" />
            <el-table-column prop="reason" label="失败原因" />
          </el-table>
        </div>
      </div>
    </div>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleClose">取消</el-button>
        <el-button type="primary" @click="handleImport" :loading="importing">
          开始导入
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { Download, UploadFilled } from '@element-plus/icons-vue'
import { downloadImportTemplate, importQuestions } from '@/api/import-export'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:modelValue', 'success'])

const visible = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

const uploadRef = ref(null)
const importing = ref(false)
const importResult = ref(null)
const selectedFile = ref(null)

const handleDownloadTemplate = async () => {
  try {
    const res = await downloadImportTemplate()
    const blob = new Blob([res], { 
      type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' 
    })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = '题目导入模板.xlsx'
    link.click()
    window.URL.revokeObjectURL(url)
    ElMessage.success('模板下载成功')
  } catch (error) {
    console.error(error)
    ElMessage.error('模板下载失败')
  }
}

const handleFileChange = (file) => {
  selectedFile.value = file.raw
  importResult.value = null
}

const handleExceed = () => {
  ElMessage.warning('只能上传一个文件')
}

const handleImport = async () => {
  if (!selectedFile.value) {
    ElMessage.warning('请先选择要导入的文件')
    return
  }

  importing.value = true
  try {
    const res = await importQuestions(selectedFile.value)
    importResult.value = res.data
    
    if (res.data.failed === 0) {
      ElMessage.success(`导入成功，共导入 ${res.data.success} 道题目`)
      emit('success')
      handleClose()
    } else {
      ElMessage.warning(`导入完成，成功 ${res.data.success} 道，失败 ${res.data.failed} 道`)
    }
  } catch (error) {
    console.error(error)
    ElMessage.error('导入失败')
  } finally {
    importing.value = false
  }
}

const handleClose = () => {
  visible.value = false
  importResult.value = null
  selectedFile.value = null
  if (uploadRef.value) {
    uploadRef.value.clearFiles()
  }
  emit('update:modelValue', false)
}

// 监听 modelValue 变化
defineExpose({
  open: () => {
    dialogVisible.value = true
  }
})
</script>

<style scoped>
.import-dialog {
  padding: 10px 0;
}

.download-section {
  text-align: center;
  padding: 20px;
  background: #F5F7FA;
  border-radius: 8px;
}

.upload-demo {
  margin: 20px 0;
}

.import-result {
  margin-top: 20px;
}

.failed-list {
  margin-top: 15px;
}

.failed-title {
  font-weight: bold;
  margin-bottom: 10px;
  color: #F56C6C;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
</style>