import request from '@/utils/request'

// 获取考试排名
export const getExamRanking = (examId, params) => {
  return request({
    url: `/exam/${examId}/ranking/`,
    method: 'get',
    params
  })
}

// 获取学生个人成绩趋势
export const getStudentScoreTrend = (params) => {
  return request({
    url: '/student/score/trend/',
    method: 'get',
    params
  })
}

// 获取班级成绩排名
export const getClassRanking = (params) => {
  return request({
    url: '/teacher/class/ranking/',
    method: 'get',
    params
  })
}