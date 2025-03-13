<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  type: { type: String, default: 'text' },
  placeholder: { type: String, default: 'Enter text...' },
  width: { type: String, default: '8vw' },
  height: { type: String, default: '5.3vh' },
  prepend: { type: String, default: '' },
  append: { type: String, default: '' }
})

const emit = defineEmits(['update:modelValue'])
const inputField = ref('')

// Permet de mettre à jour la valeur lorsque l'utilisateur tape
watch(inputField, (newValue) => {
  emit('update:modelValue', newValue)
})
</script>

<template>
    <input
      class="flex-grow border shadow-[0px_2px_10px_-3px_rgba(0,0,0,0.5)] border-transparent p-[1%] px-[2%] rounded-[0.25vw] text-base outline-none hover:cursor-text focus:border-black/30 "
      :type="type"
      :placeholder="placeholder"
      v-model="inputField"
      required
    />
</template>
