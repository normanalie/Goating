import { createRouter, createWebHistory } from 'vue-router'
import MainLayout from '@/Views/Overlays/MainOverlay.vue'
import AuthLayout from '@/Views/Overlays/AuthOverlay.vue'
import Home from '@/Views/MenuModule/Home.vue'
import ItemInfo from '@/Views/MenuModule/ItemInfo.vue'
import AuthLogin from '@/Views/AuthModule/AuthLogin.vue'
import Orders from '@/Views/OrdersModule/Orders.vue'
import Cart from '@/Views/CartHandlerModule/Cart.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home,
    meta: { layout: MainLayout }, // Ajout du layout ici
  },
  {
    path: '/login',
    name: 'AuthLogin',
    component: AuthLogin,
    meta: { layout: AuthLayout },
  },
  {
    path: '/item/:id',
    name: 'ItemInfo',
    component: ItemInfo,
    meta: { layout: MainLayout },
  },
  {
    path: '/myorders',
    name: 'Orders',
    component: Orders,
    meta: { layout: MainLayout },
  },
  {
    path: '/cart',
    name: 'Cart',
    component: Cart,
    meta: { layout: MainLayout },
  },
  /*{ path: '/session?/orders', name: 'Orders', component: Orders}*/
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
