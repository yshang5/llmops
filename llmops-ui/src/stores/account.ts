import { defineStore } from 'pinia'
import { ref } from 'vue'

const initAccount = {
  name: '慕小课',
  email: 'imooc@163.com',
  avatar: '',
}

export const useAccountStore = defineStore('account', () => {
  //1. 定义数据
  const account = ref({ ...initAccount })
  //2. 计算属性
  function update(params: Partial<typeof initAccount>) {
    Object.assign(account.value, params)
  }

  function clear() {
    account.value = { ...initAccount }
  }

  return { account, update, clear }
})
