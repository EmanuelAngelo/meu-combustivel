<script setup lang="ts">
import { useAppContext } from "../../composables/appContext";
const {
  isDemo,
  modalSaving,
  form,
  error,
  modalError,
  editingId,
  vehicleDraft,
  saveVehicle,
} = useAppContext();
import { Check } from "lucide-vue-next";
</script>
<template>
  <div class="eyebrow">SUA GARAGEM</div>
  <h2>{{ editingId ? "Editar veículo" : "Adicionar veículo" }}</h2>
  <p>
    {{
      isDemo
        ? "Os dados ficam apenas nesta sessão de demonstração."
        : "Este veículo e seu histórico ficam disponíveis somente para você."
    }}
  </p>
  <form @submit.prevent="saveVehicle">
    <div class="field-grid">
      <label class="field"
        ><span>Tipo</span
        ><select v-model="vehicleDraft.type">
          <option>Moto</option>
          <option>Carro</option>
          <option>Van</option>
          <option>Caminhonete</option>
          <option>Caminhão</option>
          <option>Outro</option>
        </select></label
      ><label class="field"
        ><span>Ano</span
        ><input
          type="number"
          v-model="vehicleDraft.year"
          min="1900"
          :max="new Date().getFullYear() + 1"
          required
      /></label>
    </div>
    <label class="field"
      ><span>Marca</span
      ><input
        v-model="vehicleDraft.brand"
        placeholder="Ex.: Yamaha"
        required
        maxlength="80" /></label
    ><label class="field"
      ><span>Modelo</span
      ><input
        v-model="vehicleDraft.model"
        placeholder="Ex.: Fluo 125"
        required
        maxlength="80"
    /></label>
    <div class="field-grid">
      <label class="field"
        ><span>Capacidade do tanque (L)</span
        ><input
          v-model="vehicleDraft.capacity"
          inputmode="decimal"
          placeholder="Ex.: 4,2"
          required /></label
      ><label class="field"
        ><span>Combustível principal</span
        ><select v-model="vehicleDraft.fuel">
          <option>Gasolina comum</option>
          <option>Gasolina aditivada</option>
          <option>Etanol</option>
          <option>Flex</option>
          <option>Diesel S10</option>
          <option>Diesel S500</option>
        </select></label
      >
    </div>
    <label class="check-row"
      ><input type="checkbox" v-model="vehicleDraft.primary" />Usar como veículo
      principal</label
    >
    <p v-if="modalError" role="alert" class="form-error">{{ modalError }}</p>
    <button class="primary-button wide" :disabled="modalSaving">
      <Check :size="18" />{{ modalSaving ? "Salvando…" : "Salvar veículo" }}
    </button>
  </form>
</template>
