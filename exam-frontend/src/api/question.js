import request from '@/utils/request'

// 获取题目列表
export const getQuestionList = (params) => {
  return request({
    url: '/question/list/',
    method: 'get',
    params
  })
}

// 获取题目详情
export const getQuestionDetail = (id) => {
  return request({
    url: `/question/${id}/`,
    method: 'get'
  })
}

// 添加题目
export const addQuestion = (data) => {
  return request({
    url: '/question/add/',
    method: 'post',
    data
  })
}

// 更新题目
export const updateQuestion = (id, data) => {
  return request({
    url: `/question/${id}/`,
    method: 'put',
    data
  })
}

// 删除题目
export const deleteQuestion = (id) => {
  return request({
    url: `/question/${id}/`,
    method: 'delete'
  })
}

// 批量删除题目
export const batchDeleteQuestions = (ids) => {
  return request({
    url: '/question/batch/',
    method: 'delete',
    data: { ids }
  })
}