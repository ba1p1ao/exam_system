import request from '@/utils/request'

// 获取试卷列表
export const getExamList = (params) => {
  return request({
    url: '/exam/list/',
    method: 'get',
    params
  })
}

// 获取学生可参加的考试列表
export const getAvailableExamList = () => {
  return request({
    url: '/exam/available/',
    method: 'get'
  })
}

// 获取试卷详情
export const getExamDetail = (id) => {
  return request({
    url: `/exam/${id}/`,
    method: 'get'
  })
}

// 创建试卷
export const addExam = (data) => {
  return request({
    url: '/exam/add/',
    method: 'post',
    data
  })
}

// 更新试卷
export const updateExam = (id, data) => {
  return request({
    url: `/exam/${id}/`,
    method: 'put',
    data
  })
}

// 删除试卷
export const deleteExam = (id) => {
  return request({
    url: `/exam/${id}/`,
    method: 'delete'
  })
}

// 发布试卷
export const publishExam = (id) => {
  return request({
    url: `/exam/${id}/publish/`,
    method: 'put'
  })
}

// 关闭试卷
export const closeExam = (id) => {
  return request({
    url: `/exam/${id}/close/`,
    method: 'put'
  })
}

// 开始考试
export const startExam = (examId) => {
  return request({
    url: '/exam/start/',
    method: 'post',
    data: { exam_id: examId }
  })
}

// 获取考试题目
export const getExamQuestions = (examId) => {
  return request({
    url: `/exam/${examId}/questions/`,
    method: 'get'
  })
}

// 保存答案
export const saveAnswer = (data) => {
  return request({
    url: '/exam/answer/',
    method: 'post',
    data
  })
}

// 提交试卷
export const submitExam = (examRecordId) => {
  return request({
    url: '/exam/submit/',
    method: 'post',
    data: { exam_record_id: examRecordId }
  })
}

// 获取考试记录列表
export const getExamRecordList = (params) => {
  return request({
    url: '/exam/record/list/',
    method: 'get',
    params
  })
}

// 获取按考试分组的考试记录（管理员/老师专用）
export const getGroupedExamRecords = (params) => {
  return request({
    url: '/exam/grouped-records/',
    method: 'get',
    params
  })
}

// 获取考试记录详情
export const getExamRecordDetail = (id) => {
  return request({
    url: `/exam/record/${id}/`,
    method: 'get'
  })
}

// 获取成绩统计
export const getExamStatistics = (examId) => {
  return request({
    url: `/exam/${examId}/statistics/`,
    method: 'get'
  })
}

// 获取系统统计数据
export const getSystemStatistics = () => {
  return request({
    url: '/exam/statistics/',
    method: 'get'
  })
}

// 检查考试剩余时间
export const checkExamTime = (examRecordId) => {
  return request({
    url: `/exam/time/check/?exam_record_id=${examRecordId}`,
    method: 'get'
  })
}