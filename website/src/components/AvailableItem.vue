<script setup>
import { ref } from 'vue'
const available = ref(true);
</script>

<template>
<p v-if="available">🟢 Disponible</p>
<p v-else>🔴 Indisponible</p>
</template>


<style></style>