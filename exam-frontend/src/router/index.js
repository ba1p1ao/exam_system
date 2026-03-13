import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/stores/user'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/',
    name: 'Layout',
    component: () => import('@/views/Layout.vue'),
    meta: { requiresAuth: true },
    redirect: '/home',
    children: [
      {
        path: '/home',
        name: 'Home',
        component: () => import('@/views/Home.vue'),
        meta: { title: '首页' }
      },
      {
        path: '/questions',
        name: 'Questions',
        component: () => import('@/views/Questions.vue'),
        meta: { title: '题库管理', roles: ['teacher', 'admin'] }
      },
      {
        path: '/questions/add',
        name: 'QuestionAdd',
        component: () => import('@/views/QuestionForm.vue'),
        meta: { title: '添加题目', roles: ['teacher', 'admin'] }
      },
      {
        path: '/questions/edit/:id',
        name: 'QuestionEdit',
        component: () => import('@/views/QuestionForm.vue'),
        meta: { title: '编辑题目', roles: ['teacher', 'admin'] }
      },
      {
        path: '/exams',
        name: 'Exams',
        component: () => import('@/views/Exams.vue'),
        meta: { title: '试卷管理', roles: ['teacher', 'admin'] }
      },
      {
        path: '/exams/add',
        name: 'ExamAdd',
        component: () => import('@/views/ExamForm.vue'),
        meta: { title: '创建试卷', roles: ['teacher', 'admin'] }
      },
      {
        path: '/exams/edit/:id',
        name: 'ExamEdit',
        component: () => import('@/views/ExamForm.vue'),
        meta: { title: '编辑试卷', roles: ['teacher', 'admin'] }
      },
      {
        path: '/exams/detail/:id',
        name: 'ExamDetail',
        component: () => import('@/views/ExamDetail.vue'),
        meta: { title: '考试详情', roles: ['teacher', 'admin'] }
      },
      {
        path: '/exam-list',
        name: 'ExamList',
        component: () => import('@/views/ExamList.vue'),
        meta: { title: '考试列表', roles: ['student'] }
      },
      {
        path: '/exam-take/:id',
        name: 'ExamTake',
        component: () => import('@/views/ExamTake.vue'),
        meta: { title: '参加考试', roles: ['student'] }
      },
      {
        path: '/exam-record/:id',
        name: 'ExamRecord',
        component: () => import('@/views/ExamRecord.vue'),
        meta: { title: '考试记录' }
      },
      {
        path: '/records',
        name: 'Records',
        component: () => import('@/views/Records.vue'),
        meta: { title: '考试记录' }
      },
      {
        path: '/profile',
        name: 'Profile',
        component: () => import('@/views/Profile.vue'),
        meta: { title: '个人中心' }
      },
      {
        path: '/users',
        name: 'Users',
        component: () => import('@/views/Users.vue'),
        meta: { title: '用户管理', roles: ['admin'] }
      },
      {
        path: '/mistake-book',
        name: 'MistakeBook',
        component: () => import('@/views/MistakeBook.vue'),
        meta: { title: '错题本', roles: ['student'] }
      },
      {
        path: '/ranking',
        name: 'Ranking',
        component: () => import('@/views/Ranking.vue'),
        meta: { title: '成绩排名' }
      },
      {
        path: '/class-management',
        name: 'ClassManagement',
        component: () => import('@/views/ClassManagement.vue'),
        meta: { title: '班级管理', roles: ['admin', 'teacher'] }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach(async (to, from, next) => {
  const userStore = useUserStore()
  const token = userStore.token

  if (to.meta.requiresAuth && !token) {
    next('/login')
  } else if (to.path === '/login' && token) {
    next('/')
  } else if (to.meta.roles) {
    // 如果没有用户信息，尝试获取
    if (!userStore.userInfo || !userStore.userInfo.role) {
      try {
        await userStore.getUserInfo()
      } catch (error) {
        userStore.logout()
        next('/login')
        return
      }
    }
    const role = userStore.userInfo?.role
    if (!to.meta.roles.includes(role)) {
      next('/')
    } else {
      next()
    }
  } else {
    next()
  }
})

export default router