<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import ItemDetail from '@/components/ItemDetail.vue';
import { supabase } from '@/supabase.js';
import MainButton from '@/components/MainButton.vue';
import packageIcon from '@/components/icons/packageIcon.svg'

const router = useRouter()

const userId = ref(null);
const showDetails = ref([]);

const orders = ref([]);
const orderImgs = ref([]); //A changer

const itemStatus = ref([
  { status: 'reserved', type: 'consommable' , button: 'Récupérer'},
  { status: 'retrieved', type: 'consommable', button: 'None'},
  { status: 'reserved', type: 'durable' , button: 'Récupérer'},
  { status: 'retrieved', type: 'durable', button: 'Retourner'}
])



async function getUserSession() {
  const { data, error } = await supabase.auth.getSession();

  if (error) {
    console.error("Erreur lors de la récupération de la session :", error.message);
    return null;
  }

  return data.session?.user?.id || null;
}

function goTo(route) {
  router.push({ name: route })
}

async function fetchOrdersWithItems(userId) {
  try {
    const { data, error } = await supabase
      .from('orders')
      .select(`
        *,
        order_items (
          item_id,
          quantity,
          status,
          material_items:material_types(id, name, image, type, description)
        )
      `)
      .eq('user_id', userId);


    if (error) throw error;

    console.log('[SUPABASE] Order fetched successfully');
    return data || [];
  } catch (err) {
    console.error('[SUPABASE] Error fetching orders:', err);
    return [];
  }
}

async function getOrderImgs(orderId) {
  // 1. Récupérer les material_item_id associés à l'orderId
  const { data: orderItems, error: orderItemsError } = await supabase
    .from('order_items')
    .select('item_id')
    .eq('order_id', orderId);

  if (orderItemsError || !orderItems.length) {
    console.error("Erreur lors de la récupération des items de la commande:", orderItemsError);
    return [];
  }

  const materialItemIds = orderItems.map(item => item.item_id);
  // 2. Récupérer les images des material_items correspondants
  const { data: materials, error: materialsError } = await supabase
    .from('material_types')
    .select('image')
    .in('id', materialItemIds);

  if (materialsError) {
    console.error("Erreur lors de la récupération des images:", materialsError);
    return [];
  }

  return materials.map(item => item.image);
}

/* Modifie ce snippet */
const sortedOrders = computed(() => {
  const ordersCopy = [...orders.value];

  return ordersCopy.sort((a, b) => {
    const dateA = new Date(a.created_at);
    const dateB = new Date(b.created_at);

    return dateA - dateB;
  });
});
/* Modifie ce snippet */

onMounted(async () =>{
  userId.value = await getUserSession();
  orders.value = await fetchOrdersWithItems(userId.value);
  console.log('sortedOrders: ', sortedOrders);
  console.log(orders.value);
  orderImgs.value = await getOrderImgs(orders.value[0].id);
  showDetails.value = orders.value.map(() => false);

})

</script>


<template class="h-screen">
  <main>
    <header>
      <h1 class="text-left text-[2em] font-bold ml-4">Mes Commandes</h1>
    </header>
        <body v-if="sortedOrders.length > 0" class="mt-4">
          <div v-for="(order, index) in sortedOrders" :key="order.id" class=" mt-[-2.1%] flex flex-col gap-4 flex-wrap flex-shrink">
            <ItemDetail class="p-6 flex-grow min-w-min">
              <template #imgs>
                <img
                v-if="order.order_items?.length > 0 && order.order_items[0]?.material_items?.image"
                :src="order.order_items[0].material_items.image"
                alt="Image" class="w-full h-full object-cover"
                >
              </template>

              <template #title>
                <h2 class="text-md font-semibold">Order n°{{ order.id.split("-").pop() }}</h2>
              </template>

              <template #details>
                <h3 class="text-sm font-medium mb-[-1%]">Nombre d'articles: {{ order.order_items.length }}</h3>
                <h3 class="text-sm font-medium mt-[-1%]">Commande passée le {{ order.created_at.split("T")[0].split("-").reverse().join("/") }} à {{ order.created_at.split("T")[1].split(/[.+]/)[0] }}</h3> <!-- OU  order.created_at.substring(0, order.created_at.lastIndexOf("T")) -->
              </template>

              <template #button>
                <MainButton
                :input="'Show details'"
                :width="'10vw'"
                :height="'12vh'"
                :id="PrimButton"
                @click="showDetails[index] = !showDetails[index]">
                </MainButton>
              </template>
            </ItemDetail>
            <Transition name="slide">
              <div v-if="showDetails[index]" class="max-h-fit flex justify-center">
                <div class="border border-y-0 border-x-gray-500 w-[90%] flex flex-col justify-center mt-[-3%]">
                  <div v-for="item in order.order_items"
                    :key="item.item_id"
                    class=" w-[100%]">
                    <ItemDetail class="p-6 flex-shrink">
                      <template #imgs>
                        <img v-if="item.material_items.image" :src="item.material_items.image" :alt="item.material_items.name" class="w-full h-full object-cover">
                      </template>
                      <template #title>
                        <h2 class="text-sm font-semibold ">Nom: {{ item.material_items.name }}</h2>
                        <h3 class="text-[0.75em] font-medium mt-[-4%]"> Statut: {{ item.status }}</h3>
                      </template>
                      <template #details>
                        <h3 class=" text-[0.75em] font-medium mb-[-1%]">Référence: {{ item.item_id.split("-").pop() }}</h3>
                        <h3 class="text-[0.75em] font-medium">Quantité: {{ item.quantity }}</h3> <!-- OU  order.created_at.substring(0, order.created_at.lastIndexOf("T")) -->
                      </template>
                      <template #button>
                        <MainButton
                          :input="'Modifier'"
                          :width="'10vw'"
                          :height="'9vh'"
                          :id="PrimButton">
                        </MainButton>
                      </template>
                    </ItemDetail>
                  </div>
                </div>
              </div>
            </Transition>
            <div class="flex justify-center">
                <hr v-if="orders.length" class="mt-[-1.5%] border-t border-gray-500 w-[90%]">
            </div>
          </div>
        </body>
        <body v-else class="h-full w-full mt-8">
        <div class="flex flex-col items-center gap-3">
          <img :src="packageIcon" class="w-[30vw] h-[35vh]"/>
          <div class="text-center flex flex-col gap-2">
            <h1 class=" text-3xl font-bold">Votre panier est vide !</h1>
            <h2 class=" text-lg font-semibold">On dirait que vous n'avez aucune commande en cours...</h2>
          </div>
          <MainButton
          :width="'20vw'"
          :height="'9vh'"
          :input="'Accéder au menu'"
          class="mt-3"
          @click="goTo('Home')">
          </MainButton>
        </div>
        </body>
  </main>
</template>

<style scoped>
/* Entrée et sortie avec animation de coulissement */
.slide-enter-active, .slide-leave-active {
  @apply transition-all duration-300 ease-in-out;
}

/* Début de l'animation (fermé) */
.slide-enter-from, .slide-leave-to {
  @apply opacity-0 translate-y-[-10px] scale-95;
}

/* Fin de l'animation (ouvert) */
.slide-enter-to, .slide-leave-from {
  @apply opacity-100 translate-y-0 scale-100;
}

</style>
