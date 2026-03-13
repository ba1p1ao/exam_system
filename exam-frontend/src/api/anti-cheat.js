import request from '@/utils/request'

// 记录考试行为
export const logExamBehavior = (data) => {
  return request({
    url: '/exam/behavior/log/',
    method: 'post',
    data
  })
}

// 获取考试行为记录
export const getExamBehaviorLogs = (examRecordId) => {
  return request({
    url: `/exam/${examRecordId}/behavior/logs/`,
    method: 'get'
  })
}