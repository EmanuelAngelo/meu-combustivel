<script setup lang="ts">
import { useAppContext } from "../../composables/appContext";
const {
  money,
  num,
  displayDate,
  vehicleName,
  stationName,
  detailFill,
  closeModal,
} = useAppContext();
</script>
<template>
  <div v-if="detailFill">
    <div class="eyebrow">SEU REGISTRO</div>
    <h2>Detalhes do abastecimento</h2>
    <p>{{ stationName(detailFill.station) }}</p>
    <div class="detail-total">{{ money(detailFill.total) }}</div>
    <dl class="detail-list">
      <div>
        <dt>Data</dt>
        <dd>{{ displayDate(detailFill.date) }}</dd>
      </div>
      <div>
        <dt>Veículo</dt>
        <dd>{{ vehicleName(detailFill.vehicle) }}</dd>
      </div>
      <div>
        <dt>Combustível</dt>
        <dd>{{ detailFill.fuel }}</dd>
      </div>
      <div>
        <dt>Preço informado</dt>
        <dd>{{ money(detailFill.price) }} / L</dd>
      </div>
      <div>
        <dt>Quantidade</dt>
        <dd>{{ num(detailFill.liters, 3) }} L</dd>
      </div>
      <div>
        <dt>Preço efetivo</dt>
        <dd>{{ money(detailFill.total / detailFill.liters) }} / L</dd>
      </div>
      <div>
        <dt>Quilometragem</dt>
        <dd>
          {{
            detailFill.km === null
              ? "Não informada"
              : num(detailFill.km) + " km"
          }}
        </dd>
      </div>
      <div>
        <dt>Tanque cheio</dt>
        <dd>{{ detailFill.full ? "Sim" : "Não" }}</dd>
      </div>
      <div>
        <dt>Pagamento</dt>
        <dd>{{ detailFill.payment }}</dd>
      </div>
    </dl>
    <p v-if="detailFill.note" class="note-display">{{ detailFill.note }}</p>
    <button class="secondary-button wide" @click="closeModal">Fechar</button>
  </div>
</template>
