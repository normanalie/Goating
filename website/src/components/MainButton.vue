<template>
  <button :type="type" :style="{ width: props.width, height: props.height }">
    {{ input || 'Empty button' }}
  </button>
</template>

<script setup>
const props = defineProps({
  input: String,
  type: String,
  width: String,
  height: String
})
</script>

<style scoped>
button {
  background-color: #2F27CE;
  color: white;
  border-radius: 0.5vw;
  border: none;
  cursor: pointer;
  padding: 10px;
  text-align: center;
  font-family: 'Franklin Gothic Medium', 'Arial Narrow', Arial, sans-serif;
  box-shadow: 2px 4px 10px rgba(0, 0, 0, 0.5);
}

button:active {
  transform: scale(0.95);
}
</style>
