<template>
          <button
          class="border-none rounded-[2vw] pl-2 pr-3 bg-white bg-opacity-[0.4] active:scale-[0.98]"
          @click="goTo('Home')"
        >
          {{ content }}
        </button>
</template>

<script setup>

import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter();
const content = ref('Retour au site →')

function goTo(route) {
  router.push({ name: route })
}
</script>
