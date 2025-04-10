import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import { supabase } from '@/supabase.js'

export const useMenuStore = defineStore('menuStore', {
  state: () => ({
    items: [],
    isLoaded: false,
    searchQuery: '',
  }),
  actions: {
    async fetchItems() {
      //if (this.isLoaded) return;

      const { data, error } = await supabase
      .from('material_types')
      .select('*');
      if (error) {
        console.error('Erreur lors du chargement des items: ', error);
        return;
      }
      console.log('Récupération des items réussie.')
      this.items = data.reverse();
      this.isLoaded = true;
    },
    setSearchQuery(query) {
      this.searchQuery = query
    },
    refreshPage(){
      this.isLoaded = false;
    }

  },
  getters: {
    getItems: (state) => state.items,
    filteredItems: (state) => {
      if (!state.searchQuery) return state.items
      return state.items.filter(item =>
        (item.name ?? '').toLowerCase().includes(state.searchQuery.toLowerCase())
        || (item.id ?? '').toLowerCase().includes(state.searchQuery.toLowerCase())
        || (item.type ?? '').toLowerCase().includes(state.searchQuery.toLowerCase())
        || (item.description ?? '').toLowerCase().includes(state.searchQuery.toLowerCase())


      )
    }
  },
  persist: true,
});
