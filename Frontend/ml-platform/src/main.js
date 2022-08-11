// with polyfills
import 'core-js/stable'
import 'regenerator-runtime/runtime'

import Vue from 'vue'
import App from './App.vue'
import router from './router'
import store from './store/'
import i18n from './locales'
import { VueAxios } from './utils/request'
import ProLayout, { PageHeaderWrapper } from '@ant-design-vue/pro-layout'
import themePluginConfig from '../config/themePluginConfig'

// mock
// WARNING: `mockjs` NOT SUPPORT `IE` PLEASE DO NOT USE IN `production` ENV.
import './mock'
import axios from 'axios'
import bootstrap from './core/bootstrap'
import './core/lazy_use' // use lazy load components
import './utils/filter' // global filter
import './global.less' // global style

Vue.config.productionTip = false

// mount axios to `Vue.$http` and `this.$http`
Vue.use(VueAxios)
// use pro-layout components
Vue.component('pro-layout', ProLayout)
Vue.component('page-container', PageHeaderWrapper)
Vue.component('page-header-wrapper', PageHeaderWrapper)

axios.defaults.baseURL = 'http://127.0.0.1:8080'

// axios.interceptors.request.use((config) => {
//   config.headers['X-Requested-With'] = 'XMLHttpRequest'
//   const regex = /.*csrftoken=([^;.]*).*$/ // 用于从cookie中匹配 csrftoken值
//   config.headers['X-CSRFToken'] = document.cookie.match(regex) === null ? null : document.cookie.match(regex)[1]
//   return config
// })

window.umi_plugin_ant_themeVar = themePluginConfig.theme

new Vue({
  router,
  store,
  i18n,
  // init localstorage, vuex, Logo message
  created: bootstrap,
  render: h => h(App)
}).$mount('#app')
