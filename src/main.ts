import { setupPwa } from './pwa'
import { createApp } from 'vue'
import App from './App.vue'
import './style.css'
createApp(App).mount('#app')

setupPwa()
