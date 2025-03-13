<script setup>
import { ref } from 'vue'
import InputField from './InputField.vue';


const showPassword = ref(false)
const placehldPassword = ref('Mot de passe')


</script>

<template>
<div>
<inputField :type="showPassword ? 'text' : 'password'" :placeholder="placehldPassword"></inputField>
<button v-if="showPassword" class="test" @click="showPassword == !showPassword"><img class="eyeimg" src="../assets/Feather Icons.png"></button>
<button v-else class="test" @click="showPassword == !showPassword"><img class="eyeimg" src="../assets/hiddenEye.png"/></button>
</div>

</template>

<style>
    .test{
        position: absolute;
        width: 2.5vw;
        align-self: end;
        background:none;
        border: none;
        top: 50%;
        transform:translateX(-100%);
        transform: translateY(-15%);
    }


</style>