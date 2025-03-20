<template>
  <div class="bg-[#2F27CE] text-white min-w-max max-h-full p-[0.5%] font-poppins sm:block hidden">
    <span
      class="collapse-icon"
      :class="{ 'rotate-180': collapsed }"
      @click="toggleSidebar"
    >
      <img src="@/components/icons/menu-bar.png" class="w-[4vw]" />
    </span>
    <div class="mt-8 ml-2 flex flex-col gap-4 text-lg">
      <SideBarLink
        v-for="item in menu"
        :key="item.name"
        class="flex flex-row gap-[1vw] items-center hover:cursor-pointer"
        :to="item.route"
        :icon="item.icon"
      >
        {{ item.name }}
      </SideBarLink>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { supabase } from '@/supabase.js';
import { collapsed, toggleSidebar } from './state'
import homeIcon from '@/components/icons/home.svg'
import boxIcon from '@/components/icons/box.svg'
import cartIcon from '@/components/icons/shoppingCart.svg'
import SideBarLink from './SideBarLink.vue'

const router = useRouter()

const logout = async () => {
  const { error } = await supabase.auth.signOut(); // Déconnexion Supabase
  if (error) {
    console.error("Erreur lors de la déconnexion :", error);
  } else {
    router.push('/login'); // Redirection vers la page de connexion
  }
}

async function signOut() {
  const { error } = await supabase.auth.signOut();
  if (error) {
    console.error('Erreur de déconnexion:', error.message);
  } else {
    console.log('Déconnexion réussie');
  }
}

const menu = ref([
  { name: 'Menu', icon: homeIcon, route: '/' },
  { name: 'Mes commandes', icon: boxIcon, route: '/myorders'},
  { name: 'Panier', icon: cartIcon, route: '/cart'},
  { name: 'Se déconnecter', icon: '', route:'/login' } // Utilisation de l'action
])
</script>

<style>
:root {
  --sidebar-bg-color: #2F27CE;
  --sidebar-item-hover: #DDDBFF;
  --sidebar-item-active: #8681e6;
}
</style>

<style scoped>
.sidebar {
  color: white;
  padding: 0.5em;

  transition: 0.3s ease;

  display: flex;
  flex-direction: column;
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
