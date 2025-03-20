import { defineStore } from 'pinia'

export const useOrderStore = defineStore('order', {
  state: () => ({
    orders: []
  }),
  actions: {
    addItemToOrder(item) {
      const index = this.orders.findIndex(orderItem => orderItem.item_id === item.item_id);
      if (index === -1) {
        this.orders.push(item);
        console.log("Nouvel élément ajouté: ", JSON.stringify(item, null, 2));
      } else {
        this.orders[index] = item;
        console.log("Élément existant écrasé: ", JSON.stringify(item, null, 2));
      }
    },
    removeItemById(id) {
      this.orders = this.orders.filter((item) => item.item_id !== id);
      console.log(`Élément avec l'ID ${id} supprimé.`);
    },
    clearOrders() {
      this.orders = []
      console.log("Commandes supprimées")
    },
    clearOrdersWithId(userId) {
        this.orders = this.orders.filter((item) => item.user_id !== userId);
        console.log("Commandes du user n°" + userId + " supprimées");
    }
  },
  getters: {
    getOrders: (state) => state.orders, // Getter pour récupérer le tableau
    getOrderById: (state) => (id) => state.orders.find(order => order.user_id === id),
    getOrdersByUserId: (state) => (user_id) => {
      return state.orders.filter(order => order.user_id === user_id);
    }


  },
  persist: true  // Active la persistance automatique
})
