<template>
  <view class="container">
    <!-- 航班列表 -->
    <view class="flight-list">
      <view 
        v-for="flight in flightList" 
        :key="flight.flight_no"
        class="flight-item"
        @click="selectFlight(flight)"
      >
        <view class="flight-header">
          <text class="airline">{{ flight.airline }}</text>
          <text class="flight-no">{{ flight.flight_no }}</text>
        </view>
        
        <view class="flight-info">
          <view class="route">
            <text class="departure">{{ flight.departure }}</text>
            <text class="arrow">→</text>
            <text class="destination">{{ flight.destination }}</text>
          </view>
          <text class="period">{{ flight.period }}</text>
        </view>
        
      </view>
    </view>

    <!-- 抽屉式弹窗 -->
    <uni-drawer 
      ref="drawer" 
      mode="right" 
      :width="400"
      @change="onDrawerChange"
    >
      <view class="drawer-content" v-if="selectedFlight">
        <!-- 航班信息 -->
        <view class="selected-flight">
          <text class="title">航班信息</text>
          <view class="flight-detail">
            <text>{{ selectedFlight.airline }} {{ selectedFlight.flight_no }}</text>
            <text>{{ selectedFlight.departure }} → {{ selectedFlight.destination }}</text>
            <text>{{ selectedFlight.period }}</text>
          </view>
        </view>

        <!-- 已添加旅客列表 -->
        <view class="Traveller-list">
          <text class="title">已添加旅客 ({{ currentTravellers.length }})</text>
          <view 
            v-for="Traveller in currentTravellers" 
            :key="Traveller.id"
            class="Traveller-item"
          >
            <text class="travellerName">{{ Traveller.travellerName }}</text>
            <text class="travellerId">{{ Traveller.travellerId }}</text>
            <uni-icons 
              type="close" 
              size="20" 
              color="#ff0000" 
              @click="removeTraveller(Traveller.id)"
            />
          </view>
          
          <view v-if="currentTravellers.length === 0" class="empty">
            <text>暂无旅客信息</text>
          </view>
        </view>

  
        <!-- 操作按钮 -->
        <view class="action-section">
          <!-- 添加旅客按钮 -->
          <button class="action-btn secondary" @tap="showAddTravellerModal">
            <uni-icons type="plus" size="16" color="#007AFF" />
            <text>添加旅客</text>
          </button>
          
          <button class="action-btn secondary" @tap="showCreateTravellerModal">
            <uni-icons type="personadd" size="16" color="#007AFF" />
            <text>创建旅客</text>
          </button>

          <button class="action-btn primary" @tap="handlePurchase">
            <uni-icons type="cart" size="16" color="#fff" />
            <text>立即购买 ({{ currentTravellers.length }})</text>
          </button>
        </view>
		
      </view>
    </uni-drawer>

    <!-- 添加旅客弹窗 -->
    <uni-popup ref="addPopup" type="dialog">
      <uni-popup-dialog 
        type="info" 
        title="添加旅客" 
        message="请选择要添加的旅客"
        :duration="0"
        @confirm="confirmAddTraveller"
      >
        <view class="popup-content">
          <view class="available-Travellers">
            <text class="sub-title">可选旅客列表</text>
            <radio-group @change="onTravellerSelect">
              <label 
                v-for="Traveller in availableTravellers" 
                :key="Traveller.id"
                class="Traveller-option"
              >
                <radio :value="Traveller.id" />
                <text>{{ Traveller.travellerName }} - {{ Traveller.travellerId }}</text>
              </label>
            </radio-group>
          </view>
        </view>
      </uni-popup-dialog>
    </uni-popup>

    <!-- 创建旅客弹窗 -->
    <uni-popup ref="createPopup" type="dialog">
      <uni-popup-dialog 
        type="info" 
        title="创建旅客" 
        message="请输入旅客信息"
        :duration="0"
        @confirm="confirmCreateTraveller"
      >
	  
        <view class="popup-content">
          <view class="form-item">
            <text class="label">姓名</text>
            <input v-model="newTraveller.name" placeholder="请输入姓名" class="input" />
          </view>
		  
          <view class="form-item">
            <text class="label">身份证号</text>
            <input v-model="newTraveller.idCard" placeholder="请输入身份证号" class="input" />
          </view>
		  
		  <view class="form-item">
		    <text class="label">电话</text>
		    <input v-model="newTraveller.tel" placeholder="请输入电话号" class="input" />
		  </view>
		  
          <!-- <view class="form-item">
            <text class="label">旅客类型</text>
            <picker 
              @change="onTypeChange" 
              :value="typeIndex" 
              :range="TravellerTypes"
            >
              <view class="picker">{{ newTraveller.type || '请选择旅客类型' }}</view>
            </picker>
          </view> -->
        </view>
      </uni-popup-dialog>
    </uni-popup>
  </view>
</template>

<script setup>
	
import { ref, reactive, onMounted, computed } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import { base_url } from "../../../config";

// 响应式数据
const flightList = ref([])
const selectedFlight = ref(null)
const drawer = ref(null)
const addPopup = ref(null)
const createPopup = ref(null)
const showAddTraveller = ref(false)
const showCreateTraveller = ref(false)
const selectedTravellerId = ref('')
const typeIndex = ref(0)

// 可选旅客
const availableTravellers = ref([])

const showAddTravellerModal = () => {
  if (!addPopup.value) {
    return
  }
  
  try {
    selectedTravellerId.value = ''

    addPopup.value.open()
  } catch (error) {
  }
}

const showCreateTravellerModal = () => {
  if (!createPopup.value) {
    return
  }
  Object.assign(newTraveller, { name: '', idCard: ''})
  typeIndex.value = 0
  createPopup.value.open()
}

// 当前航班已添加的旅客
const currentTravellers = ref([])

// 新旅客信息
const newTraveller = reactive({
  name: '',
  idCard: '',
  tel:''
})

// 计算属性 - 获取航班旅客数量
const getTravellerCount = (flightNo) => {
  const Travellers = flightTravellers.value[flightNo] || []
  return Travellers.length
}

// 航班旅客映射
const flightTravellers = ref({})

onLoad((options) => {
  if (options.flightData) {
    try {
      const flightData = JSON.parse(decodeURIComponent(options.flightData))
      flightList.value = flightData.data || []  // 提取航班列表
    } catch (e) {
      console.error('数据解析错误:', e)
      uni.showToast({ title: '数据加载失败', icon: 'none' })
    }
  }
})


// 选择航班
const selectFlight = async (flight) => {
	
	uni.showLoading({
		title: '加载中...'
	});
	
  selectedFlight.value = flight
  
  try {
	  const result = await uni.request({
	  	  url: base_url + 'api/travellers/user/',
	  	  method: 'GET',
	  	  });
	  	
	  	if (result.data.code === 200) {
	  		availableTravellers.value = result.data.data || [];
			}
		} catch (error) {
	  uni.showToast({ title: '无旅客创建', icon: 'none' })
  }
  
  try {
  	  const result = await uni.request({
  	  	  url: base_url + 'api/travellers/user/'+ flight.flight_no,
  	  	  method: 'GET',
  	  	  });
  	  	
  	  	if (result.data.code === 200) {
  	  		flightTravellers.value[flight.flight_no] = result.data.data || [];
			}
		}catch(error){
  	  uni.showToast({ title: '无旅客已添加', icon: 'none' })
  }
  
  uni.hideLoading();

  // 获取该航班已添加的旅客
  currentTravellers.value = flightTravellers.value[flight.flight_no] || []
  // 打开抽屉
  drawer.value.open()
}

// 抽屉状态变化
const onDrawerChange = (e) => {
  if (!e) {
    // 抽屉关闭时清空选择
    selectedFlight.value = null
  }
}

// 添加旅客
const confirmAddTraveller = () => {
  if (!selectedTravellerId.value) {
    uni.showToast({ title: '请选择旅客', icon: 'none' })
    return
  }
  
  const Traveller = availableTravellers.value.find(p => p.id === selectedTravellerId.value)
  if (Traveller && selectedFlight.value) {
    addTravellerToFlight(selectedFlight.value.flight_no, Traveller)
    uni.showToast({ title: '添加成功', icon: 'success' })
    addPopup.value.close()
  }
}

// 创建旅客
const confirmCreateTraveller = async () => {
  if (!newTraveller.name || !newTraveller.idCard || !newTraveller.tel) {
    uni.showToast({ title: '请填写完整信息', icon: 'none' })
    return
  }
  
  try {
	const userInfo = uni.getStorageSync('userInfo');
    // 调用后端创建旅客接口
    const result = await uni.request({
      url: base_url + 'api/travellers/',
      method: 'POST',
      data: {
		  "traveller_name": newTraveller.name,
		  "traveller_id": newTraveller.idCard,
		  "traveller_tel": newTraveller.tel,
		  "uid": userInfo.uid
      }
    });
    if (result.data.code === 201) {
      // 创建成功后添加到当前航班
      if (selectedFlight.value) {
        addTravellerToFlight(selectedFlight.value.flight_no, result.data)
        uni.showToast({ title: '创建并添加成功', icon: 'success' })
        createPopup.value.close()
        // 重置表单
        Object.assign(newTraveller, { name: '', idCard: '', type: '' })
      }
    }
  } catch (error) {
    uni.showToast({ title: '创建失败', icon: 'none' })
  }
}

// 旅客选择
const onTravellerSelect = (e) => {
  selectedTravellerId.value = e.detail.value
}

// 移除旅客
const removeTraveller = (TravellerId) => {
  if (selectedFlight.value) {
    const flightNo = selectedFlight.value.flight_no
    if (flightTravellers.value[flightNo]) {
      flightTravellers.value[flightNo] = flightTravellers.value[flightNo].filter(
        p => p.id !== TravellerId
      )
      currentTravellers.value = flightTravellers.value[flightNo]
    }
  }
}

// 添加到航班
const addTravellerToFlight = (flightNo, Traveller) => {
  if (!flightTravellers.value[flightNo]) {
    flightTravellers.value[flightNo] = []}
  
  // 检查是否已添加
  const exists = flightTravellers.value[flightNo].some(p => p.id === Traveller.id)
  if (!exists) {
    flightTravellers.value[flightNo].push(Traveller)
    currentTravellers.value = flightTravellers.value[flightNo]
  }
}

// 购买操作
const handlePurchase = async () => {
  if (!selectedFlight.value) {
	  return}
  
  if (currentTravellers.value.length === 0) {
    uni.showToast({ title: '请至少添加一位旅客', icon: 'none' })
    return
  }
  
  try {
	  
	for (const traveller of currentTravellers.value) {
		// 调用购买接口
		console.log(traveller.travellerId)
		const result = await uni.request({
		  url: base_url + 'api/travellers/',
		  method: 'PUT',
		  data: {
		      "flight_no":selectedFlight.value.flight_no,
			  "traveller_id":traveller.travellerId
		  }
		});
	}

  } catch (error) {
    uni.showToast({ title: '购买失败', icon: 'none' })
  }
  
  uni.showToast({ title: '购买成功', icon: 'success' })
  drawer.value.close()
  // 跳转到订单页面或其他处理
  
}

// 获取事件通道
const getEventChannel = () => {
  return uni.getCurrentPages()[uni.getCurrentPages().length - 1].getOpenerEventChannel()
}
</script>

<style scoped>
.container {
  padding: 30rpx;
  background-color: #f5f5f5;
  min-height: 100vh;
}

.flight-list {
  margin-bottom: 30rpx;
}

.flight-item {
  background: white;
  border-radius: 16rpx;
  padding: 30rpx;
  margin-bottom: 20rpx;
  box-shadow: 0 4rpx 12rpx rgba(0,0,0,0.1);
}

.flight-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30rpx;
}

.airline {
  font-size: 32rpx;
  font-weight: bold;
  color: #333;
}

.flight-no {
  font-size: 28rpx;
  color: #666;
}

.flight-info {
  margin-bottom: 20rpx;
}

.route {
  display: flex;
  align-items: center;
  margin-bottom: 10rpx;
}

.departure, .destination {
  font-size: 36rpx;
  font-weight: bold;
  color: #007AFF;
}

.arrow {
  margin: 0 20rpx;
  color: #666;
}

.period {
  font-size: 28rpx;
  color: #999;
}

.Traveller-count {
  font-size: 26rpx;
  color: #666;
}

/* 抽屉样式 */
.drawer-content {
  padding: 40rpx;
}

.title {
  font-size: 32rpx;
  font-weight: bold;
  margin-bottom: 20rpx;
  display: block;
}

.selected-flight {
  margin-bottom: 40rpx;
  padding-bottom: 30rpx;
  border-bottom: 2rpx solid #eee;
}

.flight-detail {
  background: #f8f9fa;
  padding: 20rpx;
  border-radius: 8rpx;
}

.flight-detail text {
  display: block;
  margin-bottom: 10rpx;
  font-size: 28rpx;
}

.Traveller-list {
  margin-bottom: 40rpx;
}

.Traveller-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20rpx;
  background: #f8f9fa;
  border-radius: 8rpx;
  margin-bottom: 15rpx;
}

.Traveller-item text {
  flex: 1;
  font-size: 28rpx;
}

.empty {
  text-align: center;
  padding: 40rpx;
  color: #999;
}

.action-buttons {
  display: flex;
  flex-direction: column;
  gap: 20rpx;
}

.btn {
  height: 80rpx;
  border-radius: 40rpx;
  font-size: 32rpx;
  border: none;
}

.add-btn {
  background: #007AFF;
  color: white;
}

.create-btn {
  background: #007AFF;
  color: white;
}

.buy-btn {
  background: #007AFF;
  color: white;
}

/* 弹窗样式 */
.popup-content {
  padding: 30rpx 0;

}

.sub-title {
  font-size: 28rpx;
  font-weight: bold;
  margin-bottom: 20rpx;
  display: block;
}

.Traveller-option {
  display: flex;
  align-items: center;
  padding: 20rpx 0;
  border-bottom: 1rpx solid #eee;
}

.form-item {
  margin-bottom: 30rpx;
}

.label {
  display: block;
  margin-bottom: 10rpx;
  font-size: 28rpx;
  color: #333;
}

.input {
  border: 2rpx solid #ddd;
  border-radius: 8rpx;
  padding: 20rpx;
  font-size: 28rpx;
  width: 100%;
}

.picker {
  border: 2rpx solid #ddd;
  border-radius: 8rpx;
  padding: 20rpx;
  font-size: 28rpx;
}

/* 确保popup在drawer之上 */
:deep(.uni-popup) {
  z-index: 1002 !important;
}

:deep(.uni-drawer) {
  z-index: 1001 !important;
}

</style>