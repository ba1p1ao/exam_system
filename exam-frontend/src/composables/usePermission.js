import { computed } from 'vue'
import { useUserStore } from '@/stores/user'
import { ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'

export function usePermission(allowedRoles) {
  const userStore = useUserStore()
  const router = useRouter()

  const hasPermission = computed(() => {
    const role = userStore.userInfo?.role
    return role && allowedRoles.includes(role)
  })

  const checkPermission = () => {
    if (!hasPermission.value) {
      ElMessage.error('您没有权限访问此页面')
      router.push('/home')
      return false
    }
    return true
  }

  return {
    hasPermission,
    checkPermission
  }
}