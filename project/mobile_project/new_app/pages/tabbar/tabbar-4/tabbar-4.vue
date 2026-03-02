<template>
  <view class="container">
    <!-- 页面标题 -->
    <view class="header">
      <text class="title">航班行李管理</text>
      <text class="subtitle">管理旅客的航班和行李信息</text>
    </view>

    <!-- 航班列表 -->
    <scroll-view 
      class="flight-list" 
      scroll-y 
      refresher-enabled 
      :refresher-triggered="refreshing"
      @refresherrefresh="onRefresh">
      
      <!-- 加载状态 -->
      <view v-if="loading" class="loading-container">
        <uni-load-more status="loading" content="正在加载航班信息..."></uni-load-more>
      </view>
      
      <!-- 空状态 -->
      <view v-else-if="flights.length === 0" class="empty-container">
        <uni-icons type="info" size="60" color="#ccc"></uni-icons>
        <text class="empty-text">暂无航班订单</text>
        <button class="refresh-btn" @tap="fetchFlights">重新加载</button>
      </view>
      
      <!-- 航班列表 -->
      <view v-else>
        <view 
          v-for="flight in flights" 
          :key="flight.travellerId + flight.flightNo"
          class="flight-card"
          @tap="showTravellerDetail(flight)">
          
          <view class="flight-header">
            <text class="flight-no">{{ flight.flightNo }}</text>
            <view class="traveller-info">
              <uni-icons type="person" size="14" color="#666"></uni-icons>
              <text class="traveller-id">旅客ID: {{ flight.travellerId }}</text>
            </view>
          </view>
          
          <view class="flight-footer">
            <text class="action-text">点击管理行李</text>
            <uni-icons type="arrowright" size="16" color="#999"></uni-icons>
          </view>
        </view>
      </view>
    </scroll-view>

    <!-- 旅客详情弹窗 -->
    <uni-popup ref="detailPopup" type="center" background-color="#fff">
      <view class="popup-content">
        <view class="popup-header">
          <text class="popup-title">行李管理</text>
          <uni-icons 
            type="close" 
            size="20" 
            color="#999" 
            @tap="closeDetailPopup">
          </uni-icons>
        </view>
        
        <!-- 旅客信息 -->
        <view class="traveller-info-section">
          <text class="info-label">航班号: {{ currentTraveller.flightNo }}</text>
          <text class="info-label">旅客ID: {{ currentTraveller.travellerId }}</text>
        </view>
        
        <!-- 行李列表 -->
        <view class="luggage-section">
          <view class="section-header">
            <text class="section-title">行李记录</text>
            <button class="add-btn" @tap="showAddLuggageModal">
              <uni-icons type="plus" size="14" color="#fff"></uni-icons>
              添加行李
            </button>
          </view>
          
          <view v-if="currentLuggage.length === 0" class="no-luggage">
            <text class="no-data-text">暂无行李记录</text>
          </view>
          
          <view v-else class="luggage-list">
            <view 
              v-for="luggage in currentLuggage" 
              :key="luggage.id"
              class="luggage-item">
              
              <view class="luggage-info">
                <text class="luggage-id">行李ID: {{ luggage.id }}</text>
                <view class="luggage-details">
                  <view class="type-badge" :class="getTypeClass(luggage.type)">
                    {{ getTypeText(luggage.type) }}
                  </view>
                  <view class="status-badge" :class="getStatusClass(luggage.status)">
                    {{ getStatusText(luggage.status) }}
                  </view>
                </view>
              </view>
              
<!--              <view class="luggage-actions">
                <text class="create-time">{{ formatTime(luggage.create_time) }}</text>
              </view> -->
            </view>
          </view>
        </view>
        
        <view class="popup-footer">
          <button class="close-btn" @tap="closeDetailPopup">关闭</button>
        </view>
      </view>
    </uni-popup>

    <!-- 添加行李弹窗 -->
    <uni-popup ref="addLuggagePopup" type="center" background-color="#fff">
      <view class="add-luggage-content">
        <view class="popup-header">
          <text class="popup-title">添加行李记录</text>
          <uni-icons 
            type="close" 
            size="20" 
            color="#999" 
            @tap="closeAddLuggageModal">
          </uni-icons>
        </view>
        
        <view class="form-content">
          
          <!-- 行李类型下拉选择 -->
          <view class="form-item">
            <text class="form-label">行李类型 <text class="required">*</text></text>
            <view class="select-wrapper">
              <picker 
                class="type-select"
                :value="newLuggage.type" 
                :range="baggageTypeOptions"
                range-key="label"
                @change="onTypeChange">
                <view class="select-display">
                  <text class="select-text" :class="{ 'placeholder-text': !newLuggage.type }">
                    {{ getSelectedTypeText() || '请选择行李类型' }}
                  </text>
                  <uni-icons type="arrowdown" size="16" color="#666"></uni-icons>
                </view>
              </picker>
            </view>
          </view>
          
          <view class="tips">
            <uni-icons type="info" size="14" color="#ff6b35"></uni-icons>
            <text class="tips-text">系统将自动为行李分配ID和初始状态</text>
          </view>
        </view>
        
        <view class="popup-footer">
          <button class="cancel-btn" @tap="closeAddLuggageModal">取消</button>
          <button class="confirm-btn" :disabled="!newLuggage.type" @tap="createLuggage">确认添加</button>
        </view>
      </view>
    </uni-popup>
  </view>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { base_url } from "../../../config";

// 行李类型选项
const baggageTypeOptions = ref([
  { value: '0', label: '托运' },
  { value: '1', label: '随身携带' }
])

// 响应式数据
const flights = ref([]) // 航班列表
const currentTraveller = ref({}) // 当前选中的旅客
const currentLuggage = ref([]) // 当前旅客的行李列表
const loading = ref(false)
const refreshing = ref(false)
const detailPopup = ref(null)
const addLuggagePopup = ref(null)

// 新行李记录
const newLuggage = ref({
  traveller_id: '',
  flight_no: '',
  type: '' // 行李类型：0-托运，1-随身携带
})

// 获取航班列表
const fetchFlights = async () => {
  loading.value = true
  try {
	  const result = await uni.request({
	  		url: base_url + 'api/users/flights',
	  		method: 'GET',
	  		});
	  		  	
	  	if (result.data.code === 200) {
	  		flights.value = result.data.data || [];
	  		}
  } catch (error) {
    console.error('获取航班数据失败:', error)
    uni.showToast({
      title: '获取航班信息失败',
      icon: 'none'
    })
  } finally {
    loading.value = false
    refreshing.value = false
  }
}

// 获取行李状态
const fetchLuggageStatus = async (travellerId) => {
  try {
	  
    const result = await uni.request({
      url: base_url + 'api/baggage/status',
      method: 'POST',
      data: {
        traveller_id: travellerId
      }
    })
    
	const Data = ref([])
	if (result.data.code === 200) {
		Data.value = result.data.data || [];
	}
    
    console.log('行李状态获取成功:', Data)
    return Data.value
  } catch (error) {
    console.error('获取行李状态失败:', error)
    uni.showToast({
      title: '获取行李状态失败',
      icon: 'none'
    })
    return []
  }
}

// 创建行李记录
const createLuggage = async () => {
  if (!newLuggage.value.type) {
    uni.showToast({
      title: '请选择行李类型',
      icon: 'none'
    })
    return
  }
  
  try {
	  console.log(currentTraveller.travellerId)
    const result = await uni.request({
      url: base_url + 'api/baggage/',
      method: 'POST',
      data: {
        traveller_id: currentTraveller.value.travellerId,
        flight_no: currentTraveller.value.flightNo,
        type: newLuggage.value.type
      }
    })
    
    // 模拟响应数据 - 实际使用时应删除
    const data = ref()
	data.value = result.data.data
    
	if(result.data.code === 201){
		uni.showToast({
		  title: '行李记录创建成功',
		  icon: 'success'
		})
	}
    
    // 刷新行李列表
    currentLuggage.value = await fetchLuggageStatus(newLuggage.value.traveller_id)
    closeAddLuggageModal()
    
  } catch (error) {
    console.error('创建行李记录失败:', error)
    uni.showToast({
      title: '创建行李记录失败',
      icon: 'none'
    })
  }
}

// 行李类型选择变化
const onTypeChange = (e) => {
  const selectedIndex = e.detail.value
  newLuggage.value.type = baggageTypeOptions.value[selectedIndex].value
}

// 获取选中的行李类型文本
const getSelectedTypeText = () => {
  const selectedType = baggageTypeOptions.value.find(
    option => option.value === newLuggage.value.type
  )
  return selectedType ? selectedType.label : ''
}

// 获取行李类型文本
const getTypeText = (type) => {
  const typeMap = {
    '0': '托运',
    '1': '随身携带'
  }
  return typeMap[type] || '未知类型'
}

// 获取行李类型样式类
const getTypeClass = (type) => {
  const classMap = {
    '1': 'type-checked',
    '2': 'type-carry'
  }
  return classMap[type] || 'type-checked'
}

// 显示旅客详情
const showTravellerDetail = async (traveller) => {
  currentTraveller.value = traveller
  newLuggage.value = {
    traveller_id: traveller.travellerId,
    flight_no: traveller.flightNo,
    type: '' // 重置类型选择
  }
  
  // 获取行李状态
  currentLuggage.value = await fetchLuggageStatus(traveller.travellerId)
  // 显示弹窗
  detailPopup.value.open()
}

// 关闭详情弹窗
const closeDetailPopup = () => {
  detailPopup.value.close()
}

// 显示添加行李弹窗
const showAddLuggageModal = () => {
  addLuggagePopup.value.open()
}

// 关闭添加行李弹窗
const closeAddLuggageModal = () => {
  newLuggage.value.type = '' // 清空类型选择
  addLuggagePopup.value.close()
}

// 获取状态文本
const getStatusText = (status) => {
  const statusMap = {
    '0': '待检验',
    '1': '已通过',
    '2': '未通过'
  }
  return statusMap[status] || '未知状态'
}

// 获取状态样式类
const getStatusClass = (status) => {
  const classMap = {
    '0': 'status-pending',
    '1': 'status-passed',
    '2': 'status-failed'
  }
  return classMap[status] || 'status-pending'
}

// 格式化时间
const formatTime = (time) => {
  if (!time) return ''
  const date = new Date(time)
  return `${date.getFullYear()}-${(date.getMonth() + 1).toString().padStart(2, '0')}-${date.getDate().toString().padStart(2, '0')} ${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}`
}

// 下拉刷新
const onRefresh = () => {
  refreshing.value = true
  fetchFlights()
}

// 页面加载时获取数据
onMounted(() => {
  fetchFlights()
})
</script>

<style scoped>
.container {
  padding: 20rpx;
  min-height: 100vh;
  background-color: #f5f5f5;
}

.header {
  text-align: center;
  padding: 30rpx 0;
}

.title {
  display: block;
  font-size: 36rpx;
  font-weight: bold;
  color: #333;
  margin-bottom: 10rpx;
}

.subtitle {
  font-size: 26rpx;
  color: #666;
}

.flight-list {
  height: calc(100vh - 200rpx);
}

.loading-container,
.empty-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 100rpx 0;
}

.empty-text {
  margin: 20rpx 0;
  font-size: 28rpx;
  color: #999;
}

.refresh-btn {
  margin-top: 20rpx;
  background: #007aff;
  color: white;
  border: none;
  border-radius: 10rpx;
  padding: 20rpx 40rpx;
  font-size: 26rpx;
}

.flight-card {
  background: white;
  border-radius: 16rpx;
  padding: 30rpx;
  margin-bottom: 20rpx;
  box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.05);
}

.flight-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20rpx;
}

.flight-no {
  font-size: 32rpx;
  font-weight: bold;
  color: #333;
}

.traveller-info {
  display: flex;
  align-items: center;
  gap: 8rpx;
}

.traveller-id {
  font-size: 26rpx;
  color: #666;
}

.flight-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.action-text {
  font-size: 26rpx;
  color: #999;
}

/* 弹窗样式 */
.popup-content {
  width: 700rpx;
  max-height: 80vh;
  padding: 40rpx;
  border-radius: 20rpx;
}

.popup-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30rpx;
}

.popup-title {
  font-size: 32rpx;
  font-weight: bold;
  color: #333;
}

.traveller-info-section {
  margin-bottom: 30rpx;
}

.info-label {
  display: block;
  font-size: 28rpx;
  color: #666;
  margin-bottom: 10rpx;
}

.luggage-section {
  margin-bottom: 30rpx;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20rpx;
}

.section-title {
  font-size: 28rpx;
  font-weight: bold;
  color: #333;
}

.add-btn {
  background: #007aff;
  color: white;
  border: none;
  border-radius: 8rpx;
  padding: 12rpx 20rpx;
  font-size: 24rpx;
  display: flex;
  align-items: center;
  gap: 6rpx;
}

.no-luggage {
  text-align: center;
  padding: 40rpx 0;
}

.no-data-text {
  font-size: 26rpx;
  color: #999;
}

.luggage-list {
  max-height: 300rpx;
  overflow-y: auto;
}

.luggage-item {
  background: #f8f9fa;
  border-radius: 12rpx;
  padding: 20rpx;
  margin-bottom: 15rpx;
}

.luggage-info {
  margin-bottom: 10rpx;
}

.luggage-id {
  font-size: 26rpx;
  color: #333;
  margin-bottom: 8rpx;
}

.luggage-details {
  display: flex;
  gap: 10rpx;
  align-items: center;
}

.type-badge {
  padding: 4rpx 12rpx;
  border-radius: 8rpx;
  font-size: 20rpx;
  font-weight: bold;
}

.type-checked {
  background-color: #e6f7ff;
  color: #1890ff;
  border: 1rpx solid #91d5ff;
}

.type-carry {
  background-color: #f6ffed;
  color: #52c41a;
  border: 1rpx solid #b7eb8f;
}

.status-badge {
  padding: 4rpx 12rpx;
  border-radius: 8rpx;
  font-size: 20rpx;
  font-weight: bold;
}

.status-pending {
  background-color: #fff3cd;
  color: #856404;
}

.status-passed {
  background-color: #d4edda;
  color: #155724;
}

.status-failed {
  background-color: #f8d7da;
  color: #721c24;
}

.luggage-actions {
  text-align: right;
}

.create-time {
  font-size: 22rpx;
  color: #999;
}

.popup-footer {
  text-align: right;
}

.close-btn {
  background: #6c757d;
  color: white;
  border: none;
  border-radius: 10rpx;
  padding: 20rpx 40rpx;
  font-size: 28rpx;
}

/* 添加行李弹窗样式 */
.add-luggage-content {
  width: 600rpx;
  padding: 40rpx;
  border-radius: 20rpx;
}

.form-content {
  margin: 30rpx 0;
}

.form-item {
  margin-bottom: 30rpx;
}

.form-label {
  display: block;
  font-size: 28rpx;
  color: #333;
  margin-bottom: 10rpx;
}

.required {
  color: #ff4d4f;
}

.form-input {
  width: 100%;
  padding: 20rpx;
  border: 1rpx solid #ddd;
  border-radius: 10rpx;
  font-size: 28rpx;
}

/* 下拉选择器样式 */
.select-wrapper {
  width: 100%;
}

.type-select {
  width: 100%;
}

.select-display {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20rpx;
  border: 1rpx solid #ddd;
  border-radius: 10rpx;
  background: #fff;
}

.select-text {
  font-size: 28rpx;
  color: #333;
}

.placeholder-text {
  color: #999;
}

.tips {
  display: flex;
  align-items: center;
  gap: 8rpx;
  margin-top: 20rpx;
  padding: 15rpx;
  background: #fff3cd;
  border-radius: 8rpx;
}

.tips-text {
  font-size: 24rpx;
  color: #856404;
}

.popup-footer {
  display: flex;
  gap: 20rpx;
  justify-content: flex-end;
}

.cancel-btn {
  background: #6c757d;
  color: white;
  border: none;
  border-radius: 10rpx;
  padding: 20rpx 30rpx;
  font-size: 28rpx;
}

.confirm-btn {
  background: #007aff;
  color: white;
  border: none;
  border-radius: 10rpx;
  padding: 20rpx 30rpx;
  font-size: 28rpx;
}

.confirm-btn:disabled {
  background: #ccc;
  color: #999;
}

/* 响应式调整 */
@media (max-width: 750px) {
  .popup-content,
  .add-luggage-content {
    width: 90vw;
    margin: 0 auto;
  }
}
</style>