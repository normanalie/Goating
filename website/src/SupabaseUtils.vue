
<script setup>

/*

INUTILE POUR L'INSTANT J'Y METS JUSTE DES FONCTIONS SUPABASE POUR POUVOIR LES RETROUVER

*/



async function signOut() {
  const { error } = await supabase.auth.signOut();
  if (error) {
    console.error('Erreur de déconnexion:', error.message);
  } else {
    console.log('Déconnexion réussie');
  }
}


async function linkItemToOrderInProcess(userId) { // ya surement plus efficace
  try {
    const { data: orders, error } = await supabase
      .from('orders')
      .select("*")
      .eq('user_id', userId)
      .eq('order_status', 'processing');

    if (error) throw error;
    // Vérifie si des commandes en cours sont trouvées
    if(orders.length === 0){
      try {
        const { data, error } = await supabase
        .from('orders')
        .insert([
          {
            user_id: userId,
            order_status: 'processing',
          }
        ])
        .select()
        if(error) throw error
        console.log("Création de la commande réussie: " + data);
        orders.push(data[0]);

      } catch (e) {
        console.log("[SUPABASE] Error during order insert: " + e)
      }

    }
    try {
      const orderId = orders[0].id
      const { data, error } =  await supabase
      .from('order_items')
      .update({ order_id: orderId })
      .is('order_id', null)  // Mettre à jour seulement les items sans order_id
      .select();

      if (error) throw error;
      console.log("[SUPABASE] Update successful")
    } catch (e) {
      console.log(e)
    }
  } catch (e) {
    console.log("[SUPABASE] Processing orders fetch error: " + e);
    return null; // Renvoie null en cas d'erreur
  }
}

async function addItemToOrder(){
  try{
    const { data, error } = await supabase
  .from('order_items')
  .insert([
    {
      quantity: Number(sliderValue.value),
      status: 'reserved',
      item_id: itemRef.value,
      order_id: null,
    }
  ])
  .select()
  if(error) throw error
  console.log("Item ajouté à la commande avec succès: " + data)
  linkItemToOrderInProcess(userId)
  } catch (e) {
    console.log("Erreur lors de l'ajout de l'item à la commande:" + e)
  }
}
</script>
