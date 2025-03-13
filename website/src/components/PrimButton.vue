<template>
  <button :type="type" :style="{ width: props.width, height: props.height }" id="PrimButton" class=" text-white rounded-[0.5vw] border-none cursor-pointer p-[10px] text-center font-inter font-semibold transform scale-100 active:scale-95 " >
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

#PrimButton{
  background: #2f27ce;
  box-shadow: 0 0 15px #2821ab;
}

#PrimButton:active{
  background: #463eda;
}

/*
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
*/
</style>
