<template>
	<view class="content">
		<view class="search-form">
			<!-- 单程/往返选择 -->
			<view class="trip-type">
				<text 
					:class="['type-item', tripType === 'oneWay' ? 'active' : '']"
					@click="tripType = 'oneWay'"
				>
					单程
				</text>
				<text 
					:class="['type-item', tripType === 'roundTrip' ? 'active' : '']"
					@click="tripType = 'roundTrip'"
				>
					往返
				</text>
			</view>

			<!-- 出发地 -->
			<view class="form-item">
				<text class="label">出发地</text>
				<input 
					class="input" 
					v-model="departureCity" 
					placeholder="请输入出发城市" 
					@focus="showCityPicker = true; pickerType = 'departure'"
				/>
				<text class="icon">↗</text>
			</view>

			<!-- 目的地 -->
			<view class="form-item">
				<text class="label">目的地</text>
				<input 
					class="input" 
					v-model="arrivalCity" 
					placeholder="请输入目的城市" 
					@focus="showCityPicker = true; pickerType = 'arrival'"
				/>
				<text class="icon">↘</text>
			</view>

			<!-- 交换按钮 -->
			<view class="swap-btn" @click="swapCities">
				<text class="swap-icon">⇅</text>
			</view>

			<!-- 出发日期 -->
			<view class="form-item">
				<text class="label">出发日期</text>
				<picker 
					mode="date" 
					:value="departureDate" 
					@change="onDepartureDateChange"
					:start="minDate"
				>
					<view class="picker">{{ departureDate }}</view>
				</picker>
			</view>

			<!-- 返程日期（往返时显示） -->
			<view class="form-item" v-if="tripType === 'roundTrip'">
				<text class="label">返程日期</text>
				<picker 
					mode="date" 
					:value="returnDate" 
					@change="onReturnDateChange"
					:start="departureDate"
				>
					<view class="picker">{{ returnDate }}</view>
				</picker>
			</view>
			
			<!-- 航空公司选择 -->
			<view class="form-item">
				<text class="label">航空公司</text>
				<picker 
					mode="selector" 
					:range="airlines" 
					range-key="name"
					:value="airlineIndex" 
					@change="onAirlineChange"
				>
					<view class="picker">
						{{ selectedAirline?.name || '不限航空公司' }}
						<text class="picker-arrow">▼</text>
					</view>
				</picker>
			</view>


			<!-- 搜索按钮 -->
			<button class="search-btn" @click="searchFlights" :disabled="!canSearch">
				搜索航班
			</button>
		</view>

		<!-- 城市选择器 -->
<!-- 		<uni-popup ref="cityPopup" type="bottom">
			<view class="city-picker">
				<view class="picker-header">
					<text class="picker-title">选择城市</text>
					<text class="picker-close" @click="closeCityPicker">关闭</text>
				</view>
				<scroll-view class="city-list" scroll-y>
					<text 
						v-for="city in popularCities" 
						:key="city.code"
						class="city-item"
						@click="selectCity(city)"
					>
						{{ city.name }}
					</text>
				</scroll-view>
			</view>
		</uni-popup> -->
	</view>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { onLoad } from '@dcloudio/uni-app';
import { base_url } from "../../../config";

// 响应式数据
const airlines = ref([
	{ name: '不限航空公司', code: '' },
	{ name: '中国国际航空', code: '中国国际航空' },
	{ name: '东方航空', code: '东方航空' },
	{ name: '南方航空', code: '南方航空' },
	{ name: '海南航空', code: '海南航空' },
	{ name: '四川航空', code: '四川航空' },
]);
const tripType = ref('oneWay'); // 行程类型：oneWay-单程, roundTrip-往返
const departureCity = ref(''); // 出发城市
const arrivalCity = ref(''); // 到达城市
const departureDate = ref(''); // 出发日期
const returnDate = ref(''); // 返程日期
// const showCityPicker = ref(false); // 是否显示城市选择器
// const pickerType = ref('departure'); // 当前选择的城市类型
// const cityPopup = ref(); // 城市选择弹窗引用

const airlineIndex = ref(0);
const selectedAirline = computed(() => airlines.value[airlineIndex.value]);

const onAirlineChange = (e) => {
	airlineIndex.value = e.detail.value;
	console.log('选中航空公司:', selectedAirline.value);
};


const canSearch = computed(() => {
	return departureCity.value && arrivalCity.value && departureDate.value;
});

const minDate = computed(() => {
	const today = new Date();
	return today.toISOString().split('T')[0];
});

// 生命周期
onLoad(() => {
	// 设置默认日期为明天
	const tomorrow = new Date();
	tomorrow.setDate(tomorrow.getDate() + 1);
	departureDate.value = tomorrow.toISOString().split('T')[0];
	
	// 设置返程日期为出发日期后一天
	const returnDay = new Date(tomorrow);
	returnDay.setDate(returnDay.getDate() + 1);
	returnDate.value = returnDay.toISOString().split('T')[0];
});

// 方法
// 交换出发地和目的地
const swapCities = () => {
	[departureCity.value, arrivalCity.value] = [arrivalCity.value, departureCity.value];
};

// 日期选择处理
const onDepartureDateChange = (e) => {
	departureDate.value = e.detail.value;
	// 如果返程日期早于新的出发日期，自动调整返程日期
	if (tripType.value === 'roundTrip') {
		const depDate = new Date(departureDate.value);
		const retDate = new Date(returnDate.value);
		if (retDate < depDate) {
			const newReturnDate = new Date(depDate);
			newReturnDate.setDate(newReturnDate.getDate() + 1);
			returnDate.value = newReturnDate.toISOString().split('T')[0];
		}
	}
};

const onReturnDateChange = (e) => {
	returnDate.value = e.detail.value;
};


// 城市选择处理
const selectCity = (city) => {
	if (pickerType.value === 'departure') {
		departureCity.value = city.name;
	} else {
		arrivalCity.value = city.name;
	}
	closeCityPicker();
};

// const openCityPicker = () => {
// 	cityPopup.value.open();
// };

// const closeCityPicker = () => {
// 	cityPopup.value.close();
// };

// 搜索航班
const searchFlights = async () => {
	if (!canSearch.value) {
		uni.showToast({
			title: '请完善搜索条件',
			icon: 'none'
		});
		return;
	}

	uni.showLoading({
		title: '搜索中...'
	});

	try {
		
		const result = await uni.request({
		  url: base_url + 'api/flights/',
		  method: 'POST',
		  data: {
			"airline": selectedAirline.value.code,
			"departure": departureCity.value,
			"destination": arrivalCity.value,
			"departure_date": departureDate.value
		  }
		});
		
		console.log('搜索结果:', result.data);
		
		// 成功获取航班数据后
		if (result.data.code === 200 || result.data.success) {
		  setTimeout(() => {
		    uni.navigateTo({
		      url: `/pages/tabbar/tabbar-2/tabbar-2-1?flightData=${encodeURIComponent(JSON.stringify(result.data))}`
		    });
		  }, 1500);
		}

	} catch (error) {
		console.error('搜索失败:', error);
		uni.showToast({
			title: '搜索失败，请重试',
			icon: 'none'
		});
	} finally {
		uni.hideLoading();
	}
};
</script>

<style scoped>
.content {
	padding: 30rpx;
	background-color: #f5f5f5;
	min-height: 100vh;
}

.search-form {
	background: white;
	border-radius: 20rpx;
	padding: 30rpx;
	box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.1);
}

.trip-type {
	display: flex;
	margin-bottom: 40rpx;
	border-radius: 10rpx;
	overflow: hidden;
	border: 2rpx solid #007aff;
}

.type-item {
	flex: 1;
	text-align: center;
	padding: 20rpx;
	font-size: 32rpx;
	background: white;
	color: #007aff;
}

.type-item.active {
	background: #007aff;
	color: white;
}

.form-item {
	position: relative;
	margin-bottom: 30rpx;
	padding: 25rpx 0;
	border-bottom: 1rpx solid #eee;
}

.label {
	display: block;
	font-size: 28rpx;
	color: #666;
	margin-bottom: 15rpx;
}

.input, .picker {
	font-size: 36rpx;
	color: #333;
	padding: 15rpx 0;
	width: 100%;
}

.icon {
	position: absolute;
	right: 0;
	top: 50%;
	transform: translateY(-50%);
	font-size: 40rpx;
	color: #007aff;
}

.swap-btn {
	position: absolute;
	right: 30rpx;
	top: 50%;
	transform: translateY(-50%);
	width: 80rpx;
	height: 80rpx;
	background: #007aff;
	border-radius: 50%;
	display: flex;
	align-items: center;
	justify-content: center;
	color: white;
	font-size: 36rpx;
	z-index: 10;
}

.search-btn {
	background: linear-gradient(135deg, #007aff, #0056cc);
	color: white;
	border: none;
	border-radius: 50rpx;
	padding: 25rpx;
	font-size: 36rpx;
	margin-top: 40rpx;
}

.search-btn:disabled {
	background: #ccc;
}

.city-picker {
	background: white;
	border-radius: 30rpx 30rpx 0 0;
	padding: 40rpx;
	max-height: 70vh;
}

.picker-header {
	display: flex;
	justify-content: space-between;
	align-items: center;
	margin-bottom: 30rpx;
}

.picker-title {
	font-size: 36rpx;
	font-weight: bold;
}

.picker-close {
	color: #007aff;
	font-size: 32rpx;
}

.city-list {
	max-height: 50vh;
}

.city-item {
	display: block;
	padding: 25rpx 0;
	font-size: 32rpx;
	border-bottom: 1rpx solid #eee;
}
</style>