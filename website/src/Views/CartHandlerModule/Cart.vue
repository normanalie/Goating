<script setup>
import { ref, onMounted, computed, watch } from 'vue';
import { supabase } from '@/supabase.js';
import { useRouter } from 'vue-router'
import ElemDetail from '@/components/ItemDetail.vue';
import Slider from '@/components/Slider.vue';
import { useOrderStore } from '@/stores/orderStore';
import cartIcon from '@/components/icons/cartIcon.svg'
import MainButton from '@/components/MainButton.vue';

const router = useRouter()
const userId = ref('');
const ordersWithId = ref([]);
const orderStore = useOrderStore();
const orders = computed(() => orderStore.getOrdersByUserId(userId.value));


async function getUserSession() {
  const { data, error } = await supabase.auth.getSession();

  if (error) {
    console.error("Erreur lors de la récupération de la session :", error.message);
    return null;
  }

  return data.session?.user?.id || null;
}

async function createOrder() {
  try {
    const { data, error } = await supabase
    .from('orders')
    .insert([
      { user_id: userId.value, order_status: 'processing' }
    ])
    .select('id')
    if(error) throw error
    console.log("[SUPABASE]: Commande créée.")
    console.log(data[0]?.id)
    ordersWithId.value = await addOrdersWithId(orders, data[0]?.id);
    await addItemsToOrder();
  } catch(e) {
    console.log("[SUPABASE]: Erreur lors de la création de la commande: ", e)
  }
}

const addOrdersWithId = async (orders, orderId) => {
  const updatedOrders = await Promise.all(
    orders.value.map(async (order) => {
      return {
        ...order,
        order_id: orderId
      }
    })
  );
  return updatedOrders;
}

function filterOrderItems(orders) {
  return orders.map(({ image, name, user_id, ...order }) => order);
}

async function addItemsToOrder() {
  try {
    const filteredOrders = filterOrderItems(ordersWithId.value);

    const { data, error } = await supabase
      .from('order_items')
      .upsert(filteredOrders)
      .select();

    if (error) throw error;
    console.log("[SUPABASE] Insertion réussie: ", data);
    orderStore.clearOrdersWithId(userId.value)
    console.log(orders.value)
  } catch (e) {
    console.log("[SUPABASE] Error while data insertion: ", e);
  }
}

function goTo(route) {
  router.push({ name: route })
}

watch(orders, (newOrders) => {
  console.log("Nouvelle valeur de orders :", newOrders);
});

const disappearingItems = ref(new Set()); // Stocker les éléments supprimés
const removeItem = (itemId) => {
  disappearingItems.value.add(itemId); // Ajouter l'élément à la liste des disparus

  setTimeout(() => {
    orderStore.removeItemById(itemId);
    disappearingItems.value.delete(itemId);
  }, 500);
};


onMounted(async () => {
  userId.value = await getUserSession();

});
</script>

<template>
  <main class=" h-full">
    <header>
      <h1 class="text-left text-[2em] font-bold ml-4">Mon panier</h1>
    </header>
    <body class="mt-4 h-full" v-if="orders.length > 0">
      <div>
        <div v-for="(item) in orders" :key="item.item_id" class="flex flex-col gap-4 flex-wrap flex-shrink">
          <Transition name="fade">
          <ElemDetail v-if="!disappearingItems.has(item.item_id)" class="p-6">
            <template #imgs>
              <img :src=item.image class="w-full h-full object-cover">
            </template>

            <template #title>
              <h2 class="text-lg font-semibold">{{ item.name }}</h2>
            </template>

            <template #details>
              <div>
                <div class="w-[100%]">
                  <Slider
                    :sliderId="item.id"
                    :maxValue="20"
                    :modelValue=Number(item.quantity)
                    @update:value="(val) => item.quantity = val"
                  ></Slider>
                </div>
                <h3 class="text-sm font-medium mt-[-1%]">Référence: {{ item.item_id.split('-').pop() }}</h3>
              </div>
            </template>

            <template #button>
              <div class="flex items-center mr-10">
                <button
                class="w-[2.5vw]"
                @click="removeItem(item.item_id)">
                  <img src="@/components/icons/bin.png" alt="bin" class="transform scale-100 active:scale-95 w-[100%]">
                </button>
              </div>
            </template>
          </ElemDetail>
        </Transition>
          <div class="flex justify-center">
              <hr class="mt-[-1.5%] border-t border-gray-500 w-[90%]">
          </div>
        </div>
        <div class="flex justify-end mr-14">
          <MainButton
            :width="'10vw'"
            :input="'Valider la commande'"
            @click="createOrder()">
          </MainButton>
        </div>
      </div>
    </body>
    <body v-else class="h-full w-full mt-8">
        <div class="flex flex-col items-center gap-3">
          <img :src="cartIcon" class="w-[30vw] h-[35vh]"/>
          <div class="text-center flex flex-col gap-2">
            <h1 class=" text-3xl font-bold">Votre panier est vide !</h1>
            <h2 class=" text-lg font-semibold">On dirait que vous n'avez aucune commande en cours...</h2>
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
    </body>
  </main>
</template>


<style scoped>

.fade-leave-active {
  transition:  all 0.7s cubic-bezier(0, 0.5, 0, 1.3);
}

.fade-leave-to {
  opacity: 0;
  transform: translateY(-20px);
}

.fade-leave-to {
  opacity: 0;
}


</style>
