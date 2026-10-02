<script setup lang="ts">
const commonPayment = defineModel<string>("commonPayment", { required: true });
const commonPrice = defineModel<string>("commonPrice", { required: true });
const creditPrice = defineModel<string>("creditPrice", { required: true });
</script>
<template>
  <details class="price-fields">
    <summary>Preço comum e no crédito (opcional)</summary>
    <p>
      Informe os preços que você conferiu neste posto, para o combustível e a
      data deste abastecimento. Deixe em branco o que não souber.
    </p>
    <div class="field-grid">
      <label class="field"
        ><span>Pagamento do preço comum</span
        ><select v-model="commonPayment">
          <option>Pix</option>
          <option>Dinheiro</option>
          <option>Débito</option>
        </select></label
      >
      <label class="field"
        ><span>Preço comum / L (R$)</span
        ><input
          v-model="commonPrice"
          inputmode="decimal"
          placeholder="Ex.: 6,199"
      /></label>
      <label class="field"
        ><span>Preço no crédito / L (R$)</span
        ><input
          v-model="creditPrice"
          inputmode="decimal"
          placeholder="Ex.: 6,399"
      /></label>
    </div>
    <small
      >Se não houver diferença, informe o mesmo valor. Esses preços só serão
      publicados se você marcar “Contribuir com o preço deste posto”.</small
    >
  </details>
</template>
