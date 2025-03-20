<script setup>
import { ref, onMounted, computed, watch, onUnmounted } from 'vue';

import ElemDetail from '@/components/OrderDetail.vue';
import { supabase } from '@/supabase.js';
import Slider from '@/components/Slider.vue';
import { storeToRefs } from 'pinia'
import { useOrderStore } from '@/stores/orderStore';
import PrimButton from '@/components/PrimButton.vue';
import { toRaw } from "vue";



const userId = ref('');
const ordersWithId = ref([]);
const orderStore = useOrderStore();
const { getOrdersByUserId } = storeToRefs(orderStore);

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


onMounted(async () => {
  userId.value = await getUserSession();
  //getOrders(userId);
  //orderStore.clearOrders();
});
</script>

<template>
  <main>
    <header>
      <h1 class="text-left text-[2em] font-bold ml-4">Mon panier</h1>
    </header>
    <body class="mt-4">
      <div v-for="(item) in orders" :key="item.item_id" class="flex flex-col gap-4 flex-wrap flex-shrink">
        <ElemDetail class="p-6">
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
              @click="orderStore.removeItemById(item.item_id)">
                <img src="@/components/icons/bin.png" alt="bin" class="transform scale-100 active:scale-95 w-[100%]">
              </button>
            </div>
          </template>
        </ElemDetail>
        <div class="flex justify-center">
            <hr class="mt-[-1.5%] border-t border-gray-500 w-[90%]">
        </div>
      </div>
      <PrimButton
      :width="'10vw'"
      @click="createOrder()">
      </PrimButton>
    </body>
  </main>
</template>
