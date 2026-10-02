<script setup lang="ts">
import { useAppContext } from "../composables/appContext";
const { page, vehicles, newVehicle } = useAppContext();
import { Car, ShieldCheck } from "lucide-vue-next";

import AbastecimentoForms from "../components/forms/AbastecimentoForms.vue";
</script>
<template>
  <div class="page-heading">
    <div>
      <div class="eyebrow">CADA LITRO CONTA</div>
      <h1>Novo abastecimento</h1>
      <p>Registre os valores da bomba. A gente confere a conta.</p>
    </div>
    <div class="heading-tag"><ShieldCheck :size="16" />Registro privado</div>
  </div>
  <div v-if="!vehicles.length" class="card empty-state">
    <Car :size="36" />
    <h2>Cadastre seu primeiro veículo</h2>
    <p>Informe a marca, o modelo e a capacidade do tanque para começar.</p>
    <button class="primary-button" @click="newVehicle">
      Adicionar veículo
    </button>
  </div>
  <AbastecimentoForms v-else />
</template>
