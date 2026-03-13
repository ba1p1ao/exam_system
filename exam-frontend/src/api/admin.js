import request from '@/utils/request'

// 获取用户列表
export const getUserList = (params) => {
  return request({
    url: '/admin/users/',
    method: 'get',
    params
  })
}

// 获取用户详情
export const getUserDetail = (id) => {
  return request({
    url: `/admin/users/${id}/`,
    method: 'get'
  })
}

// 更新用户状态
export const updateUserStatus = (id, data) => {
  return request({
    url: `/admin/users/${id}/status/`,
    method: 'put',
    data
  })
}

// 更新用户角色
export const updateUserRole = (id, data) => {
  return request({
    url: `/admin/users/${id}/role/`,
    method: 'put',
    data
  })
}

// 删除用户
export const deleteUser = (id) => {
  return request({
    url: `/admin/users/${id}/`,
    method: 'delete'
  })
}

// 获取用户统计数据
export const getUserStatistics = () => {
  return request({
    url: '/admin/users/statistics/',
    method: 'get'
  })
}