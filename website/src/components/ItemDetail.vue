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
    <div class=" flex flex-row gap-2 flex-grow min-w-[20vw] border-3 border-red-600">
      <Rectangle
        :width="'10vw'">
        <slot name="imgs"></slot>
      </Rectangle>
      <div class="flex flex-col justify-between gap-3 flex-grow min-w-max">
        <slot name="title"></slot>
        <div>
          <slot name="details"></slot>
        </div>
      </div>
    </div>
    <div class="border-3 border-blue-600">
      <slot name="button"></slot>
    </div>
  </div>
</template>


