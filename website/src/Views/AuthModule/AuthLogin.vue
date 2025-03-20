<script setup>
import { ref, onMounted } from 'vue'
import { createClient } from '@supabase/supabase-js'
import { useRouter } from 'vue-router'
import InputField from '@/components/InputField.vue'
import PrimButton from '@/components/PrimButton.vue'
import SecButton from '@/components/SecButton.vue'
import TerButton from '@/components/TerButton.vue'
import { supabase } from '@/supabase.js';

// Initialisation de Supabase

// Gestion des données et de l'état utilisateur
const router = useRouter()
const user = ref(null)
//const logo = ref('StoreBot')

// Champs de formulaire
const userInput = ref('')
const pwdInput = ref('')
const errorMessage = ref('')

async function isUserLoggedIn() {
  const { data } = await supabase.auth.getSession()
  user.value = data.session?.user || null
}

// Fonction de connexion
async function loginUserWithEmail() {
  try {
    errorMessage.value = ''
    const { data, error } = await supabase.auth.signInWithPassword({
      email: userInput.value,
      password: pwdInput.value,
    })

    if (error) throw error

    console.log('Connexion réussie.')
    user.value = data.user
    isUserLoggedIn()
    router.push('/')
  } catch (e) {
    errorMessage.value = 'Erreur de connexion : ' + e.message
    console.error(e)
  }
}

async function loginUserWithNumber(staffNumber, password) {
  try {
    // Récupérer l'email à partir du numéro de staff
    const { data: emailData, error: emailError } = await supabase.rpc('get_email_for_staff_num', {
      staff_num: staffNumber,
    })

    if (emailError) throw emailError
    if (!emailData) throw new Error('Aucun email trouvé pour ce numéro de staff.')

    // Tentative de connexion avec l'email récupéré
    const { data, error } = await supabase.auth.signInWithPassword({
      email: emailData,
      password: password,
    })

    if (error) throw error

    user.value = data.user
    errorMessage.value = ''
    return { user: data.user, error: null }
  } catch (e) {
    //console.error('[SUPABASE] Erreur de connexion :', e.message)
    errorMessage.value = e.message
    return { user: null, error: e.message }
  }
}

const loginUser = () => {
  if (/^\d+$/.test(userInput.value)) {
    loginUserWithNumber(userInput.value)
  } else {
    loginUserWithEmail(userInput.value)
  }
}



// Vérification de la session utilisateur au montage du composant
onMounted(async () => {})
</script>

<template>
  <div class="font-[Arial] w-full flex flex-row items-stretch justify-center">
    <div class="w-[60vw] md:w-[30vw] h-fit p-6 rounded-tl-md rounded-bl-md bg-[#e6e6e6]">
      <h2 class="text-2xl mb-5 font-bold">Connexion</h2>

      <div class="flex flex-col gap-[5vh]">
        <div>
          <label class="block mb-1 ml-1">Identifiant</label>
          <InputField v-model="userInput" placeholder="e-mail ou n° étudiant" class="w-full" />
        </div>

        <div>
          <label class="block mb-1 ml-1">Mot de passe</label>
          <InputField
            v-model="pwdInput"
            placeholder="mot de passe"
            type="password"
            class="w-full"
          />
        </div>

        <PrimButton input="Se connecter" class="w-[90%] mx-auto" @click="loginUser" />
        <SecButton input="Aide" class="w-[90%] mx-auto mt-[-5%]" />
        <p v-if="errorMessage" class="text-red-600 text-center mt-2">{{ errorMessage }}</p>
      </div>
    </div>
    <div
      class="hidden md:block w-[30vw] h- p-6 bg-gradient-to-br from-[#003399] to-[#DDDBFF] rounded-tr-md rounded-br-md"
    >
      <div class="flex flex-row justify-between items-center text-white">
        <h2 class="text-left text-xl font-semibold">STOREBOT</h2>
        <TerButton></TerButton>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* Ajoute ici du CSS global ou Tailwind gère déjà l'essentiel */
</style>
