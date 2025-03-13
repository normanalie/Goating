import { createApp } from 'vue'
import LayoutWrapper from './Views/Overlays/OverlayWrapper.vue'
import router from './router'
import './assets/tailwind.css'
import MainLayout from './Views/Overlays/MainOverlay.vue'

const app = createApp(LayoutWrapper)
app.use(router)
app.mount('#app')
