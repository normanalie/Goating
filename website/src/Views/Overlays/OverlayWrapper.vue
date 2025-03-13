<template>
  <!-- Le layout est dynamique et dépend de la route -->
  <component :is="layout">
    <router-view />
  </component>
</template>

<script setup>
import { onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import MainLayout from './MainOverlay.vue'

const route = useRoute()

// Récupérer le layout associé à la route, sinon utiliser MainLayout par défaut
const layout = computed(() => route.meta.layout || MainLayout)

onMounted(() => {})
</script>

<style scoped>
/* Ajoute des styles si nécessaire */
</style>
