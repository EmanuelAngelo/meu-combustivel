<script setup lang="ts">
import { useAppContext } from "../../composables/appContext";
const {
  isDemo,
  modalSaving,
  form,
  error,
  modalError,
  stationDraft,
  saveStation,
  locating,
  locate,
} = useAppContext();
import { Plus, Navigation } from "lucide-vue-next";
import GooglePostoMapa from "../mapas/GooglePostoMapa.vue";
</script>
<template>
  <div class="eyebrow">CADASTRO COLABORATIVO</div>
  <h2>Cadastrar posto</h2>
  <p>
    {{
      isDemo
        ? "Cadastro manual de demonstração."
        : "Confira os dados do estabelecimento antes de salvar."
    }}
  </p>
  <GooglePostoMapa @select="Object.assign(stationDraft, $event)" />
  <form @submit.prevent="saveStation">
    <label class="field"
      ><span>Nome do posto</span
      ><input v-model="stationDraft.name" required maxlength="120" /></label
    ><label class="field"
      ><span>Endereço</span
      ><input v-model="stationDraft.address" required maxlength="200"
    /></label>
    <div class="field-grid">
      <label class="field"
        ><span>Cidade</span
        ><input v-model="stationDraft.city" required /></label
      ><label class="field"
        ><span>Estado (UF)</span
        ><input
          v-model="stationDraft.state"
          required
          maxlength="2"
          minlength="2"
      /></label>
    </div>
    <button
      type="button"
      class="secondary-button wide"
      @click="locate"
      :disabled="locating"
    >
      <Navigation :size="17" />{{
        locating ? "Buscando localização…" : "Usar minha localização"
      }}
    </button>
    <div class="field-grid">
      <label class="field"
        ><span>Latitude</span
        ><input
          v-model="stationDraft.lat"
          placeholder="-2.5025"
          required /></label
      ><label class="field"
        ><span>Longitude</span
        ><input v-model="stationDraft.lng" placeholder="-44.2896" required
      /></label>
    </div>
    <label class="field"
      ><span>Calibrador de pneus</span
      ><select v-model="stationDraft.air">
        <option>Não informado</option>
        <option>Gratuito</option>
        <option>Pago</option>
      </select></label
    >
    <p v-if="modalError" role="alert" class="form-error">{{ modalError }}</p>
    <button class="primary-button wide" :disabled="modalSaving">
      <Plus :size="18" />{{
        modalSaving
          ? "Salvando…"
          : isDemo
            ? "Adicionar nesta sessão"
            : "Cadastrar posto"
      }}
    </button>
  </form>
</template>
