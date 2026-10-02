<script setup lang="ts">
import { useAppContext } from "../../composables/appContext";
const {
  parseDecimal,
  form,
  selectedVehicle,
  calculation,
  money,
  num,
  displayDate,
  latest,
  comparison,
} = useAppContext();
import { Fuel, History, Info, Bike, ReceiptText } from "lucide-vue-next";
</script>
<template>
  <aside class="summary-column">
    <section class="vehicle-summary">
      <div class="summary-top"><span>SEU VEÍCULO</span><Bike :size="28" /></div>
      <h2>{{ selectedVehicle?.brand }} {{ selectedVehicle?.model }}</h2>
      <p>{{ selectedVehicle?.type }} · {{ selectedVehicle?.year }}</p>
      <div class="tank-capacity">
        <span><Fuel :size="16" />Capacidade do tanque</span
        ><strong>{{ num(selectedVehicle?.capacity ?? 0) }} L</strong>
      </div>
    </section>
    <section class="card receipt">
      <div class="receipt-title">
        <ReceiptText :size="19" />
        <h2>Conferência da bomba</h2>
      </div>
      <p class="receipt-subtitle">Uma conta simples. Mais tranquilidade.</p>
      <div class="receipt-line">
        <span>Preço informado</span
        ><strong
          >{{ calculation ? money(parseDecimal(form.price)) : "—"
          }}<small> / L</small></strong
        >
      </div>
      <div class="receipt-line">
        <span>Litros abastecidos</span
        ><strong>{{
          calculation ? num(parseDecimal(form.liters), 3) + " L" : "—"
        }}</strong>
      </div>
      <div class="receipt-divider"></div>
      <div class="receipt-line">
        <span>Total esperado</span
        ><strong>{{ calculation ? money(calculation.expected) : "—" }}</strong>
      </div>
      <div class="receipt-total">
        <span>Total pago</span
        ><strong>{{
          calculation ? money(parseDecimal(form.total)) : "R$ —"
        }}</strong>
      </div>
      <div v-if="calculation" class="receipt-difference">
        <span>Diferença</span
        ><strong :class="{ negative: !calculation.consistent }">{{
          money(calculation.difference)
        }}</strong>
      </div>
      <div class="receipt-effective">
        <span>Preço efetivo por litro</span
        ><strong>{{ calculation ? money(calculation.effective) : "—" }}</strong>
      </div>
      <p class="receipt-footnote">
        <Info :size="15" /><span
          >A conferência compara os valores digitados. Não verifica a qualidade
          do combustível nem o volume entregue.</span
        >
      </p>
    </section>
    <section v-if="latest" class="last-fill">
      <div class="last-heading">
        <History :size="17" />
        <h3>Seu último abastecimento</h3>
      </div>
      <p>{{ displayDate(latest.date) }} · {{ latest.fuel }}</p>
      <div>
        <strong>{{ money(latest.total) }}</strong
        ><span>{{ num(latest.liters, 3) }} litros</span>
      </div>
      <p v-if="comparison !== null" class="comparison">
        {{
          Math.abs(comparison) < 0.02
            ? "Mesmo custo por litro do último registro."
            : `${money(Math.abs(comparison))} ${comparison < 0 ? "a menos" : "a mais"} para a mesma quantidade de litros.`
        }}
      </p>
    </section>
  </aside>
</template>
