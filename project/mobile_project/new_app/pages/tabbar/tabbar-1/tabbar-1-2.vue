<template>
	<view class="content">
		行李咨询
		<br />
		<uni-forms>
			<uni-forms-item label="行李类型">
				<uni-data-picker v-model="formData.type" placeholder="选择类型" :localdata="dataTree">
				</uni-data-picker>
			</uni-forms-item>
			<uni-forms-item label="计划携带">
					<uni-easyinput type="textarea" v-model="formData.content" placeholder="请输入内容" ></uni-easyinput>
			</uni-forms-item>
			<uni-forms-item>
				<uni-section>
					<button text="咨询" type="primary" @click="submit" >
						<text class="word-btn-white">咨询</text>
					</button>
				</uni-section>
			</uni-forms-item>
		</uni-forms>
		<uni-load-more color="#007AFF" :status="loadStatus" />
		<view v-html="advice_content">
			
		</view>
	</view>
</template>

<script setup lang="ts">
	
import { reactive, ref } from 'vue';
import { onShow } from '@dcloudio/uni-app'
import { base_url } from '@/config.ts'

const result = ref('')
const input = ref('')
const loadStatus = ref('more')
const formData = reactive({
	type: '',
	content: ''
})
const dataTree = ref([{text: '随身携带', value:'随身携带'}, {text: '托运', value: '托运'}])

const advice_content = ref('')

const submit = ()=> {
	loadStatus.value = 'loading'
	uni.request({
		url:base_url + "api/dify/baggage",
		method: 'POST',
		data: {
			"content":  formData.content,
			"type": formData.type
		},
		success: (res) => {
			const advice = res.data.data.outputs.result.toString()
			advice_content.value = advice
			loadStatus.value = 'noMore'
		}
	})
	
	console.info("test: " + formData.type)
}

onShow(() => {
	console.log('onShow !!')
	// uni.request({
	// 	url: base_url + 'logic/sysuser/peewee/all',
	// 	method: 'GET',
	// 	success: (res) => {
	// 		console.log(res.data)
	// 		result.value = res.data
	// 	}
	// })
})

</script>

<style lang="scss">
.uni-mt-5 {
	margin-top: 5px;
}
.content {
	text-align: left;
	height: 400upx;
	margin-top: 200upx;
	// margin-left: 20upx;
	// margin-right: 20upx;
}
</style>
