    <template>
    <button id="filterBtn">
      <span class="btn-text">
        <slot>text</slot>
      </span>
      <img v-if="icon" :src="icon" alt="Icon" class="btn-icon" />
    </button>
  </template>

  <script setup>
  defineProps({
    icon: String, // Chemin de l'image (optionnel)
  });
  </script>

  <style scoped>
  #filterBtn {
    width: 13vw;
    height: 3.54vh;
    border-radius: 0.25em;
    text-align: center;
    display: flex;
    align-items: center;
    justify-content: flex-start; /* Décale le texte vers la gauche */
    padding: 0 10px; /* Ajoute un padding pour éviter que le texte colle au bord */
    gap: 8px; /* Espacement entre l’image et le texte */
    background-color: #007bff; /* Couleur de fond */
    color: white;
    font-size: 1em;
    cursor: pointer;
    border: none;
  }

  .btn-icon {
    width: 1.5em; /* Taille relative à la police */
    height: 1.5em;
  }

  .btn-text {
    flex-grow: 1; /* Permet au texte de prendre la place restante */
    text-align: left; /* Aligne le texte à gauche */
  }
  </style>
