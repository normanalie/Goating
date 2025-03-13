<script setup>
import { ref } from 'vue'
import Rectangle from '@/components/ItemRectangle.vue'

const props = defineProps({
  elementId: {
    type: String,
    default: '0000000'
  },
  imgSrc: {
    type: String,
    default: ''
  }

})

</script>


<template>
  <div class="flex flex-row items-center">
    <div class="flex flex-row w-[100%] gap-2">
      <Rectangle
      :width="'10vw'">
      <slot name="imgs"></slot>
    </Rectangle>
      <div class="flex flex-col justify-between gap-3">
        <slot name="title"></slot>
        <div>
          <slot name="details"></slot>
        </div>
      </div>
    </div>
    <div>
      <slot name="button"></slot>
    </div>
  </div>
</template>


