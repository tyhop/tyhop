import App from './App.vue'


// #ifndef VUE3
import Vue from 'vue'

// 添加全局请求拦截器
uni.addInterceptor('request', {
  invoke(args) {
    // 获取token
    const token = uni.getStorageSync('token');
    if (token) {
      args.header = {
        ...args.header,
        'Authorization': `Bearer ${token}`
      };
    }
  }
});

Vue.config.productionTip = false
App.mpType = 'app'
const app = new Vue({
	...App
})
app.$mount()
// #endif

// #ifdef VUE3
import {
	createSSRApp
} from 'vue'
export function createApp() {
	const app = createSSRApp(App)
	
	// 添加全局请求拦截器
	uni.addInterceptor('request', {
	  invoke(args) {
	    // 获取token
	    const token = uni.getStorageSync('token');
	    if (token) {
	      args.header = {
	        ...args.header,
	        'Authorization': `Bearer ${token}`
	      };
	    }
	  }
	});
	
	return {
		app
	}
}
// #endif
