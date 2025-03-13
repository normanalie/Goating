<script setup>
import { createRouter, createWebHistory, useRoute } from 'vue-router'
import { onMounted, ref } from 'vue'
import Rectangle from '@/components/ItemRectangle.vue';
import PrimButton from '@/components/PrimButton.vue';
import { createClient } from '@supabase/supabase-js';

// Initialisation de Supabase (remplace par tes credentials)

const supabaseKey = import.meta.env.VITE_SUPABASE_KEY;
const supabaseUrl = import.meta.env.VITE_SUPABASE_URL;

const supabase = createClient(supabaseUrl, supabaseKey);


const itemName = ref("Item Name");
const itemRef = ref("Référence: -");
const itemType = ref("Type: -");
const itemDescription = ref('');
const mainImgWidth = ref('45vw');
const imgOption = ref('10vw');
const otherItems = ref('10vw');
const mainImgSrc = ref('');

//const test = ref(main);
const router = useRoute();
const itemId = ref(router.params.id).value;

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

function displayData(data){
  if (data.length > 0) {
    const item = data[0];

    itemName.value = item.name;
    itemRef.value = "Référence: " + item.id.split("-").pop();
    itemType.value = "Type: " + item.type;
    itemDescription.value = item.description || "Aucune description disponible.";
    mainImgSrc.value = item.image;
  }
}

onMounted(() => {
  getItemData(itemId)
  .then((data) => {
      displayData(data);
    })
    .catch((error) => {
      console.error("Erreur lors de la récupération des données:", error);
    });
  });

</script>

<template>
  <body>
    <main class="h-full">
      <div class="item">
        <div class="imgDiv">
          <Rectangle id="mainImg" :imgSrc="mainImgSrc"
          :width=mainImgWidth></Rectangle>
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
            <h2 class="text-[3.5em]">{{ itemName }}</h2>
            <h3>{{ itemRef }}</h3>
          </div>
          <h3 class="text-[1.5em]">{{ itemType }}</h3>
          <p>{{ itemDescription }}</p>
          <PrimButton id="addBtn"
          :input="'Ajouter au panier'"
          :width="'15vw'"></PrimButton>
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
  </body>
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

#description{

}

</style>
