import request from '@/utils/request'

/**
 * 获取班级列表
 * @param {Object} params - 查询参数
 * @returns {Promise}
 */
export function getClassList(params) {
  return request({
    url: '/class/list/',
    method: 'get',
    params
  })
}

/**
 * 获取班级详情
 * @param {number} id - 班级ID
 * @returns {Promise}
 */
export function getClassDetail(id) {
  return request({
    url: `/class/${id}/`,
    method: 'get'
  })
}

/**
 * 创建班级
 * @param {Object} data - 班级信息
 * @returns {Promise}
 */
export function createClass(data) {
  return request({
    url: '/class/create/',
    method: 'post',
    data
  })
}

/**
 * 更新班级信息
 * @param {number} id - 班级ID
 * @param {Object} data - 班级信息
 * @returns {Promise}
 */
export function updateClass(id, data) {
  return request({
    url: `/class/${id}/`,
    method: 'put',
    data
  })
}

/**
 * 删除班级
 * @param {number} id - 班级ID
 * @returns {Promise}
 */
export function deleteClass(id) {
  return request({
    url: `/class/${id}/`,
    method: 'delete'
  })
}

/**
 * 更新班级状态
 * @param {number} id - 班级ID
 * @param {Object} data - 状态信息
 * @returns {Promise}
 */
export function updateClassStatus(id, data) {
  return request({
    url: `/class/${id}/status/`,
    method: 'put',
    data
  })
}

/**
 * 获取班级成员列表
 * @param {number} id - 班级ID
 * @param {Object} params - 查询参数
 * @returns {Promise}
 */
export function getClassMembers(id, params) {
  return request({
    url: `/class/${id}/members/`,
    method: 'get',
    params
  })
}

/**
 * 添加学生到班级
 * @param {number} id - 班级ID
 * @param {Object} data - 用户ID列表
 * @returns {Promise}
 */
export function addClassMembers(id, data) {
  return request({
    url: `/class/${id}/members/add/`,
    method: 'post',
    data
  })
}

/**
 * 从班级移除学生
 * @param {number} id - 班级ID
 * @param {Object} data - 用户ID列表
 * @returns {Promise}
 */
export function removeClassMembers(id, data) {
  return request({
    url: `/class/${id}/members/remove/`,
    method: 'delete',
    data
  })
}

/**
 * 获取可选学生列表（未加入班级的学生）
 * @param {number} id - 班级ID
 * @param {Object} params - 查询参数
 * @returns {Promise}
 */
export function getAvailableStudents(id, params) {
  return request({
    url: `/class/${id}/available-students/`,
    method: 'get',
    params
  })
}

/**
 * 获取班级成绩统计
 * @param {number} id - 班级ID
 * @returns {Promise}
 */
export function getClassStatistics(id) {
  return request({
    url: `/class/${id}/statistics/`,
    method: 'get'
  })
}

/**
 * 获取班级考试排名
 * @param {number} id - 班级ID
 * @param {Object} params - 查询参数
 * @returns {Promise}
 */
export function getClassExamRanking(id, params) {
  return request({
    url: `/class/${id}/exam-ranking/`,
    method: 'get',
    params
  })
}

/**
 * 获取班级成绩趋势
 * @param {number} id - 班级ID
 * @param {Object} params - 查询参数
 * @returns {Promise}
 */
export function getClassScoreTrend(id, params) {
  return request({
    url: `/class/${id}/score-trend/`,
    method: 'get',
    params
  })
}

/**
 * 获取教师管理的班级列表
 * @param {Object} params - 查询参数
 * @returns {Promise}
 */
export function getTeacherClasses(params) {
  return request({
    url: '/teacher/classes/',
    method: 'get',
    params
  })
}

/**
 * 获取学生所在班级信息
 * @returns {Promise}
 */
export function getStudentClass() {
  return request({
    url: '/student/class/',
    method: 'get'
  })
}

/**
 * 获取所有班级（用于下拉选择）
 * @returns {Promise}
 */
export function getClassOptions() {
  return request({
    url: '/class/options/',
    method: 'get'
  })
}