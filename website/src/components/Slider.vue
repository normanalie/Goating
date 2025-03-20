<script setup>
import { ref, watch, onMounted } from 'vue';
import { useSliderStore } from '@/stores/sliderStore';

const props = defineProps({
  sliderId: String,
  maxValue: Number,
  modelValue: Number,  // Ajout de modelValue pour récupérer item.quantity
});

const emit = defineEmits(['update:value']);
const sliderStore = useSliderStore();

// 🔹 Initialisation avec item.quantity (via modelValue)
const sliderValue = ref(props.modelValue || 0);

watch(sliderValue, (newValue) => {
  sliderStore.setSliderValue(props.sliderId, newValue);
  emit('update:value', newValue);
});

const updateValue = (event) => {
  sliderValue.value = Number(event.target.value);
};

onMounted(() => {
  sliderStore.setSliderValue(props.sliderId, sliderValue.value);
});
</script>

<template>
  <div class="flex flex-row items-center gap-4">
    <input
      type="range"
      min="0"
      :max="maxValue || 15"
      id="slider"
      class="appearance-none w-[100%] h-[0.35em] bg-[#dddbff] rounded-lg"
      v-model="sliderValue"
      @input="updateValue"
    />
    <p class="bg-[#DDDBFF] p-[2%]">{{ sliderValue }}</p>
  </div>
</template>


<style scoped>
#slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 0.75em;
  height: 0.75em;
  border-radius: 50%;
  background: #2F27de;
}

#slider::-moz-range-thumb {
  width: 0.75em;
  height: 0.75em;
  border-radius: 50%;
  background: #DDDBFF;
  cursor: pointer;
}
</style>
