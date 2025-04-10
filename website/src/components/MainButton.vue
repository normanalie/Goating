<template>
  <button
  :type="type"
  :style="{ width: props.width, height: props.height }"
  :id="buttonId"
  class=" text-white rounded-[0.5vw] border-none cursor-pointer p-[10px] px-5 text-center font-inter font-bold transform scale-100 active:scale-95 " >
    {{ input || 'Empty button' }}
  </button>
</template>

<script setup>
const props = defineProps({
  id: String,
  input: String,
  type: String,
  width: String,
  height: String
})

const buttonId = props.id || 'PrimButton';
</script>

<style scoped>

#PrimButton{
  background: #2f27ce;
  box-shadow: 0 0 15px #2821ab;
}

#SecButton {
  background: #dddbff;
  color: #463eda;
  box-shadow: 0 0 15px #737373;
}

#UnusedButton {
  background: #a6a6a6;
  color: #404040;
  box-shadow: 0 0 15px #b3b3b3;
}

#PrimButton:active{
  background: #463eda;
}

#SecButton:active {

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
