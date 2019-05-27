import Vue from 'vue'
import App from './App.vue'
import Meta from 'vue-meta';

Vue.config.productionTip = false;
Vue.config.devtools = true;

Vue.use(Meta);

new Vue({
  render: h => h(App),
}).$mount('#app')
