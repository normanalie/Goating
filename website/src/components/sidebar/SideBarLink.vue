<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { collapsed } from './state'

const props = defineProps({
  to: { type: String, required: true },
  icon: { type: String, required: true }
})

const route = useRoute()
const isActive = computed(() => route.path === props.to)
</script>

<template>
  <router-link :to="to" class="link" :class="{ active: isActive }">
    <img v-if="!collapsed" class="w-[13%] mr-1" :src="icon" />
    <img v-else class="w-[40%] mr-1" :src="icon" />
    <transition name="fade">
      <span v-if="!collapsed">
        <slot />
      </span>
    </transition>
  </router-link>
</template>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.1s;
}

.fade-enter,
.fade-leave-to {
  opacity: 0;
}

.link {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0.6rem;
  border-radius: 8px;
  transition: background 0.3s;
  color: white;
  text-decoration: none;
}

.link:hover {
  background-color: rgba(255, 255, 255, 0.2);
}

.link.active {
  background-color: rgba(255, 255, 255, 0.3);
}

.link .icon {
  flex-shrink: 0;
  width: 50%;
  margin-right: 10px;
}
</style>
