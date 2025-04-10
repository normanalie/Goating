<script setup>
import { createRouter, createWebHistory, useRouter } from 'vue-router'
import { ref, onMounted } from 'vue'
import { createClient } from '@supabase/supabase-js'
import SideBar from '@/components/sidebar/Sidebar.vue';

const router = useRouter();

</script>

<template>
  <div class="h-screen flex flex-row">
    <SideBar class="h-full" />
    <div class="flex-1 w-full overflow-y-auto">
      <h1 class="text-[3em] text-center">STOREBOT</h1>
      <router-view />
    </div>
  </div>
</template>

