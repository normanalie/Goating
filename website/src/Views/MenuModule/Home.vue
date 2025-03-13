<script setup>
import { createRouter, createWebHistory, useRouter } from 'vue-router'
import { ref, onMounted } from 'vue'
import Card from '@/components/ItemCard.vue'
import Search from '@/components/SearchBTN.vue'
import Button from '@/components/Button.vue'
import { createClient } from '@supabase/supabase-js'
import SecBTN from '@/components/SecButton.vue'

// Initialisation de Supabase (remplace par tes credentials)

const supabaseKey = import.meta.env.VITE_SUPABASE_KEY
const supabaseUrl = import.meta.env.VITE_SUPABASE_URL
const supabase = createClient(supabaseUrl, supabaseKey)
const router = useRouter()

const user = ref(null)

const search = ref('Rechercher')
//const filter = ref('Filtrer')

function resetDOM() {

  // Sélection du premier élément avec la classe "wrapper"
  const wrapper = document.getElementsByClassName('wrapper')[0]
  if (wrapper) {
    while (wrapper.firstChild) {
      wrapper.removeChild(wrapper.firstChild)
    }
  }
  displayItems()
}

async function getItemData(materialId) {
  try {
    const { data, error } = await supabase.from('material_types').select('*').eq('id', materialId)

    if (error) throw error
    console.log('Fetch successful.')
    return data || []
  } catch (err) {
    console.error('[SUPABASE] Error fetching orders:', err)
    return []
  }
}

async function getAllItems() {
  try {
    const { data, error } = await supabase.from('material_types').select('*')

    if (error) throw error
    console.log('Data has been fetched successfully.')
    return data || []
  } catch (err) {
    console.error('[SUPABASE] Error fetching orders:', err)
    return []
  }
}

const items = ref([])

async function displayItems() {
  try {
    const data = await getAllItems()
    console.log(data)
    items.value = data
    items.value.reverse()
  } catch (error) {
    console.error('Erreur lors de la récupération des données:', error)
  }
}

function goToItem(itemId) {
  router.push({ name: 'ItemInfo', params: { id: itemId } })
}

async function isUserLoggedIn() {
  const { data } = await supabase.auth.getSession()
  user.value = data.session?.user || null
}

onMounted(() => {
  resetDOM()
  isUserLoggedIn()
})
</script>

<template>
  <main>
    <body>
      <nav class="flex flex-row justify-around items-center w-[60%] h-[5vh]">
        <Search :placeholder="search" :width="'62%'" :height="'5vh'"></Search>
        <SecBTN :height="'5vh'"> </SecBTN>
      </nav>
      <div v-if="items.length > 0" class="wrapper">
        <Card
          v-for="item in items"
          :key="item.id"
          :input="item.name"
          :img="item.image"
          @click="goToItem(item.id)"
        />
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
  grid-template-columns: repeat(auto-fit, minmax(20vw, 1fr));
  /*column-gap: 1vw;*/
  padding-top: 1.18vh;
  margin: 1vw;
  margin-left: 1vw;
}

@media (max-width: 900px) {
  .wrapper {
    grid-template-columns: repeat(3, minmax(20vw, 1fr)); /* Passe à 3 colonnes */
  }
}

@media (max-width: 600px) {
  .wrapper {
    grid-template-columns: repeat(2, minmax(30vw, 1fr)); /* Passe à 2 colonnes */
  }
}

@media (max-width: 400px) {
  .wrapper {
    grid-template-columns: 1fr; /* Passe à 1 colonne */
  }
}

.navBar {
  display: flex;
  flex-direction: row;
  justify-content: space-around;
  width: 90%;
  height: 3.54vh;
  margin-left: 4vw;
}

#filterBtn {
  width: 13vw;
  height: 3.54vh;
  border-radius: 0.25em;
  text-align: center;
}
</style>
