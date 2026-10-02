<script setup lang="ts">
import { useAppContext } from "../composables/appContext";
const {
  page,
  vehicles,
  money,
  num,
  displayDate,
  vehicleName,
  stationName,
  go,
  historyQuery,
  historyVehicle,
  historyMonth,
  historyMonths,
  filteredFills,
  openFill,
  exportHistory,
} = useAppContext();
import { Plus, ChevronRight, Search, Download } from "lucide-vue-next";
</script>
<template>
  <div class="page-heading">
    <div>
      <div class="eyebrow">CADA REGISTRO, UMA HISTÓRIA</div>
      <h1>Seus abastecimentos</h1>
      <p>Compare valores e acompanhe cada parada.</p>
    </div>
    <button class="primary-button" @click="go('fill')">
      <Plus :size="18" />Novo abastecimento
    </button>
  </div>
  <div class="filter-bar">
    <div class="search-input">
      <Search :size="18" /><input
        v-model="historyQuery"
        placeholder="Buscar por posto, veículo ou combustível"
        aria-label="Buscar abastecimentos"
      />
    </div>
    <select v-model="historyVehicle" aria-label="Filtrar veículo">
      <option value="all">Todos os veículos</option>
      <option v-for="v in vehicles" :value="v.id">
        {{ v.brand }} {{ v.model }}
      </option></select
    ><select v-model="historyMonth" aria-label="Filtrar mês">
      <option value="all">Todo o período</option>
      <option v-for="m in historyMonths" :value="m">
        {{
          new Date(m + "-02").toLocaleDateString("pt-BR", {
            month: "long",
            year: "numeric",
          })
        }}
      </option>
    </select>
  </div>
  <section class="card table-card">
    <div class="section-title">
      <div>
        <h2>{{ filteredFills.length }} abastecimentos</h2>
        <p>
          {{ money(filteredFills.reduce((s, f) => s + f.total, 0)) }} no período
          selecionado
        </p>
      </div>
      <button class="secondary-button" @click="exportHistory">
        <Download :size="17" />Exportar CSV
      </button>
    </div>
    <div class="table-scroll">
      <table>
        <thead>
          <tr>
            <th>Posto / data</th>
            <th>Veículo</th>
            <th>Preço / L</th>
            <th>Litros</th>
            <th>Total pago</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="f in filteredFills" :key="f.id">
            <td>
              <strong>{{ stationName(f.station) }}</strong
              ><small>{{ displayDate(f.date) }} · {{ f.fuel }}</small>
            </td>
            <td>{{ vehicleName(f.vehicle) }}</td>
            <td>{{ money(f.price) }}</td>
            <td>{{ num(f.liters, 3) }} L</td>
            <td>
              <strong>{{ money(f.total) }}</strong>
            </td>
            <td>
              <button
                class="icon-button"
                @click="openFill(f)"
                aria-label="Ver detalhes do abastecimento"
              >
                <ChevronRight :size="19" />
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    <div v-if="!filteredFills.length" class="empty-state">
      <Search :size="30" />
      <h3>Nenhum abastecimento encontrado</h3>
      <p>Experimente outro posto, veículo ou período.</p>
      <button
        class="text-button"
        @click="
          historyQuery = '';
          historyVehicle = 'all';
          historyMonth = 'all';
        "
      >
        Limpar filtros
      </button>
    </div>
  </section>
</template>
