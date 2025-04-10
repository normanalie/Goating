<template class="bg-[#2F27CE] h-full">
  <div class="sidebar-container">
    <div class="sidebar bg-[#2F27CE] text-white min-w-max max-h-full p-[0.5%] font-poppins sm:block hidden">
      <span
        class="collapse-icon"
        :class="{ 'rotate-180': collapsed }"
        @click="toggleSidebar"
      >
        <img src="@/components/icons/menu-bar.png" class="w-[4vw]" />
      </span>
      <div class="mt-8 ml-2 flex flex-col gap-4 text-lg flex-grow">
        <SideBarLink
          v-for="item in menu"
          :key="item.name"
          class="flex flex-row gap-[1vw] items-center hover:cursor-pointer"
          :to="item.route"
          :icon="item.icon"
          @click="item.action ? item.action() : null"
        >
          {{ item.name }}
        </SideBarLink>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { supabase } from '@/supabase.js';
import { collapsed, toggleSidebar } from './state'
import homeIcon from '@/components/icons/home.svg'
import boxIcon from '@/components/icons/box.svg'
import cartIcon from '@/components/icons/shoppingCart.svg'
import exitIcon from '@/components/icons/exit.png'
import SideBarLink from './SideBarLink.vue'

const router = useRouter()

const logout = async () => {
  const { error } = await supabase.auth.signOut(); // Déconnexion Supabase
  if (error) {
    console.error("Erreur lors de la déconnexion : ", error);
  } else {
    router.push('/login');
  }
}

async function isUserLoggedIn() {
  const { data } = await supabase.auth.getSession()
  return data.session?.user ? true : false;
}

const menu = ref([])

const loggedInMenu = ref([
  { name: 'Menu', icon: homeIcon, route: '/' },
  { name: 'Mes commandes', icon: boxIcon, route: '/myorders'},
  { name: 'Panier', icon: cartIcon, route: '/cart'},
  { name: 'Se déconnecter', icon: exitIcon, route: '', action: logout }
])

const baseMenu = ref([
  { name: 'Menu', icon: homeIcon, route: '/' },
  { name: 'Se connecter', icon: exitIcon, route: '/login'},
])

async function loadMenu() {
  menu.value = (await isUserLoggedIn() ? loggedInMenu.value : baseMenu.value);
}

onMounted(() => {
  loadMenu();
})


</script>

<style>
:root {
  --sidebar-bg-color: #2F27CE;
  --sidebar-item-hover: #DDDBFF;
  --sidebar-item-active: #8681e6;
}

.sidebar-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
}

.sidebar {
  display: flex;
  flex-direction: column;
  flex-grow: 1;
  overflow-y: auto;
}

.sidebar h1 {
  height: 2.5em;
}

.collapse-icon {
  padding: 0.75em;
  color: rgba(255, 255, 255, 0.7);
  transition: 0.2s linear;
}

.rotate-180 {
  transform: rotate(180deg);
  transition: 0.2s linear;
}
</style>

