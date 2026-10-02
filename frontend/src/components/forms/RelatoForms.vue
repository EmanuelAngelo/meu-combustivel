<script setup lang="ts">
import { useAppContext } from "../../composables/appContext";
const {
  isDemo,
  modalSaving,
  dateInput,
  form,
  error,
  stationDetail,
  modalError,
  reportDraft,
  submitReport,
} = useAppContext();
import { Info } from "lucide-vue-next";
</script>
<template>
  <div class="eyebrow">RELATO DO USUÁRIO</div>
  <h2>Relatar um problema</h2>
  <p>{{ stationDetail?.name }}</p>
  <div class="info-strip">
    <Info :size="20" />
    <p>
      Um relato não comprova adulteração.
      {{
        isDemo
          ? "Nesta prévia, ele será apenas simulado, sem publicação."
          : "Seu relato passará por moderação antes de qualquer publicação."
      }}
    </p>
  </div>
  <form @submit.prevent="submitReport">
    <label class="field"
      ><span>O que você percebeu?</span
      ><select v-model="reportDraft.type">
        <option>Falhas após abastecer</option>
        <option>Queda de rendimento</option>
        <option>Dificuldade para ligar</option>
        <option>Divergência nos valores</option>
        <option>Calibrador indisponível</option>
        <option>Outro problema</option>
      </select></label
    ><label class="field"
      ><span>Data do ocorrido</span
      ><input
        type="date"
        v-model="reportDraft.date"
        :max="dateInput()"
        required /></label
    ><label class="field"
      ><span>Descreva o ocorrido</span
      ><textarea
        v-model="reportDraft.description"
        rows="4"
        minlength="15"
        maxlength="1500"
        required
        placeholder="Conte o que aconteceu, sem incluir dados pessoais."
      ></textarea>
    </label>
    <p v-if="modalError" role="alert" class="form-error">{{ modalError }}</p>
    <button class="primary-button wide" :disabled="modalSaving">
      {{
        modalSaving
          ? "Enviando…"
          : isDemo
            ? "Simular envio para moderação"
            : "Enviar para moderação"
      }}
    </button>
  </form>
</template>
