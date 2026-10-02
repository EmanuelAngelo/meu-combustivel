<script setup lang="ts">
import { useAppContext } from "../composables/appContext";
const { page, vehicles, fills, form, num, go, newVehicle, editVehicle } =
  useAppContext();
import { Fuel, Car, Plus, Info, Bike, Star } from "lucide-vue-next";
</script>
<template>
  <div class="page-heading">
    <div>
      <div class="eyebrow">PRONTOS PARA O PRÓXIMO CAMINHO</div>
      <h1>Meus veículos</h1>
      <p>Um histórico separado para cada veículo.</p>
    </div>
    <button class="primary-button" @click="newVehicle">
      <Plus :size="18" />Adicionar veículo
    </button>
  </div>
  <div class="vehicle-grid">
    <section v-for="v in vehicles" :key="v.id" class="card vehicle-card">
      <div class="vehicle-card-top">
        <span class="vehicle-icon"
          ><component :is="v.type === 'Moto' ? Bike : Car" :size="32" /></span
        ><span v-if="v.primary" class="subtle-pill"
          ><Star :size="13" />Principal</span
        >
      </div>
      <h2>{{ v.brand }} {{ v.model }}</h2>
      <p>{{ v.type }} · {{ v.year }}</p>
      <div class="vehicle-specs">
        <div>
          <span>Capacidade do tanque</span
          ><strong>{{ num(v.capacity) }} litros</strong>
        </div>
        <div>
          <span>Combustível</span><strong>{{ v.fuel }}</strong>
        </div>
        <div>
          <span>Abastecimentos</span
          ><strong>{{ fills.filter((f) => f.vehicle === v.id).length }}</strong>
        </div>
      </div>
      <div class="vehicle-actions">
        <button class="text-button" @click="editVehicle(v)">
          Editar veículo</button
        ><button
          class="secondary-button"
          @click="
            form.vehicle = v.id;
            go('fill');
          "
        >
          <Fuel :size="16" />Abastecer
        </button>
      </div>
    </section>
    <button class="add-vehicle-card" @click="newVehicle">
      <span><Plus :size="27" /></span><strong>Mais um veículo?</strong>
      <p>Carro, moto, van e muito mais.</p>
    </button>
  </div>
  <div class="info-strip">
    <Info :size="20" />
    <p>
      A capacidade do tanque ajuda a conferir os registros. Ela não indica
      quanto combustível ainda resta no veículo.
    </p>
  </div>
</template>
