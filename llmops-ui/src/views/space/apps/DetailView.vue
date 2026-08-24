<script setup lang="ts">
import { ref } from 'vue'
import { Message } from '@arco-design/web-vue'
import { debugApp } from '@/services/app.ts'
import { useRoute } from 'vue-router'

// 1. 定义交互所需的数据
const query = ref('')
const messages = ref<{ role: string; content: string }[]>([])
const isLoading = ref(false)
const route = useRoute()

const clearMessage = () => {
  messages.value = []
}

const send = async () => {
  // 1.获取用户输入的数据，并且校验值是否存在
  if (!query.value) {
    Message.error('用户提问不能为空')
    return
  }

  //2.当上一条请求还没结束时，不许发出新的请求
  if (isLoading.value) {
    Message.warning('上次回复还未结束，请稍等')
  }

  try {
    //3.提取用户的输入信息
    const humanQuery = query.value
    messages.value.push({
      role: 'human',
      content: humanQuery,
    })
    //4.清空输入框
    query.value = ''

    //5. 发起请求
    isLoading.value = true
    const response = await debugApp(route.params.app_id as string, humanQuery)
    const content = response.data.content
    messages.value.push({
      role: 'ai',
      content: content,
    })
    isLoading.value = false
  } finally {
    isLoading.value = false
  }
}
</script>

<template>
  <!-- 最外层容器，高度撑满整个浏览器屏幕 -->
  <div class="min-h-screen">
    <!-- 顶部导航 -->
    <header class="flex items-center h-[74px] bg-gray-100 border-b border-gray-200 px-4">
      顶部导航
    </header>
    <!--  底部内容区  -->
    <div class="flex flex-row h-[calc(100vh-74px)]">
      <!-- 左侧的编排 -->
      <div class="w-2/3 bg-gray-50 h-full">
        <header class="flex items-center h-16 border-gray-200 px-7 text-xl text-gray-700">
          应用编排
        </header>
        <div class="flex flex-row h-[calc(100%-64px)]">
          <div class="flex-1 border-r border-gray-200 p-6">人设与回复逻辑</div>
          <div class="flex-1 p-6">应用能力</div>
        </div>
      </div>
      <!-- 右侧的调试与预览-->
      <div class="flex flex-col w-1/3 bg-white h-full">
        <!-- 调试与预览-->
        <header
          class="flex flex-shrink-0 items-center h-16 px-4 text-xl bg-white border-b border-gray-200 shadow-sm"
        >
          调试与预览
        </header>
        <!-- 调试对话界面 -->
        <div class="h-full min-h-0 px-6 py-7 overflow-x-hidden overflow-y-scroll scrollbar-w-none">
          <!-- 消息 -->
          <div class="flex flex-row gap-2 mb-6" v-for="message in messages" :key="message.content">
            <!--人头像-->
            <a-avatar
              v-if="message.role == 'human'"
              :style="{ backgroundColor: '#3370ff' }"
              :size="30"
              class="flex-shrink-0"
            >
              越
            </a-avatar>
            <!--AI头像-->
            <a-avatar
              v-else
              :size="30"
              class="flex-shrink-0"
              :style="{ backgroundColor: '#00d0b6' }"
            >
              <icon-apps />
            </a-avatar>
            <!-- 用户名字 + 实际消息-->
            <div class="flex flex-col gap-2">
              <div class="font-semibold text-gray-700">
                {{ message.role === 'human' ? 'Y哥' : 'ChatGPT聊天机器人' }}
              </div>
              <div
                v-if="message.role === 'human'"
                class="max-w-max bg-blue-700 text-white border border-blue-800 px-4 py-3 rounded-2xl leading-5"
              >
                {{ message.content }}
              </div>
              <div
                v-else
                class="max-w-max bg-gray-100 text-gray-900 border border-gray-200 px-4 py-3 rounded-2xl leading-5"
              >
                {{ message.content }}
              </div>
            </div>
          </div>
          <!-- 当没有内容的时候默认放个默认内容 -->
          <div
            v-if="!messages.length"
            class="mt-[200px] flex flex-col items-center justify-center gap-2"
          >
            <a-avatar :size="70" shape="square" :style="{ backgroundColor: '#00d0b6' }">
              <icon-apps />
            </a-avatar>
            <div class="text-2xl font-semibold text-gray-900 mt-2">ChatGPT聊天机器人</div>
          </div>
          <!-- AI加载状态 -->
          <div v-if="isLoading" class="flex flex-row gap-2 mb-6">
            <!--头像-->
            <a-avatar :size="30" class="flex-shrink-0" :style="{ backgroundColor: '#00d0b6' }">
              <icon-apps />
            </a-avatar>
            <!-- 用户名字 + 实际消息-->
            <div class="flex flex-col gap-2">
              <div class="font-semibold text-gray-700">ChatGPT聊天机器人</div>
              <div
                class="max-w-max bg-gray-100 text-gray-900 border border-gray-200 px-4 py-3 rounded-2xl leading-5"
              >
                <icon-loading></icon-loading>
              </div>
            </div>
          </div>
        </div>
        <div class="w-full flex-shrink-0 flex flex-col">
          <!--输入框-->
          <div class="px-6 gap-4 flex items-center">
            <!--清除按钮-->
            <a-button class="flex-shrink-0" type="text" shape="circle" @click="clearMessage">
              <template #icon>
                <icon-empty size="16px" :style="{ color: '#374151' }" />
              </template>
            </a-button>
            <div
              class="h-[50px] flex items-center gap-2 px-4 flex-1 border border-gray-200 rounded-full"
            >
              <input type="text" class="flex-1 outline-0" v-model="query" @keyup.enter="send" />
              <a-button type="text" shape="circle">
                <template #icon>
                  <icon-plus-circle size="16px" :style="{ color: '#374151' }" />
                </template>
              </a-button>
              <a-button type="text" shape="circle" @click="send" :disabled="isLoading">
                <template #icon>
                  <icon-send size="16px" :style="{ color: '#1d4ed8' }" />
                </template>
              </a-button>
            </div>
          </div>
          <!--底部提示文字-->
          <div class="text-center text-gray-500 text-xs py-4">
            内容由AI生成，无法确保真实准确，仅供参考。
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped></style>
