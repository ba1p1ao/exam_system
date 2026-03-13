import request from '@/utils/request'

// 获取考试成绩分布图数据
export const getScoreDistributionChart = (examId) => {
  return request({
    url: `/exam/${examId}/chart/score-distribution/`,
    method: 'get'
  })
}

// 获取题目正确率图数据
export const getQuestionCorrectnessChart = (examId) => {
  return request({
    url: `/exam/${examId}/chart/question-correctness/`,
    method: 'get'
  })
}

// 获取学生成绩对比图数据
export const getStudentScoreComparisonChart = () => {
  return request({
    url: '/student/chart/score-comparison/',
    method: 'get'
  })
}

// 获取学生成绩趋势图数据
export const getScoreTrendChart = (days) => {
  return request({
    url: '/student/score/trend/',
    method: 'get',
    params: { days }
  })
}