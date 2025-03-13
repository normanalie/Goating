<script setup>
import { ref } from 'vue'

const props = defineProps({
  type: {
    type: String,
    default: 'text',
  },
  placeholder: {
    type: String,
    default: 'Enter text...',
  },
  width: {
    type: String,
    default: '83vw',
  },
  height: {
    type: String,
    default: '5.3vh',
  },
  prepend: {
    type: String,
    default: '',
  },
  append: {
    type: String,
    default: '',
  },
})

const inputField = ref('')
</script>

<template>
    <input
      :type="type"
      :placeholder="placeholder"
      v-model="inputField"
      :style="{ width: width, height: height }"
      required
    />
</template>

<style scoped>
.input-wrapper {
  display: flex;
  align-items: center;
  border-radius: 5px;
  width: 80vw;
  height: 30vh;
  box-shadow: 1px 1px 7px rgba(0, 0, 0, 0.7);
}

.input-icon {
  display: flex;
  justify-content: center;
  align-items: center;
}

.input-icon img {
  width: 20px; /* Taille de l'icône */
  height: 20px;
}

input {
  border: 1px solid #cccccc;
  padding-left: 10px;
  padding-right: 10px;
  border-radius: 5px;
}

input:hover {
  cursor: text;
}

input:active {
  border-color: rgba(0, 0, 0, 0.1);
}
</style>
