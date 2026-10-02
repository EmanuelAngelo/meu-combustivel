<script setup lang="ts">
import { useAppContext } from "../composables/appContext";
const {
  isDemo,
  page,
  stations,
  fills,
  money,
  num,
  displayDate,
  vehicleName,
  stationName,
  sortedFills,
  totalSpend,
  totalLiters,
  average,
  go,
  openFill,
} = useAppContext();
import {
  Droplet,
  Fuel,
  MapPin,
  Plus,
  ChevronRight,
  ArrowUpRight,
  Wallet,
} from "lucide-vue-next";
</script>
<template>
  <div class="page-heading">
    <div>
      <div class="eyebrow">SEU CAMINHO, SOB CONTROLE</div>
      <h1>Visão geral</h1>
      <p>Um olhar sobre seus veículos e abastecimentos.</p>
    </div>
    <button class="primary-button" @click="go('fill')">
      <Plus :size="18" />Novo abastecimento
    </button>
  </div>
  <div class="stats-grid">
    <section class="stat-card">
      <div><span>Total registrado</span><Wallet :size="20" /></div>
      <strong>{{ money(totalSpend) }}</strong
      ><small
        >{{ fills.length }} abastecimentos
        {{ isDemo ? "nesta demonstração" : "registrados" }}</small
      >
    </section>
    <section class="stat-card">
      <div><span>Volume abastecido</span><Droplet :size="20" /></div>
      <strong>{{ num(totalLiters, 3) }} <em>L</em></strong
      ><small>Todos os veículos cadastrados</small>
    </section>
    <section class="stat-card">
      <div><span>Preço médio pago</span><Fuel :size="20" /></div>
      <strong>{{ money(average) }} <em>/ L</em></strong
      ><small>Média ponderada pelo volume</small>
    </section>
  </div>
  <div class="overview-grid">
    <section class="card chart-card">
      <div class="section-title">
        <div>
          <h2>Seus últimos abastecimentos</h2>
          <p>Valor total por registro</p>
        </div>
        <span class="subtle-pill">Em reais</span>
      </div>
      <div v-if="!fills.length" class="empty-state">
        <Fuel :size="30" />
        <p>Seu primeiro abastecimento aparecerá aqui.</p>
      </div>
      <div v-else class="bar-chart">
        <div
          v-for="f in sortedFills.slice(0, 7).reverse()"
          :key="f.id"
          class="chart-column"
        >
          <span>{{ money(f.total) }}</span>
          <div
            class="chart-bar"
            :style="{
              height:
                Math.max(
                  8,
                  (f.total / Math.max(...fills.map((x) => x.total))) * 135,
                ) + 'px',
            }"
          ></div>
          <small>{{ displayDate(f.date) }}</small>
        </div>
      </div>
    </section>
    <section class="recommend-card">
      <span class="eyebrow">EXPLORE A REGIÃO</span><MapPin :size="30" />
      <h2>Um bom preço pode estar no seu caminho.</h2>
      <p>Compare os postos e encontre quem oferece calibrador gratuito.</p>
      <button class="light-button" @click="go('stations')">
        Ver postos no mapa<ArrowUpRight :size="18" /></button
      ><small>{{
        isDemo
          ? "Preços fictícios nesta prévia."
          : "Preços compartilhados pela comunidade."
      }}</small>
    </section>
  </div>
  <section class="card table-card">
    <div class="section-title">
      <h2>Histórico recente</h2>
      <button class="text-button" @click="go('history')">
        Ver todos<ChevronRight :size="16" />
      </button>
    </div>
    <div class="table-scroll">
      <table>
        <thead>
          <tr>
            <th>Posto / data</th>
            <th>Veículo</th>
            <th>Litros</th>
            <th>Total</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="f in sortedFills.slice(0, 4)" :key="f.id">
            <td>
              <strong>{{ stationName(f.station) }}</strong
              ><small>{{ displayDate(f.date) }} · {{ f.fuel }}</small>
            </td>
            <td>{{ vehicleName(f.vehicle) }}</td>
            <td>{{ num(f.liters, 3) }} L</td>
            <td>
              <strong>{{ money(f.total) }}</strong>
            </td>
            <td>
              <button
                class="icon-button"
                @click="openFill(f)"
                aria-label="Ver abastecimento"
              >
                <ChevronRight :size="19" />
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </section>
</template>
