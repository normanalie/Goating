<script setup>
import { useRouter } from 'vue-router'
import { ref, onMounted, computed, watch, onUpdated, onBeforeMount } from 'vue'
import { supabase } from '@/supabase.js'
import { storeToRefs } from 'pinia'
import Card from '@/components/ItemCard.vue'
import Search from '@/components/SearchBTN.vue'
import { useMenuStore } from '@/stores/menuStore'
import Button from '@/components/MainButton.vue'
import emptyIcon from '@/components/icons/cross.png'


const router = useRouter()

const menuStore = useMenuStore()
const { filteredItems, searchQuery } = storeToRefs(menuStore)

const search = ref('Rechercher')
//const filter = ref('Filtrer')

const items = ref([])

/* A REFAIRE */
async function displayItems() {
  try {
    items.value = menuStore.filteredItems;
  } catch (error) {
    console.error(`Erreur lors de l'affichage des données: `, error)
  }
}

function goToItem(itemId) {
  router.push({ name: 'ItemInfo', params: { id: itemId } })
}

onBeforeMount(() => {
  menuStore.fetchItems()
})

onMounted(() => {
  displayItems()
  console.log(items)
})

onUpdated(() =>{
  displayItems()
})
</script>

<template>
  <main>
    <body>
      <nav class="flex flex-row justify-around items-center w-[100%] h-[100%]">
        <Search
        :placeholder="search"
        :width="'80%'"
        :height="'7vh'"
        v-model="searchQuery"></Search>
        <Button
        :height="'7vh'"
        :input="'Filtrer'"
        id="SecButton"></Button>
      </nav>
      <div v-if="items.length > 0" class="w-[100%] grid grid-cols-[repeat(4,minmax(1vw,20vw))] gap-4 pt-[1.18vh] pl-[1.6vw]">
        <Card
          v-for="item in items"
          :key="item.id"
          :input="item.name"
          :img="item.image"
          class="mt-[2.5vh]"
          @click="goToItem(item.id)"
        />
      </div>
      <div v-else class="h-full w-full mt-8">
        <div class="flex flex-col items-center gap-3">
          <img :src="emptyIcon" class="w-[30vw] h-[35vh]"/>
          <div class="text-center flex flex-col gap-2">
            <h1 class=" text-3xl font-bold">Aucun article ne correspond à votre recherche...</h1>
          </div>
          <MainButton
          :width="'20vw'"
          :height="'9vh'"
          :input="'Accéder au menu'"
          class="mt-3
          "
          @click="goTo('Home')">
          </MainButton>
        </div>
      </div>
    </body>
  </main>
</template>

<style>
body {
  margin: 0;
  padding: 0;
  width: 100%;
  font-family: 'Poppins', sans-serif;
  box-sizing: border-box;
}

.titleBar {
  text-align: center;
  margin-bottom: 5vh;
}

.wrapper {
  width: 100%;
  display: grid;
  grid-template-columns: repeat(4, minmax(20vw, 1vw));
  padding-top: 1.18vh;
  padding-left: 1.6vw;
}

@media (max-width: 900px) {
  .wrapper {
    grid-template-columns: repeat(3, minmax(20vw, 1fr));
  }
}

@media (max-width: 600px) {
  .wrapper {
    grid-template-columns: repeat(2, minmax(30vw, 1fr));
  }
}

@media (max-width: 400px) {
  .wrapper {
    grid-template-columns: 1fr;
  }
}


#filterBtn {
  width: 13vw;
  height: 3.54vh;
  border-radius: 0.25em;
  text-align: center;
}
</style>
