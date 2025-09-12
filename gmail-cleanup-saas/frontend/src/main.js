import { createApp } from 'vue'
import { createPinia } from 'pinia'
import router from './router'
import App from './App.vue'
import './style.css'

// Popular Vue 3 libraries
import Toast from 'vue-toastification'
import 'vue-toastification/dist/index.css'
import FloatingVue from 'floating-vue'
import 'floating-vue/dist/style.css'

const app = createApp(App)

// Toast notifications with custom options
const toastOptions = {
  position: 'top-right',
  timeout: 5000,
  closeOnClick: true,
  pauseOnFocusLoss: true,
  pauseOnHover: true,
  draggable: true,
  draggablePercent: 0.6,
  showCloseButtonOnHover: false,
  hideProgressBar: false,
  closeButton: 'button',
  icon: true,
  rtl: false
}

app.use(createPinia())
app.use(router)
app.use(Toast, toastOptions)
app.use(FloatingVue)

app.mount('#app')