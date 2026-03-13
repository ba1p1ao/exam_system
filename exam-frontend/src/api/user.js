import request from '@/utils/request'

// 用户登录
export const login = (data) => {
  return request({
    url: '/user/login/',
    method: 'post',
    data
  })
}

// 用户注册
export const register = (data) => {
  return request({
    url: '/user/register/',
    method: 'post',
    data
  })
}

// 获取用户信息
export const getUserInfo = () => {
  return request({
    url: '/user/info/',
    method: 'get'
  })
}

// 更新用户信息
export const updateUserInfo = (data) => {
  return request({
    url: '/user/update/',
    method: 'put',
    data
  })
}

// 修改密码
export const changePassword = (data) => {
  return request({
    url: '/user/password/',
    method: 'put',
    data
  })
}