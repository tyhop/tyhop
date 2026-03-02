<template>
  <view class="container">
    <!-- 头部标题 -->
    <view class="header">
      <view class="logo-section">
        <view class="logo">AI</view>
        <text class="title">美食攻略</text>
      </view>
<!--      <text class="subtitle">对您行李中的物品进行问答</text> -->
    </view>

    <!-- 对话区域 -->
    <scroll-view class="chat-container" scroll-y :scroll-top="scrollTop" scroll-with-animation>
      <view class="chat-messages">
        <!-- 欢迎消息 -->
        <view class="message-wrapper assistant-message" v-if="messages.length === 0">
          <view class="avatar">
            <uni-icons type="staff" size="24" color="#fff"></uni-icons>
          </view>
          <view class="message-content">
            <text class="message-text">您好！您可以对任意城市的特色美食进行提问？</text>
            <text class="message-time">{{ getCurrentTime() }}</text>
          </view>
        </view>

        <!-- 历史消息 -->
        <view v-for="(message, index) in messages" :key="index" 
              class="message-wrapper" 
              :class="message.role === 'user' ? 'user-message' : 'assistant-message'">
          
          <view class="avatar" :class="message.role === 'user' ? 'user-avatar' : 'assistant-avatar'">
            <uni-icons 
              :type="message.role === 'user' ? 'person' : 'staff'" 
              size="20" 
              color="#fff"
            ></uni-icons>
          </view>
          
          <view class="message-content">
            <text class="message-text">{{ message.content }}</text>
            <text class="message-time">{{ message.time }}</text>
          </view>
        </view>

        <!-- 加载状态 -->
        <view class="message-wrapper assistant-message" v-if="loading">
          <view class="avatar assistant-avatar">
            <uni-icons type="staff" size="20" color="#fff"></uni-icons>
          </view>
          <view class="message-content">
            <view class="typing-indicator">
              <view class="typing-dot"></view>
              <view class="typing-dot"></view>
              <view class="typing-dot"></view>
            </view>
            <text class="message-time">正在思考中...</text>
          </view>
        </view>
      </view>
    </scroll-view>

    <!-- 输入区域 -->
    <view class="input-container">
      <view class="input-wrapper">
        <uni-easyinput
          v-model="inputQuestion"
          type="textarea"
          placeholder="请输入您的问题..."
          :maxlength="1000"
          :styles="inputStyles"
          :focus="autoFocus"
          @confirm="sendQuestion"
          class="question-input"
        ></uni-easyinput>
        
        <button 
          class="send-button" 
          :class="{ 'send-button-disabled': !canSend }"
          :disabled="!canSend || loading"
          @click="sendQuestion"
        >
          <uni-icons type="paperplane" size="20" color="#fff"></uni-icons>
          <text v-if="!loading">发送</text>
          <text v-else>发送中</text>
        </button>
      </view>
      
      <view class="input-tips">
        <text class="tip-text">Shift + Enter 换行，Enter 发送</text>
        <text class="word-count">{{ inputQuestion.length }}/1000</text>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref, computed, nextTick } from 'vue'
import { base_url } from "../../../config";

// 响应式数据
const inputQuestion = ref('')
const messages = ref([])
const loading = ref(false)
const scrollTop = ref(0)
const autoFocus = ref(true)

// 计算属性
const canSend = computed(() => {
  return inputQuestion.value.trim().length > 0 && !loading.value
})

// 输入框样式
const inputStyles = ref({
  borderColor: 'transparent',
  color: '#333',
  backgroundColor: '#f7f7f8',
  borderRadius: '20rpx'
})

// 获取当前时间
const getCurrentTime = () => {
  const now = new Date()
  return `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}`
}

// 发送问题
const sendQuestion = async () => {
  if (!canSend.value) return

  const question = inputQuestion.value.trim()
  const currentTime = getCurrentTime()

  // 添加用户消息
  messages.value.push({
    role: 'user',
    content: question,
    time: currentTime
  })

  // 清空输入框
  inputQuestion.value = ''
  
  // 设置加载状态
  loading.value = true
  
  // 滚动到底部
  scrollToBottom()
  console.log(question)
  try {
    // TODO: 替换为实际的后端API调用
    const response = await uni.request({
		  url: base_url + 'api/dify/food',
		  method: 'POST',
		  data: {
			  question: question
		  }
		});
    
    // 添加助手回复
    messages.value.push({
      role: 'assistant',
      content: response.data.data.outputs.text.toString(),
      time: getCurrentTime()
    })
    
  } catch (error) {
    console.error('请求失败:', error)
    
    // 添加错误消息
    messages.value.push({
      role: 'assistant',
      content: '抱歉，我暂时无法回答这个问题。请稍后再试或重新提问。',
      time: getCurrentTime()
    })
    
    uni.showToast({
      title: '请求失败',
      icon: 'none'
    })
  } finally {
    loading.value = false
    scrollToBottom()
  }
}

// 滚动到底部
const scrollToBottom = () => {
  nextTick(() => {
    setTimeout(() => {
      scrollTop.value = 99999 // 设置一个足够大的值确保滚动到底部
    }, 100)
  })
}

// 处理键盘事件（Shift+Enter换行，Enter发送）
const handleKeydown = (event) => {
  if (event.key === 'Enter' && !event.shiftKey) {
    event.preventDefault()
    sendQuestion()
  }
}
</script>

<style scoped>
.container {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
}

.header {
  padding: 60rpx 40rpx 40rpx;
  background: white;
  border-bottom: 1rpx solid #e5e5e5;
}

.logo-section {
  display: flex;
  align-items: center;
  margin-bottom: 16rpx;
}

.logo {
  width: 80rpx;
  height: 80rpx;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 20rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 32rpx;
  font-weight: bold;
  margin-right: 20rpx;
}

.title {
  font-size: 40rpx;
  font-weight: bold;
  color: #333;
}

.subtitle {
  font-size: 26rpx;
  color: #666;
}

.chat-container {
  flex: 1;
  padding: 30rpx;
}

.chat-messages {
  max-width: 1200rpx;
  margin: 0 auto;
}

.message-wrapper {
  display: flex;
  margin-bottom: 40rpx;
  animation: messageSlideIn 0.3s ease-out;
}

.user-message {
  flex-direction: row-reverse;
}

.avatar {
  width: 80rpx;
  height: 80rpx;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  margin: 0 20rpx;
}

.user-avatar {
  background: linear-gradient(135deg, #ff6b6b, #ee5a24);
}

.assistant-avatar {
  background: linear-gradient(135deg, #667eea, #764ba2);
}

.message-content {
  max-width: 70%;
  background: white;
  border-radius: 24rpx;
  padding: 30rpx;
  box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.08);
  position: relative;
}

.user-message .message-content {
  background: linear-gradient(135deg, #1890ff, #096dd9);
  color: white;
}

.message-text {
  font-size: 30rpx;
  line-height: 1.6;
  display: block;
  word-wrap: break-word;
}

.message-time {
  display: block;
  font-size: 22rpx;
  color: #999;
  margin-top: 16rpx;
  opacity: 0.8;
}

.user-message .message-time {
  color: rgba(255, 255, 255, 0.8);
}

/* 输入区域 */
.input-container {
  padding: 30rpx;
  background: white;
  border-top: 1rpx solid #e5e5e5;
}

.input-wrapper {
  display: flex;
  align-items: flex-end;
  gap: 20rpx;
  margin-bottom: 16rpx;
}

.question-input {
  flex: 1;
}

:deep(.question-input .uni-easyinput__content) {
  border-radius: 24rpx !important;
  border: 2rpx solid #e8e8e8 !important;
  min-height: 120rpx;
  padding: 24rpx;
  transition: all 0.3s;
}

:deep(.question-input .uni-easyinput__content:focus-within) {
  border-color: #1890ff !important;
  box-shadow: 0 0 0 4rpx rgba(24, 144, 255, 0.1);
}

:deep(.question-input .uni-textarea-textarea) {
  font-size: 28rpx;
  line-height: 1.6;
}

.send-button {
  background: linear-gradient(135deg, #1890ff, #096dd9);
  border: none;
  border-radius: 16rpx;
  padding: 24rpx 32rpx;
  color: white;
  font-size: 28rpx;
  display: flex;
  align-items: center;
  gap: 8rpx;
  transition: all 0.3s;
  min-width: 140rpx;
  justify-content: center;
}

.send-button:active {
  transform: scale(0.95);
  opacity: 0.9;
}

.send-button-disabled {
  background: #ccc !important;
  transform: none !important;
}

.input-tips {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.tip-text {
  font-size: 24rpx;
  color: #999;
}

.word-count {
  font-size: 24rpx;
  color: #999;
}

/* 打字指示器 */
.typing-indicator {
  display: flex;
  align-items: center;
  gap: 6rpx;
  margin-bottom: 16rpx;
}

.typing-dot {
  width: 12rpx;
  height: 12rpx;
  background: #999;
  border-radius: 50%;
  animation: typingBounce 1.4s infinite ease-in-out;
}

.typing-dot:nth-child(1) { animation-delay: -0.32s; }
.typing-dot:nth-child(2) { animation-delay: -0.16s; }

@keyframes typingBounce {
  0%, 80%, 100% {
    transform: scale(0.8);
    opacity: 0.5;
  }
  40% {
    transform: scale(1);
    opacity: 1;
  }
}

@keyframes messageSlideIn {
  from {
    opacity: 0;
    transform: translateY(20rpx);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 响应式设计 */
@media (max-width: 750px) {
  .header {
    padding: 40rpx 30rpx 30rpx;
  }
  
  .chat-container {
    padding: 20rpx;
  }
  
  .input-container {
    padding: 20rpx;
  }
  
  .message-content {
    max-width: 85%;
  }
  
  .avatar {
    width: 60rpx;
    height: 60rpx;
    margin: 0 16rpx;
  }
}
</style>