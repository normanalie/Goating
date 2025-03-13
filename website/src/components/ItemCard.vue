<script setup>
import { ref } from 'vue';
import Rectangle from './ItemRectangle.vue';
import Disp from './AvailableItem.vue';

const props = defineProps({
  input: String, // On récupère le nom de l'item
  type: String,
  img: String,
  to: Object // Permet de passer l'objet route

});
</script>

<template>
  <div class="m-0 mb-2">
  <router-link :to="to">
    <Rectangle>
    <img v-if="img != null" :src="img" alt="Image" class="w-[100%] h-[100%] object-cover">
  </Rectangle>
    <div>
      <h3 class="mt-[0.75]">{{ input }}</h3> <!-- On affiche input -->
      <Disp></Disp>
    </div>
  </router-link>
  </div>
</template>

<style scoped>
.ItemName {
  margin-top: 0.75em;
  margin-bottom: -0.75em;
}
</style>
