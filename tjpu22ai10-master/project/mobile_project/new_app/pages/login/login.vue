<template>
  <view>
    <cmd-nav-bar back title="用户登录" rightText="注册" @rightText="fnRegisterWin"></cmd-nav-bar>
    <cmd-page-body type="top">
      <view class="login">
        <!-- 上部分 start -->
        <view class="login-title">{{ '使用账号密码登录'}}</view>
        <view class="login-explain">{{ '未注册用户可通过点击右上角进行注册'}}</view>
        <!-- 上部分 end -->

        <!-- 账号表单登录 start -->
        <cmd-transition name="fade-up">
          <view>
            <view class="login-username">
              <input v-model="account.username" type="text" :focus="true" maxlength="26" placeholder="请输入账号"></input>
            </view>
            <view class="login-password">
              <input v-model="account.password" type="password" displayable maxlength="26" placeholder="请输入密码"></input>
            </view>
            <button class="btn-login" :class="{'btn-login-active': loginAccount}" hover-class="btn-login-hover" @click="fnLogin" :disabled="!loginAccount">登录</button>
          </view>
        </cmd-transition>
        <!-- 账号表单登录 end -->
      </view>
    </cmd-page-body>
  </view>
</template>

<script setup>
import { ref, reactive, watch, onUnmounted } from 'vue';
import { base_url } from "../../config"

// 响应式数据
const account = reactive({
  username: '',
  password: ''
});

const usernameReg = /^[A-Za-z0-9]+$/;
const passwordReg = /^\w+$/;
const loginAccount = ref(false);

// 验证码相关数据
const safety = reactive({
  time: 60,
  state: false,
  interval: null
});

// 监听账号输入变化
watch(account, (newValue) => {
  if ((usernameReg.test(newValue.username) && newValue.username.length >= 1) && 
      (passwordReg.test(newValue.password) && newValue.password.length >= 6)) {
    loginAccount.value = true;
  } else {
    loginAccount.value = false;
  }
}, { deep: true });

/**
 * 登录按钮点击执行
 */
const fnLogin = async () => {
  if (!loginAccount.value) return;
  
  try {
    const result = await uni.request({
      url: base_url + 'api/users/login',
      method: 'POST',
      data: {
        "uid": account.username,
        "pwd": account.password
      }
    });
    
    console.log('登录结果:', result.data);
    
    // 登录成功处理
    if (result.data.code == 200 || result.data.success) {
      // 存储用户信息到本地
	  uni.setStorageSync('userInfo', result.data.data);
      uni.setStorageSync('token', result.data.data.token);
	  
      
      uni.showToast({
        title: '登录成功',
        icon: 'success',
      });
      
      // 跳转到首页
      setTimeout(() => {
        uni.switchTab({
          url: "/pages/tabbar/tabbar-1/tabbar-1"
        });
      }, 1500);
      
    } else {
      uni.showToast({
        title: result.data.message || '登录失败',
        icon: 'none'
      });
    }
    
  } catch (error) {
    console.error('登录错误:', error);
    uni.showToast({
      title: '网络错误，请重试',
      icon: 'none'
    });
  }
};

/**
 * 重置表单状态
 */
const fnChangeStatus = (reset) => {
  account.username = '';
  account.password = '';
  loginAccount.value = false;
  
  // 验证码时间状态还原
  clearInterval(safety.interval);
  safety.time = 60;
  safety.state = false;
};

/**
 * 跳转注册页面
 */
const fnRegisterWin = () => {
  uni.navigateTo({
    url: "/pages/register/register"
  });
  // 改变状态重置，跳转不会摧毁实例
  fnChangeStatus(true);
};

// 组件卸载时清除定时器
onUnmounted(() => {
  clearInterval(safety.interval);
});
</script>

<style>
.login {
  margin-top: 56upx;
  margin-right: 72upx;
  margin-left: 72upx;
}

.login-title {
  font-size: 56upx;
  font-weight: 500;
}

.login-explain {
  font-size: 28upx;
  color: #9E9E9E;
  margin-bottom: 40upx;
}

.login-username {
  margin-bottom: 40upx;
  border-bottom: 2upx #dedede solid;
}

.login-password {
  border-bottom: 2upx #dedede solid;
}

.btn-login {
  margin-top: 100upx;
  border-radius: 50upx;
  font-size: 16px;
  color: #fff;
  background: linear-gradient(to right, #88a1f9, #9ac6ff);
}

.btn-login-active {
  background: linear-gradient(to right, #365fff, #36bbff);
}

.btn-login-hover {
  background: linear-gradient(to right, #365fdd, #36bbfa);
}

button[disabled] {
  background: linear-gradient(to right, #cccccc, #dddddd) !important;
  color: #999 !important;
}
</style>