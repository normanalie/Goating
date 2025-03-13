<script setup>
const props = defineProps({
    width: {
        type: String,
        default: '90%'
    },
    height: {
        type: String
    },
    imgSrc: {  // Nouvelle prop pour l'image
        type: String,
        default: ''  // Valeur par défaut vide
    }
});

const goToItem = () => {
    console.log("test validé");
};
</script>

<template>
  <div @click="goToItem" class="border border-gray-300 bg-[#DDDBFF] w-[90%] aspect-[13/9] rounded-[0.05em] flex justify-center items-center overflow-hidden transform scale-100 active:scale-97.5" :style="{ width: props.width, height: props.height }">
    <slot></slot>
</div>
</template>

<style scoped>
.itemCard {
  border: 1px solid #cccccc;
  background-color: #DDDBFF;
  width: 90%;
  aspect-ratio: 13 / 9;
  border-radius: 0.05em;
  display: flex;
  justify-content: center;
  align-items: center;
  overflow: hidden; /* Empêche l'image de dépasser */
}

.itemCard:active {
  transform: scale(0.975);
}

.itemImage {
  width: 100%;
  height: 100%;
  object-fit: cover; /* Ajuste l'image pour remplir le rectangle */
}
</style>
