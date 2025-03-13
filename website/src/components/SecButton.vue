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
  background-color: #DDDBFF;
  color: #2F27CE;
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


"inline-flex items-center gap-2 rounded-md bg-gray-700 py-1.5 px-3 text-sm/6 font-semibold
text-white shadow-inner shadow-white/10 focus:outline-none data-[hover]:bg-gray-600
data-[open]:bg-gray-700 data-[focus]:outline-1 data-[focus]:outline-white">
