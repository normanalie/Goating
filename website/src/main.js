import { createApp } from 'vue'
import LayoutWrapper from './Views/Overlays/OverlayWrapper.vue'
import router from './router'
import './assets/tailwind.css'
import { createPinia } from 'pinia'; // Importer Pinia
import piniaPluginPersistedstate from 'pinia-plugin-persistedstate'


// Créer une instance de Pinia et l'utiliser avec l'application Vue
const app = createApp(LayoutWrapper)
const pinia = createPinia();
pinia.use(piniaPluginPersistedstate)
app.use(pinia)
app.use(router)
app.mount('#app')
