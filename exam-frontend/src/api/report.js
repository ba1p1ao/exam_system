import request from '@/utils/request'

// 生成考试分析报告
export const generateExamReport = (examId, data) => {
  return request({
    url: `/exam/${examId}/report/generate/`,
    method: 'post',
    data
  })
}

// 导出考试分析报告（PDF）
export const exportExamReport = (examId) => {
  return request({
    url: `/exam/${examId}/report/export/`,
    method: 'get',
    responseType: 'blob'
  })
}

// 发送成绩单邮件
export const sendScoreEmail = (examId, data) => {
  return request({
    url: `/exam/${examId}/report/email/`,
    method: 'post',
    data
  })
}

// 自动提交试卷
export const autoSubmitExam = (examRecordId) => {
  return request({
    url: '/exam/auto-submit/',
    method: 'post',
    data: { exam_record_id: examRecordId }
  })
}