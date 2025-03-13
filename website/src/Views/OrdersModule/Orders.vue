<script setup>
import { ref, onMounted } from 'vue';
import ElemDetail from '@/components/OrderDetail.vue';
import { createClient } from '@supabase/supabase-js';
import PrimButton from '@/components/PrimButton.vue';


const supabaseKey = import.meta.env.VITE_SUPABASE_KEY
const supabaseUrl = import.meta.env.VITE_SUPABASE_URL
const supabase = createClient(supabaseUrl, supabaseKey)

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
    return null; // Retourne null si une erreur survient
  }

  // Si l'utilisateur est connecté, on renvoie son ID, sinon on renvoie null
  return data.session?.user?.id || null;
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

    console.log('Data fetched successfully');
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

function getButton(type, status) {
  const item = itemStatus.value.find(item => item.status === status && item.type === type);
  return item ? item.button : null; // Retourne null si aucun élément trouvé
}


onMounted(async () =>{
  userId.value = await getUserSession();
  orders.value = await fetchOrdersWithItems(userId.value);
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
    <body>
      <div v-for="(order, index) in orders" :key="order.id" class="mt-4 flex flex-col gap-4 flex-wrap flex-shrink">
        <ElemDetail class="p-6">
          <template #imgs>
              <img v-if="order.order_items[0].material_items.image" :src="order.order_items[0].material_items.image" alt="Image" class="w-full h-full object-cover">
          </template>

          <template #title>
            <h2 class="text-md font-semibold">Order n°{{ order.id.split("-").pop() }}</h2>
          </template>

          <template #details>
            <h3 class="text-sm font-medium mb-[-1%]">Nombre d'articles: {{ order.order_items.length }}</h3>
            <h3 class="text-sm font-medium mt-[-1%]">Commande passée le {{ order.created_at.split("T")[0] }}</h3> <!-- OU  order.created_at.substring(0, order.created_at.lastIndexOf("T")) -->
          </template>

          <template #button>
            <PrimButton
            :input="'Show details'"
            :width="'10vw'"
            @click="showDetails[index] = !showDetails[index]">
            </PrimButton>
          </template>
        </ElemDetail>
        <Transition name="slide">
          <div v-if="showDetails[index]" class="max-h-fit flex justify-center">
            <div class="border border-y-0 border-x-gray-500 w-[90%] flex flex-col justify-center mt-[-3%]">
              <div v-for="item in order.order_items"
                :key="item.item_id"
                class=" w-[100%]">
                <ElemDetail class="p-6">
                  <template #imgs>
                    <img v-if="item.material_items.image" :src="item.material_items.image" :alt="item.material_items.name" class="w-full h-full object-cover">
                  </template>
                  <template #title>
                    <h2 class="text-sm font-semibold ">Nom: {{ item.material_items.name }}</h2>
                    <h3 class="text-[0.75em] font-medium"> Statut: {{ item.status }}</h3>
                  </template>
                  <template #details>
                    <h3 class=" text-[0.75em] font-medium mb-[-1%]">Référence: {{ item.item_id.split("-").pop() }}</h3>
                    <h3 class="text-[0.75em] font-medium mt-[-1%]">Quantité: {{ item.quantity }}</h3> <!-- OU  order.created_at.substring(0, order.created_at.lastIndexOf("T")) -->
                  </template>
                  <template #button>
                    <PrimButton
                      :input="getButton(item.material_items.type, item.status)"
                      width="'10vw'"
                      :disabled="getButton(item.material_items.type, item.status) === 'None'"
                      :class="{
                        'bg-gray-400 cursor-not-allowed': getButton(item.material_items.type, item.status) === 'None',
                      }">
                    </PrimButton>
                  </template>
                </ElemDetail>
              </div>
            </div>
          </div>
        </Transition>
        <div class="flex justify-center">
            <hr v-if="orders.length" class="mt-[-1.8%] border-t border-gray-500 w-[90%]">
        </div>
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
