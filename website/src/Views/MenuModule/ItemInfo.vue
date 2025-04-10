<script setup>
import { createRouter, createWebHistory, useRoute } from 'vue-router'
import { onMounted, ref } from 'vue'
import Rectangle from '@/components/ItemRectangle.vue';
import PrimButton from '@/components/MainButton.vue';
import { supabase } from '@/supabase.js';
import Slider from '@/components/Slider.vue';
import { useOrderStore } from '@/stores/orderStore';


/* a refaire ici */
const itemName = ref("Item Name");
const itemRef = ref("Référence: -");
const itemType = ref("Type: -");
const itemDescription = ref('');
const mainImgWidth = ref('45vw');
const imgOption = ref('10vw');
const otherItems = ref('10vw');
/* */
const mainImgSrc = ref('');

const itemData = ref([]);

//const test = ref(main);
const userId = ref('');
const router = useRoute();
const itemId = ref(router.params.id).value;
const sliderValue = ref(0);
const orderStore = useOrderStore();


async function getItemData(materialId){
  try{
      const { data, error } = await supabase
        .from('material_types')
        .select("*")
        .eq("id", materialId);

      if(error) throw error;
      console.log("Fetch successful.");
      return data || [];
  } catch (err) {
        console.error('[SUPABASE] Error fetching orders:', err);
        return [];
    }
}

async function getUserSession() {
  const { data, error } = await supabase.auth.getSession();

  if (error) {
    console.error("Erreur lors de la récupération de la session :", error.message);
    return null;
  }

  return data.session?.user?.id || null;
}

function addItemToCart() {
  //Ajouter la logique
  const newItem = { user_id: userId.value, item_id: itemRef.value, name: itemName.value, image: mainImgSrc.value, quantity: sliderValue.value, status: 'reserved' }
  orderStore.addItemToOrder(newItem)
  //orderStore.clearOrders()
  console.log("Bouton 'Ajouter au panier' appuyé.")
}

/* CONCEPTION TRES NULLE A REVOIR (je peux juste prendre un tableau avec les donnees json et l'utiliser comme j'ai fait pour Orders) */
function displayData(data){
  if (data.length > 0) {
    const item = data[0];

    itemName.value = item.name;
    itemRef.value = item.id;
    itemType.value = "Type: " + item.type;
    itemDescription.value = item.description || "Aucune description disponible.";
    mainImgSrc.value = item.image;
  }
}

const updateSliderValue = (newValue) => {
  sliderValue.value = newValue;
};

onMounted(async () => {
  userId.value = await getUserSession();
  getItemData(itemId)
  .then((data) => {
    itemData.value = data;
    console.log(itemData.value);
      displayData(itemData.value);
    })
    .catch((error) => {
      console.error("Erreur lors de la récupération des données:", error);
    });
  });

</script>

<template>
    <main class="h-full">
      <div class="item">
        <div class="imgDiv">
          <Rectangle id="mainImg"
          :width=mainImgWidth>
          <img v-if="mainImgSrc" alt="" :src="mainImgSrc" class="w-full h-full object-cover">
          </Rectangle>
          <div class="imgSelection">
            <Rectangle class="imgOption"
            :width=imgOption></Rectangle>
            <Rectangle class="imgOption"
            :width=imgOption></Rectangle>
            <Rectangle class="imgOption"
            :width=imgOption></Rectangle>
            <Rectangle class="imgOption"
            :width=imgOption></Rectangle>
          </div>
        </div>
        <div class="itemInfo">
          <div class="itemHeader">

            <h2 class="text-[2.5em]">{{ itemName }}</h2>
            <h3> Référence: {{ itemRef.split("-").pop() }}</h3>
          </div>
          <h3 class="text-[1.5em]">{{ itemType }}</h3>
          <p class=" text-sm">{{ itemDescription }}</p>
          <Slider
          :sliderId="itemRef"
          @update:value="updateSliderValue"></Slider>
          <PrimButton
          :input="'Ajouter au panier'"
          :width="'15vw'"
          @click="addItemToCart"></PrimButton>
        </div>
      </div>
      <div class="ml-[4.75vw] m-[3vh] text-[2em]">
        <h2>Similar Items</h2>
        <div class="itemRow">
          <Rectangle
            :width=otherItems></Rectangle>
            <Rectangle
            :width=otherItems></Rectangle>
            <Rectangle
            :width=otherItems></Rectangle>
            <Rectangle
            :width=otherItems></Rectangle>
            <Rectangle
            :width=otherItems></Rectangle>
        </div>
      </div>
    </main>
</template>


<style>
  body {
    margin: 0;
    padding: 0;
    font-family: 'Poppins', sans-serif;
    box-sizing: border-box;
  }

  .titleBar{
    text-align: center;
    margin-bottom: 5vh;
  }

  .item {
    font-weight: 400;
    width: 90%;
    display: flex;
    flex-wrap: wrap;
    gap: 1vw;
    margin-left: 4vw;
    margin-bottom: 2vh;
    justify-content: space-between;
    align-items: stretch;
}

.itemInfo {
    flex: 1 1 300px; /* Largeur minimale avant wrap */
    display: flex;
    flex-wrap: wrap;
    flex-direction: column;
    gap: 2vw;
}

@media (max-width: 830px) { /* Sur écrans petits où le wrap se produit */
  .imgDiv {
    min-width: 100%; /* Assure que ça prenne toute la largeur */
  }
  #mainImg{
    min-width: 100%;
  }
  .imgOption{
    min-width: 15vw;
  }
}

.item * {
    font-weight: inherit;
}

.itemHeader {
  display: flex;
  flex: 0 1 auto;
  flex-wrap: wrap;
  flex-direction: row;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  height: fit-content;
  margin-top: 1vw;
}

.imgDiv {
  flex: 0 0 300px; /* Largeur minimale avant wrap */
  display: flex;
  flex-direction: column;
  flex-shrink: 1;
  gap: 1vw;
  margin-left: 0.75vw;
}



.imgSelection {
  display: flex;
  flex-direction: row;
  gap: 1vw;
}

#itemName {
  font-size: 3.5em;
}

#ref{
  font-size: 1em;
  text-align:start;
}

#type {
  font-size: 1.5em;
}

.itemRow{
  display: flex;
  flex-direction: row;
  gap: 0.75vw;
}

</style>
