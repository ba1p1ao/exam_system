import request from '@/utils/request'

// 获取错题列表
export const getMistakeList = (params) => {
  return request({
    url: '/mistake/list/',
    method: 'get',
    params
  })
}

// 获取错题列表和统计数据（合并接口）
// 只需一次请求即可获取所有数据
export const getMistakeListWithStatistics = (params) => {
  return request({
    url: '/mistake/list-with-statistics/',
    method: 'get',
    params
  })
}

// 标记错题为已掌握
export const markMistakeAsMastered = (mistakeId) => {
  return request({
    url: `/mistake/${mistakeId}/mastered/`,
    method: 'put'
  })
}

// 导出错题本
export const exportMistakeQuestions = () => {
  return request({
    url: '/mistake/export/',
    method: 'post',
    responseType: 'blob'
  })
}