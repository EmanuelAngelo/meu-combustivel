<script setup lang="ts">
import { computed } from "vue";
import type { Station } from "../../types/domain";
const props = defineProps<{ station: Station; commonPayment: string }>();
const price = (value: number | null | undefined) =>
  value == null
    ? "Não informado"
    : new Intl.NumberFormat("pt-BR", {
        style: "currency",
        currency: "BRL",
        minimumFractionDigits: 3,
      }).format(value);
const date = (value?: string) =>
  value ? new Date(value + "T12:00:00").toLocaleDateString("pt-BR") : "";
const difference = computed(() =>
  props.station.common_price == null || props.station.credit_price == null
    ? null
    : Math.round(
        (props.station.credit_price - props.station.common_price) * 1000,
      ) / 1000,
);
</script>
<template>
  <span class="price-comparison">
    <span
      >Comum ({{ commonPayment }}): <b>{{ price(station.common_price) }}</b
      ><small v-if="station.common_updated">
        · {{ date(station.common_updated) }}</small
      ></span
    >
    <span
      >Crédito: <b>{{ price(station.credit_price) }}</b
      ><small v-if="station.credit_updated">
        · {{ date(station.credit_updated) }}</small
      ></span
    >
    <span
      v-if="difference !== null"
      :class="{ 'credit-surcharge': difference > 0 }"
      >{{
        difference === 0
          ? "Mesmo valor informado"
          : `${price(Math.abs(difference))}/L ${difference > 0 ? "a mais" : "a menos"} no crédito`
      }}</span
    >
    <small
      v-if="
        difference !== null && station.common_updated !== station.credit_updated
      "
      >Informações de datas diferentes. Confirme os valores no posto.</small
    >
  </span>
</template>
