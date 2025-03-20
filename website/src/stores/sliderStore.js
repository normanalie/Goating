import { defineStore } from 'pinia';

export const useSliderStore = defineStore('slider', {
  state: () => ({
    sliders: {}  // Un objet qui stocke les valeurs des sliders
  }),
  actions: {
    setSliderValue(id, value) {
      this.sliders[id] = value;
    }
  },
  getters: {
    getSliderValue: (state) => (id) => state.sliders[id] || 0,  // ✅ Getter réactif
  },
  persist: true
});
