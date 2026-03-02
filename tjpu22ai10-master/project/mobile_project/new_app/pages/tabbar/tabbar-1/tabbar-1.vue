<template>
  <view class="container">
    <!-- 页面标题 -->
    <view class="header">
      <text class="title">航班旅行助手</text>
      <text class="subtitle">一站式旅行服务</text>
    </view>
    <!-- 六宫格功能模块 -->
    <view class="grid-container">
      <!-- 第一行 -->
      <view class="grid-row">
        <view class="grid-item" @tap="navigateTo('delay')">
          <view class="item-content">
            <view class="item-icon delay-icon">
              <uni-icons type="chat" size="36" color="#fff"></uni-icons>
            </view>
            <text class="item-title">延误判断</text>
            <text class="item-desc">实时航班状态查询</text>
          </view>
        </view>

        <view class="grid-item" @tap="navigateTo('luggage')">
          <view class="item-content">
            <view class="item-icon luggage-icon">
              <uni-icons type="calendar" size="36" color="#fff"></uni-icons>
            </view>
            <text class="item-title">行李咨询</text>
            <text class="item-desc">行李规定与状态</text>
          </view>
        </view>
      </view>

      <!-- 第二行 -->
      <view class="grid-row">
        <view class="grid-item" @tap="navigateTo('weather')">
          <view class="item-content">
            <view class="item-icon weather-icon">
              <uni-icons type="paperplane" size="36" color="#fff"></uni-icons>
            </view>
            <text class="item-title">天气预报</text>
            <text class="item-desc">目的地天气信息</text>
          </view>
        </view>

        <view class="grid-item" @tap="navigateTo('travel')">
          <view class="item-content">
            <view class="item-icon travel-icon">
              <uni-icons type="map" size="36" color="#fff"></uni-icons>
            </view>
            <text class="item-title">旅游指南</text>
            <text class="item-desc">景点攻略与路线</text>
          </view>
        </view>
      </view>

      <!-- 第三行 -->
      <view class="grid-row">
        <view class="grid-item" @tap="navigateTo('food')">
          <view class="item-content">
            <view class="item-icon food-icon">
              <uni-icons type="shop" size="36" color="#fff"></uni-icons>
            </view>
            <text class="item-title">美食攻略</text>
            <text class="item-desc">当地特色美食推荐</text>
          </view>
        </view>

        <view class="grid-item" @tap="navigateTo('more')">
          <view class="item-content">
            <view class="item-icon more-icon">
              <uni-icons type="more" size="36" color="#fff"></uni-icons>
            </view>
            <text class="item-title">更多功能</text>
            <text class="item-desc">敬请期待</text>
          </view>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup>
import { onLoad } from '@dcloudio/uni-app'

// 页面跳转函数
const navigateTo = (page) => {
  const pageMap = {
    'delay': 'tabbar-1-1',
    'luggage': 'tabbar-1-2',
    'weather': 'tabbar-1-3',
    'travel': 'tabbar-1-4',
    'food': 'tabbar-1-5',
    'more': 'tabbar-1-6'
  }

  const url = pageMap[page]
  
  if (url) {
    uni.navigateTo({
      url: url,
      fail: (err) => {
        console.error('页面跳转失败:', err)
        uni.showToast({
          title: '功能开发中，敬请期待',
          icon: 'none'
        })
      }
    })
  }
}

// 页面加载时执行
onLoad(() => {
  console.log('Tabbar-1 页面加载完成')
})
</script>

<style scoped>
.container {
  padding: 30rpx;
  min-height: 100vh;
  background-color: #f5f7fa;
}

.header {
  text-align: center;
  padding: 40rpx 0 60rpx 0;
}

.title {
  display: block;
  font-size: 48rpx;
  font-weight: bold;
  color: #333;
  margin-bottom: 16rpx;
}

.subtitle {
  font-size: 28rpx;
  color: #666;
}

.grid-container {
  padding: 0 20rpx;
}

.grid-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 30rpx;
  gap: 30rpx;
}

.grid-item {
  flex: 1;
  background: white;
  border-radius: 20rpx;
  padding: 40rpx 0;
  box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
  border: 1rpx solid #f0f0f0;
}

.grid-item:active {
  transform: scale(0.98);
  box-shadow: 0 2rpx 10rpx rgba(0, 0, 0, 0.12);
}

.item-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
}

.item-icon {
  width: 80rpx;
  height: 80rpx;
  border-radius: 20rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 24rpx;
}

/* 不同模块的图标背景色 */
.delay-icon {
  background: linear-gradient(135deg, #ff6b6b, #ff8e8e);
}

.luggage-icon {
  background: linear-gradient(135deg, #4834d4, #686de0);
}

.weather-icon {
  background: linear-gradient(135deg, #00d2d3, #54a0ff);
}

.travel-icon {
  background: linear-gradient(135deg, #10ac84, #1dd1a1);
}

.food-icon {
  background: linear-gradient(135deg, #ff9ff3, #f368e0);
}

.more-icon {
  background: linear-gradient(135deg, #8395a7, #c8d6e5);
}

.item-title {
  display: block;
  font-size: 32rpx;
  font-weight: 600;
  color: #333;
  margin-bottom: 8rpx;
}

.item-desc {
  display: block;
  font-size: 24rpx;
  color: #999;
  line-height: 1.4;
}

/* 响应式设计 */
@media (max-width: 750px) {
  .grid-row {
    flex-direction: column;
    margin-bottom: 0;
    gap: 20rpx;
  }
  
  .grid-item {
    margin-bottom: 20rpx;
    padding: 30rpx 0;
  }
  
  .item-icon {
    width: 70rpx;
    height: 70rpx;
    border-radius: 16rpx;
  }
  
  .item-title {
    font-size: 30rpx;
  }
  
  .item-desc {
    font-size: 22rpx;
  }
}

/* 动画效果 */
.grid-item {
  opacity: 0;
  transform: translateY(30rpx);
  animation: fadeInUp 0.6s ease forwards;
}

.grid-item:nth-child(1) { animation-delay: 0.1s; }
.grid-item:nth-child(2) { animation-delay: 0.2s; }
.grid-item:nth-child(3) { animation-delay: 0.3s; }
.grid-item:nth-child(4) { animation-delay: 0.4s; }
.grid-item:nth-child(5) { animation-delay: 0.5s; }
.grid-item:nth-child(6) { animation-delay: 0.6s; }

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(30rpx);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>