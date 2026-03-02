<template>
  <view>
    <cmd-nav-bar back title="用户注册"></cmd-nav-bar>
    <cmd-page-body type="top">
      <view class="register">
        <!-- 上部分 start -->
        <view class="register-title">{{ '账号密码注册' }}</view>
        <!-- 上部分 end -->
        <!-- 账号表单注册 start -->
        <!-- #ifdef H5 -->
        <cmd-transition name="fade-up">
          <view v-if="!status">
            <view class="register-username">
              <input v-model="account.username" type="text" focus maxlength="26" placeholder="请输入账号"></input>
            </view>
            <view class="register-password">
              <input v-model="account.password" type="password" displayable maxlength="26" placeholder="请输入密码"></input>
            </view>
            <button class="btn-register" hover-class="btn-register-hover" @tap="fnRegister(account)">注册</button>
          </view>
        </cmd-transition>
        <!-- #endif -->
        <!-- #ifndef H5 -->
        <cmd-transition name="fade-up" v-if="!status">
          <view class="register-username">
            <cmd-input v-model="account.username" type="text" focus maxlength="26" placeholder="请输入账号"></cmd-input>
          </view>
          <view class="register-password">
            <cmd-input v-model="account.password" type="password" displayable maxlength="26" placeholder="请输入密码"></cmd-input>
          </view>
          <button class="btn-register" hover-class="btn-register-hover" @tap="fnRegister">注册</button>
        </cmd-transition>
        <!-- #endif -->
        <!-- 账号表单注册 end -->
      </view>
    </cmd-page-body>
  </view>

</template>

<script>
  import cmdNavBar from "@/components/cmd-nav-bar/cmd-nav-bar.vue"
  import cmdPageBody from "@/components/cmd-page-body/cmd-page-body.vue"
  import cmdTransition from "@/components/cmd-transition/cmd-transition.vue"
  import cmdInput from "@/components/cmd-input/cmd-input.vue"
import { base_url } from "../../config"

  export default {
    components: {
      cmdNavBar,
      cmdPageBody,
      cmdTransition,
      cmdInput
    },

    data() {
      return {
        account: {
          username: '',
          password: ''
        },
        usernameReg: /^[A-Za-z0-9]+$/,
        passwordReg: /^\w+$/,
        registerAccount: false,
        mobile: {
          phone: '',
          code: ''
        }
        // phoneReg: /^[1](([3][0-9])|([4][5-9])|([5][0-3,5-9])|([6][5,6])|([7][0-8])|([8][0-9])|([9][1,8,9]))[0-9]{8}$/,
        // registerMobile: false,
        // safety: {
        //   time: 60,
        //   state: false,
        //   interval: ''
        // },
        // status: false // true手机注册,false账号注册
      };
    },

    watch: {
      /**
       * 监听账号注册数值
       */
      account: {
        handler(newValue) {
          if ((this.usernameReg.test(newValue.username) && newValue.username.length >= 8) && (this.passwordReg.test(
              newValue
              .password) && newValue.password.length >= 8)) {
				  this.password = newValue.password;
				  this.username = newValue.username
            this.registerAccount = true;
          } else {
			  
            this.registerAccount = false
          }
        },
        deep: true
      }
    },

    methods: {
      /**
       * 注册按钮点击执行
       */
      fnRegister(account1) {
		const account = account1
		uni.request({
			url: base_url + 'api/users/register',
			method: 'POST',
			data: {
				"uid": account.username,
				"pwd": account.password,
				"nick_name": "默认"
			},
			success: (res) => {
				console.log("注册成功")
				
				uni.showToast({
				  title: '注册成功',
				  icon: 'success',
				});
			}
		})
		
      },
      
      /**
       * 改变注册方式状态
       */
      fnChangeStatus() {
        this.mobile = {
          phone: '',
          code: ''
        }
        this.registerAccount = false
        this.account = {
          username: '',
          password: ''
        }
        this.registerMobile = false
        // 验证码时间状态还原
        clearInterval(this.safety.interval);
        this.safety.time = 60;
        this.safety.state = false;
        // 可以延迟3后切换
        this.status = !this.status;
      }
    },

    beforeDestroy() {
      /**
       * 关闭页面清除轮询器
       */
      clearInterval(this.safety.interval);
    }
  }
</script>

<style>
  .register {
    margin-top: 56upx;
    margin-right: 72upx;
    margin-left: 72upx;
  }

  .register-title {
    font-size: 56upx;
    font-weight: 500;
  }

  .register-explain {
    font-size: 28upx;
    color: #9E9E9E;
  }

  .register-phone {
    display: flex;
    flex-direction: row;
    justify-content: space-between;
    align-items: center;
    border-bottom: 2upx #dedede solid;
    margin-top: 56upx;
    margin-bottom: 40upx;
  }

  .register-phone-getcode {
    color: #3F51B5;
    text-align: center;
    min-width: 140upx;
  }

  .register-code {
    border-bottom: 2upx #dedede solid;
  }

  .register-username {
    margin-top: 56upx;
    margin-bottom: 40upx;
    border-bottom: 2upx #dedede solid;
  }

  .register-password {
    border-bottom: 2upx #dedede solid;
  }

  .btn-register {
    margin-top: 100upx;
    border-radius: 50upx;
    font-size: 16px;
    color: #fff;
    background: linear-gradient(to right, #88a1f9, #9ac6ff);
  }

  .btn-register-active {
    background: linear-gradient(to right, #365fff, #36bbff);
  }

  .btn-register-hover {
    background: linear-gradient(to right, #365fdd, #36bbfa);
  }

  button[disabled] {
    color: #fff;
  }

  .register-mode {
    text-align: center;
    margin-top: 32upx;
  }
</style>
