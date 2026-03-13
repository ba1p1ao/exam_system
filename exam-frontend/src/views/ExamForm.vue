<template>
    <div class="exam-form-container">
        <el-card>
            <template #header>
                <div class="card-header">
                    <span>{{ isEdit ? '编辑试卷' : '创建试卷' }}</span>
                    <el-button @click="handleBack">返回</el-button>
                </div>
            </template>

            <el-form :model="form" :rules="rules" ref="formRef" label-width="130px">
                <el-form-item label="试卷标题" prop="title">
                    <el-input v-model="form.title" placeholder="请输入试卷标题（2-100个字符）" maxlength="100" show-word-limit />
                </el-form-item>

                <el-form-item label="试卷描述" prop="description">
                    <el-input v-model="form.description" type="textarea" :rows="3" placeholder="请输入试卷描述（选填，不超过500个字符）"
                        maxlength="500" show-word-limit />
                </el-form-item>

                <el-form-item label="考试时长(分钟)" prop="duration">
                    <el-input-number v-model="form.duration" :min="1" :max="480" controls-position="right" />
                    <span class="form-tip">考试时长为1-480分钟</span>
                </el-form-item>

                <el-form-item label="总分" prop="total_score">
                    <el-input-number v-model="form.total_score" :min="1" :max="1000" controls-position="right"
                        @change="handleScoreChange" />
                    <span class="form-tip">总分为1-1000分</span>
                </el-form-item>

                <el-form-item label="及格分数" prop="pass_score">
                    <el-input-number v-model="form.pass_score" :min="1" :max="1000" controls-position="right" />
                    <span class="form-tip">及格分数不能大于总分</span>
                </el-form-item>

                <el-form-item label="考试开始时间" prop="start_time">
                    <el-date-picker v-model="form.start_time" type="datetime" placeholder="选择开始时间"
                        format="YYYY-MM-DD HH:mm:ss" value-format="YYYY-MM-DD HH:mm:ss"
                        :disabled-date="disabledStartDate" />
                </el-form-item>

                <el-form-item label="考试结束时间" prop="end_time">
                    <el-date-picker v-model="form.end_time" type="datetime" placeholder="选择结束时间"
                        format="YYYY-MM-DD HH:mm:ss" value-format="YYYY-MM-DD HH:mm:ss"
                        :disabled-date="disabledEndDate" />
                </el-form-item>

                <el-form-item label="是否随机组卷">
                    <el-switch v-model="form.is_random" :active-value="1" :inactive-value="0" @click="" />
                    <span class="form-tip">开启后将从题库中随机抽取题目</span>
                </el-form-item>

                <el-form-item label="是否允许重复作答">
                    <el-switch v-model="form.allow_retake" :active-value="1" :inactive-value="0" />
                    <span class="form-tip">开启后学生可以重复参加该考试</span>
                </el-form-item>

                <el-form-item label="指定班级">
                    <el-select v-model="form.class_ids" multiple placeholder="请选择班级（不选则所有班级可见）" style="width: 100%" filterable>
                        <el-option
                            v-for="cls in classList"
                            :key="cls.id"
                            :label="cls.name"
                            :value="cls.id"
                        />
                    </el-select>
                    <span class="form-tip">不选择班级时，所有学生都可以看到此考试</span>
                </el-form-item>

                <el-divider content-position="left">题目选择</el-divider>

                <el-form-item label="选择题目" prop="question_ids">
                    <div class="question-selector">
                        <el-button type="primary" @click="openQuestionDialog">
                            <el-icon>
                                <Plus />
                            </el-icon>
                            添加题目
                        </el-button>
                        <el-tag v-if="selectedQuestions.length > 0" type="success">
                            已选择 {{ selectedQuestions.length }} 道题目
                        </el-tag>
                        <el-tag v-else type="info">
                            请添加题目
                        </el-tag>
                    </div>
                </el-form-item>

                <!-- 题目统计信息 -->
                <el-form-item v-if="selectedQuestions.length > 0">
                    <el-alert :title="`题目统计：共 ${selectedQuestions.length} 道题目，总分 ${selectedTotalScore} 分`" type="info"
                        :closable="false" style="margin-bottom: 15px">
                        <div class="question-stats">
                            <div class="stat-item">
                                <span class="stat-label">题目总分：</span>
                                <span class="stat-value"
                                    :class="{ 'score-warning': selectedTotalScore !== form.total_score }">
                                    {{ selectedTotalScore }} 分
                                </span>
                            </div>
                            <div class="stat-item">
                                <span class="stat-label">试卷总分：</span>
                                <span class="stat-value">{{ form.total_score }} 分</span>
                            </div>
                            <div class="stat-item" v-if="selectedTotalScore !== form.total_score">
                                <span class="stat-label">差异：</span>
                                <span class="stat-value score-warning">{{ form.total_score - selectedTotalScore }}
                                    分</span>
                            </div>
                            <div class="stat-divider"></div>
                            <div class="stat-item" v-for="(count, type) in typeStats" :key="type">
                                <span class="stat-label">{{ getTypeText(type) }}：</span>
                                <span class="stat-value">{{ count }} 道</span>
                            </div>
                        </div>
                    </el-alert>
                </el-form-item>

                <!-- 已选题目列表 -->
                <el-form-item v-if="selectedQuestions.length > 0">
                    <div class="selected-questions-header">
                        <div class="header-left">
                            <el-checkbox v-model="selectAllSelected" @change="handleSelectAllSelected">全选</el-checkbox>
                            <span class="selected-count">已选 {{ selectedRowKeys.length }} 项</span>
                        </div>
                        <el-button type="danger" size="small" @click="handleBatchRemove"
                            :disabled="selectedRowKeys.length === 0">
                            批量移除
                        </el-button>
                    </div>
                    <el-table :data="selectedQuestions" border style="width: 100%" max-height="400"
                        @selection-change="handleSelectedQuestionsChange">
                        <el-table-column type="selection" width="55" />
                        <el-table-column prop="id" label="ID" width="80" />
                        <el-table-column prop="type" label="题型" width="100">
                            <template #default="{ row }">
                                <el-tag :type="getTypeColor(row.type)">{{ getTypeText(row.type) }}</el-tag>
                            </template>
                        </el-table-column>
                        <el-table-column prop="category" label="分类" width="120" />
                        <el-table-column prop="content" label="题目内容" show-overflow-tooltip min-width="200" />
                        <el-table-column prop="difficulty" label="难度" width="80">
                            <template #default="{ row }">
                                <el-tag :type="getDifficultyColor(row.difficulty)" size="small">
                                    {{ getDifficultyText(row.difficulty) }}
                                </el-tag>
                            </template>
                        </el-table-column>
                        <el-table-column prop="score" label="分值" width="80" align="center" />
                        <el-table-column label="操作" width="100" align="center" fixed="right">
                            <template #default="{ $index }">
                                <el-button type="danger" size="small" @click="removeQuestion($index)">
                                    移除
                                </el-button>
                            </template>
                        </el-table-column>
                    </el-table>
                </el-form-item>

                <el-form-item>
                    <el-button type="primary" @click="handleSubmit" :loading="loading" size="large">
                        保存试卷
                    </el-button>
                    <el-button @click="handleBack" size="large">取消</el-button>
                </el-form-item>
            </el-form>
        </el-card>

        <!-- 题目选择弹窗 -->
        <el-dialog v-model="showQuestionDialog" title="选择题目" width="80%" :close-on-click-modal="false"
            @open="handleDialogOpen">
            <!-- 搜索表单 -->
            <el-form :inline="true" :model="questionSearchForm" class="search-form">
                <el-form-item label="题目类型">
                    <el-select v-model="questionSearchForm.type" placeholder="请选择" clearable style="width: 120px">
                        <el-option label="单选题" value="single" />
                        <el-option label="多选题" value="multiple" />
                        <el-option label="判断题" value="judge" />
                        <el-option label="填空题" value="fill" />
                    </el-select>
                </el-form-item>
                <el-form-item label="题目分类">
                    <el-input v-model="questionSearchForm.category" placeholder="请输入分类" clearable
                        style="width: 150px" />
                </el-form-item>
                <el-form-item label="难度">
                    <el-select v-model="questionSearchForm.difficulty" placeholder="请选择" clearable style="width: 120px">
                        <el-option label="简单" value="easy" />
                        <el-option label="中等" value="medium" />
                        <el-option label="困难" value="hard" />
                    </el-select>
                </el-form-item>
                <el-form-item>
                    <el-button type="primary" @click="handleSearchQuestions">
                        <el-icon>
                            <Search />
                        </el-icon>
                        搜索
                    </el-button>
                    <el-button @click="resetQuestionSearch">
                        <el-icon>
                            <Refresh />
                        </el-icon>
                        重置
                    </el-button>
                </el-form-item>
            </el-form>

            <!-- 已选提示 -->
            <el-alert v-if="selectedQuestions.length > 0"
                :title="`当前试卷已选择 ${selectedQuestions.length} 道题目，总分 ${selectedTotalScore} 分`" type="info"
                :closable="false" style="margin-bottom: 15px" />

            <!-- 题目表格 -->
            <el-table :data="questionList" v-loading="questionLoading" border max-height="450" ref="questionTableRef"
                @selection-change="handleQuestionSelectionChange" :row-key="getRowKey">
                <el-table-column type="selection" width="55" :reserve-selection="true" />
                <el-table-column prop="id" label="ID" width="80" />
                <el-table-column prop="type" label="题型" width="100">
                    <template #default="{ row }">
                        <el-tag :type="getTypeColor(row.type)" size="small">{{ getTypeText(row.type) }}</el-tag>
                    </template>
                </el-table-column>
                <el-table-column prop="category" label="分类" width="120" />
                <el-table-column prop="content" label="题目内容" show-overflow-tooltip min-width="200" />
                <el-table-column prop="difficulty" label="难度" width="80">
                    <template #default="{ row }">
                        <el-tag :type="getDifficultyColor(row.difficulty)" size="small">
                            {{ getDifficultyText(row.difficulty) }}
                        </el-tag>
                    </template>
                </el-table-column>
                <el-table-column prop="score" label="分值" width="80" align="center" />
                <el-table-column label="状态" width="80" align="center">
                    <template #default="{ row }">
                        <el-tag v-if="isQuestionSelected(row.id)" type="success" size="small">已选</el-tag>
                        <el-tag v-else type="info" size="small">未选</el-tag>
                    </template>
                </el-table-column>
            </el-table>

            <!-- 分页 -->
            <div class="pagination-container">
                <el-pagination v-model:current-page="questionPagination.page"
                    v-model:page-size="questionPagination.size" :total="questionPagination.total"
                    layout="total, sizes, prev, pager, next, jumper" :page-sizes="[10, 20, 50, 100]"
                    @current-change="handlePageChange" @size-change="handleSizeChange" />
            </div>

            <template #footer>
                <el-button @click="showQuestionDialog = false">取消</el-button>
                <el-button type="primary" @click="confirmSelectQuestions"
                    :disabled="tempSelectedQuestions.length === 0">
                    确定 ({{ tempSelectedQuestions.length }})
                </el-button>
            </template>
        </el-dialog>
    </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, nextTick, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useUserStore } from '@/stores/user'
import { Plus, Search, Refresh } from '@element-plus/icons-vue'
import { getExamDetail, addExam, updateExam } from '@/api/exam'
import { getClassOptions } from '@/api/class'
import { getQuestionList } from '@/api/question'

const userStore = useUserStore()
const userInfo = computed(() => userStore.userInfo || {})

// 检查是否为教师或管理员
const router = useRouter()
const route = useRoute()

const formRef = ref(null)
const questionTableRef = ref(null)
const loading = ref(false)
const showQuestionDialog = ref(false)
const questionLoading = ref(false)

const isEdit = computed(() => !!route.params.id)

const form = reactive({
    title: '',
    description: '',
    duration: 60,
    total_score: 100,
    pass_score: 60,
    start_time: '',
    end_time: '',
    is_random: 0,
    allow_retake: 0,
    class_ids: [],
    question_ids: []
})

// 增强的表单验证规则
const rules = {
    title: [
        { required: true, message: '请输入试卷标题', trigger: 'blur' },
        { min: 2, max: 100, message: '试卷标题长度为2-100个字符', trigger: 'blur' }
    ],
    description: [
        { max: 500, message: '试卷描述不能超过500个字符', trigger: 'blur' }
    ],
    duration: [
        { required: true, message: '请输入考试时长', trigger: 'blur' },
        { type: 'number', min: 1, max: 480, message: '考试时长为1-480分钟', trigger: 'blur' }
    ],
    total_score: [
        { required: true, message: '请输入总分', trigger: 'blur' },
        { type: 'number', min: 1, max: 1000, message: '总分为1-1000分', trigger: 'blur' }
    ],
    pass_score: [
        { required: true, message: '请输入及格分数', trigger: 'blur' },
        { type: 'number', min: 1, max: 1000, message: '及格分数为1-1000分', trigger: 'blur' },
        {
            validator: (rule, value, callback) => {
                if (value > form.total_score) {
                    callback(new Error('及格分数不能大于总分'))
                } else {
                    callback()
                }
            },
            trigger: 'blur'
        }
    ],
    start_time: [
        { required: true, message: '请选择考试开始时间', trigger: 'change' }
    ],
    end_time: [
        { required: true, message: '请选择考试结束时间', trigger: 'change' },
        {
            validator: (rule, value, callback) => {
                if (form.start_time && value && new Date(value) <= new Date(form.start_time)) {
                    callback(new Error('结束时间必须大于开始时间'))
                } else {
                    callback()
                }
            },
            trigger: 'change'
        }
    ],
    question_ids: [
        {
            validator: (rule, value, callback) => {
                if (!value || value.length === 0) {
                    callback(new Error('请至少选择一道题目'))
                } else {
                    callback()
                }
            },
            trigger: 'change'
        }
    ]
}

const selectedQuestions = ref([])
const classList = ref([])
const tempSelectedQuestions = ref([])
const selectedRowKeys = ref([])
const selectAllSelected = ref(false)

const questionSearchForm = reactive({
    type: '',
    category: '',
    difficulty: ''
})

const questionList = ref([])
const questionPagination = reactive({
    page: 1,
    size: 10,
    total: 0
})

// 计算属性
const selectedTotalScore = computed(() => {
    return selectedQuestions.value.reduce((sum, q) => sum + (q.score || 0), 0)
})

const typeStats = computed(() => {
    const stats = {}
    selectedQuestions.value.forEach(q => {
        stats[q.type] = (stats[q.type] || 0) + 1
    })
    return stats
})

// 辅助函数
const getTypeText = (type) => {
    const typeMap = {
        single: '单选题',
        multiple: '多选题',
        judge: '判断题',
        fill: '填空题'
    }
    return typeMap[type] || type
}

// 禁用开始日期（不能早于当前时间）
const disabledStartDate = (time) => {
    return time.getTime() < Date.now() - 8.64e7
}

// 禁用结束日期（必须大于开始时间）
const disabledEndDate = (time) => {
    if (!form.start_time) {
        return time.getTime() < Date.now() - 8.64e7
    }
    return time.getTime() <= new Date(form.start_time).getTime()
}

// 打开题目选择对话框
const openQuestionDialog = () => {
    showQuestionDialog.value = true
}

// 对话框打开时的处理
const handleDialogOpen = () => {
    tempSelectedQuestions.value = []
    questionPagination.page = 1
    loadQuestions().then(() => {
        // 在题目加载完成后清除选中状态
        nextTick(() => {
            if (questionTableRef.value) {
                questionTableRef.value.clearSelection()
                // 重新设置已选题目的选中状态
                selectedQuestions.value.forEach(selectedQ => {
                    const row = questionList.value.find(q => q.id === selectedQ.id)
                    if (row) {
                        questionTableRef.value.toggleRowSelection(row, true)
                    }
                })
            }
        })
    })
}

// 搜索题目
const handleSearchQuestions = () => {
    questionPagination.page = 1
    loadQuestions()
}

// 分页变化
const handlePageChange = (page) => {
    questionPagination.page = page
    loadQuestions()
}

// 每页数量变化
const handleSizeChange = (size) => {
    questionPagination.size = size
    questionPagination.page = 1
    loadQuestions()
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

const getRowKey = (row) => {
    return row.id
}

const isQuestionSelected = (id) => {
    return selectedQuestions.value.some(q => q.id === id)
}

// 加载班级列表
const loadClassList = async () => {
  try {
    const res = await getClassOptions()
    classList.value = res.data || []
  } catch (error) {
    console.error(error)
  }
}

// 加载题目列表
const loadQuestions = async () => {
    questionLoading.value = true
    try {
        const params = {
            page: questionPagination.page,
            size: questionPagination.size,
            ...questionSearchForm
        }
        const res = await getQuestionList(params)
        questionList.value = res.data.list || []
        questionPagination.total = res.data.total || 0
    } catch (error) {
        console.error(error)
        ElMessage.error('加载题目列表失败')
    } finally {
        questionLoading.value = false
    }
}

// 题目选择变化
const handleQuestionSelectionChange = (selection) => {
    tempSelectedQuestions.value = selection
}

// 确认选择题目
const confirmSelectQuestions = () => {
    if (tempSelectedQuestions.value.length === 0) {
        ElMessage.warning('请选择至少一道题目')
        return
    }

    // 过滤已存在的题目，避免重复添加
    const newQuestions = tempSelectedQuestions.value.filter(
        tempQ => !selectedQuestions.value.some(selectedQ => selectedQ.id === tempQ.id)
    )

    if (newQuestions.length === 0) {
        ElMessage.info('所选题目已在试卷中')
        showQuestionDialog.value = false
        return
    }

    const duplicateCount = tempSelectedQuestions.value.length - newQuestions.length
    if (duplicateCount > 0) {
        ElMessage.warning(`已过滤 ${duplicateCount} 道重复题目`)
    }

    selectedQuestions.value = [...selectedQuestions.value, ...newQuestions]
    form.question_ids = selectedQuestions.value.map(q => q.id)

    ElMessage.success(`成功添加 ${newQuestions.length} 道题目`)
    showQuestionDialog.value = false
}

// 重置题目搜索
const resetQuestionSearch = () => {
    Object.assign(questionSearchForm, {
        type: '',
        category: '',
        difficulty: ''
    })
    questionPagination.page = 1
    loadQuestions()
}

// 已选题目选择变化
const handleSelectedQuestionsChange = (selection) => {
    selectedRowKeys.value = selection.map(q => q.id)
}

// 已选题目全选
const handleSelectAllSelected = (val) => {
    if (val) {
        selectedRowKeys.value = selectedQuestions.value.map(q => q.id)
    } else {
        selectedRowKeys.value = []
    }
}

// 批量移除题目
const handleBatchRemove = () => {
    if (selectedRowKeys.value.length === 0) {
        ElMessage.warning('请先选择要移除的题目')
        return
    }

    ElMessageBox.confirm(
        `确定要移除选中的 ${selectedRowKeys.value.length} 道题目吗？`,
        '确认移除',
        {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning'
        }
    ).then(() => {
        selectedQuestions.value = selectedQuestions.value.filter(
            q => !selectedRowKeys.value.includes(q.id)
        )
        form.question_ids = selectedQuestions.value.map(q => q.id)
        selectedRowKeys.value = []
        selectAllSelected.value = false
        ElMessage.success('移除成功')
    }).catch(() => {
        // 用户取消
    })
}

// 移除单个题目
const removeQuestion = (index) => {
    ElMessageBox.confirm(
        '确定要移除这道题目吗？',
        '确认移除',
        {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning'
        }
    ).then(() => {
        selectedQuestions.value.splice(index, 1)
        form.question_ids = selectedQuestions.value.map(q => q.id)
        ElMessage.success('移除成功')
    }).catch(() => {
        // 用户取消
    })
}

// 分数变化处理
const handleScoreChange = (value) => {
    if (form.pass_score > value) {
        form.pass_score = Math.floor(value * 0.6)
    }
}

// // 随机选题
const getRandomQuestionList = (questions, totalScore) => {
    if (questions.length === 0) return []

    // 1. 按分数分组
    let questionScore = {}
    questions.forEach(item => {
        if (!questionScore[item.score]) {
            questionScore[item.score] = []
        }
        questionScore[item.score].push(item)
    })

    // 2. 使用贪心算法找到最接近的组合
    const findBestCombination = (targetScore) => {
        const scores = Object.keys(questionScore).map(Number).sort((a, b) => b - a)
        const usedQuestions = []
        let currentScore = 0

        for (const score of scores) {
            while (currentScore < targetScore && questionScore[score].length > 0) {
                if (currentScore + score <= targetScore) {
                    const question = questionScore[score].pop()
                    usedQuestions.push(question)
                    currentScore += score
                } else {
                    break
                }
            }
        }

        return usedQuestions
    }

    const selectedQuestions = findBestCombination(totalScore)
    const actualTotal = selectedQuestions.reduce((sum, q) => sum + q.score, 0)

    // 3. 如果总分不匹配，提示用户
    if (actualTotal !== totalScore) {
        ElMessage.warning(`随机组卷总分(${actualTotal}分)与目标总分(${totalScore}分)不一致，请手动调整`)
    }

    return selectedQuestions
}
watch(() => form.is_random, async () => {

    if (form.is_random == 1) {
        questionPagination.page = 1
        questionPagination.size = questionPagination.total

        const params = {
            page: questionPagination.page,
            size: questionPagination.total,
        }
        const res = await getQuestionList(params)
        const questions = res.data.list || []

        selectedQuestions.value = getRandomQuestionList(questions, form.total_score)
        form.question_ids = selectedQuestions.value.map(q => q.id)
    } else {
        selectedQuestions.value = []
        form.question_ids = []
        questionPagination.page = 1
        questionPagination.size = 10
    }
})


// 提交表单
const handleSubmit = async () => {
    // 验证表单
    try {
        await formRef.value.validate()
    } catch (error) {
        return
    }

    // 验证题目数量
    if (selectedQuestions.value.length === 0) {
        ElMessage.error('请至少选择一道题目')
        return
    }

    // 验证分数
    if (selectedTotalScore.value !== form.total_score) {
        ElMessageBox.confirm(
            `题目总分(${selectedTotalScore.value}分)与试卷总分(${form.total_score.value}分)不一致，是否继续保存？`,
            '分数不一致提示',
            {
                confirmButtonText: '继续保存',
                cancelButtonText: '取消',
                type: 'warning'
            }
        ).then(() => {
            doSubmit()
        }).catch(() => {
            // 用户取消
        })
    } else {
        doSubmit()
    }
}

// 执行提交
const doSubmit = async () => {
    loading.value = true
    try {
        const submitData = {
            ...form,
            question_ids: selectedQuestions.value.map(q => q.id)
        }

        if (isEdit.value) {
            await updateExam(route.params.id, submitData)
            ElMessage.success('更新成功')
        } else {
            await addExam(submitData)
            ElMessage.success('创建成功')
        }
        router.push('/exams')
    } catch (error) {
        console.error(error)
        ElMessage.error(isEdit.value ? '更新失败' : '创建失败')
    } finally {
        loading.value = false
    }
}

// 返回
const handleBack = () => {
    if (selectedQuestions.value.length > 0 || form.title) {
        ElMessageBox.confirm(
            '当前未保存的内容将丢失，确定要返回吗？',
            '确认返回',
            {
                confirmButtonText: '确定',
                cancelButtonText: '取消',
                type: 'warning'
            }
        ).then(() => {
            router.back()
        }).catch(() => {
            // 用户取消
        })
    } else {
        router.back()
    }
}

// 加载试卷详情
const loadDetail = async () => {
    try {
        const res = await getExamDetail(route.params.id)
        const data = res.data
        Object.assign(form, {
            title: data.title,
            description: data.description,
            duration: data.duration,
            total_score: data.total_score,
            pass_score: data.pass_score,
            start_time: data.start_time,
            end_time: data.end_time,
            is_random: data.is_random,
            allow_retake: data.allow_retake || 0,
            question_ids: data.question_ids || [],
            class_ids: data.class_ids || []
        })
        selectedQuestions.value = data.questions || []
    } catch (error) {
        console.error(error)
        ElMessage.error('加载试卷详情失败')
    }
}

onMounted(() => {
    // 检查是否为教师或管理员
    const userRole = userInfo.value?.role
    if (!userRole || !['teacher', 'admin'].includes(userRole)) {
      ElMessage.error('您没有权限访问此页面')
      router.push('/home')
      return
    }
    loadClassList()
    if (isEdit.value) {
        loadDetail()

    }
    questionPagination.page = 1
    loadQuestions()
})
</script>

<style scoped>
.exam-form-container {
    max-width: 1200px;
    margin: 20px auto;
    padding: 0 20px;
}

.card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.card-header span {
    font-size: 18px;
    font-weight: 600;
}

.form-tip {
    margin-left: 10px;
    color: #909399;
    font-size: 12px;
}

.question-selector {
    display: flex;
    align-items: center;
    gap: 10px;
    flex-wrap: wrap;
}

.question-stats {
    display: flex;
    flex-wrap: wrap;
    gap: 15px;
    margin-top: 10px;
    padding: 10px;
    background: #f5f7fa;
    border-radius: 4px;
}

.stat-item {
    display: flex;
    align-items: center;
    gap: 5px;
}

.stat-label {
    color: #606266;
    font-size: 14px;
}

.stat-value {
    color: #303133;
    font-weight: 600;
    font-size: 14px;
}

.stat-value.score-warning {
    color: #f56c6c;
}

.stat-divider {
    width: 1px;
    height: 20px;
    background: #dcdfe6;
    margin: 0 5px;
}

.selected-questions-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 10px;
    padding: 10px;
    background: #f5f7fa;
    border-radius: 4px;
}

.header-left {
    display: flex;
    align-items: center;
    gap: 10px;
}

.selected-count {
    color: #909399;
    font-size: 12px;
}

.search-form {
    margin-bottom: 15px;
}

.pagination-container {
    margin-top: 20px;
    display: flex;
    justify-content: flex-end;
}

/* 表单样式优化 */
:deep(.el-form-item__label) {
    font-weight: 500;
}

:deep(.el-input-number) {
    width: 150px;
}

:deep(.el-date-picker) {
    width: 100%;
}

/* 表格样式优化 */
:deep(.el-table) {
    border-radius: 4px;
}

:deep(.el-table th) {
    background: #f5f7fa;
    font-weight: 600;
}

/* 弹窗样式优化 */
:deep(.el-dialog__header) {
    padding: 20px 20px 10px;
    border-bottom: 1px solid #e4e7ed;
}

:deep(.el-dialog__body) {
    padding: 20px;
}

:deep(.el-dialog__footer) {
    padding: 10px 20px 20px;
    border-top: 1px solid #e4e7ed;
}

/* 按钮样式优化 */
:deep(.el-button--large) {
    padding: 12px 24px;
    font-size: 14px;
}

/* 标签样式优化 */
:deep(.el-tag) {
    margin-right: 5px;
}

/* 分隔线样式 */
:deep(.el-divider__text) {
    font-weight: 600;
    color: #303133;
}
</style>