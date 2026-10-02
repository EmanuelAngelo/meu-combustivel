<script setup lang="ts">
import { useAppContext } from "../composables/appContext";
const {
  priceMoney,
  rankedStations,
  isDemo,
  page,
  stations,
  form,
  money,
  displayDate,
  error,
  stationFuel,
  stationPayment,
  commonPayment,
  stationLoading,
  stationError,
  stationQuery,
  region,
  sort,
  onlyAir,
  mapSelected,
  stationDetail,
  fillAt,
  openModal,
  newStation,
  pricedStations,
  refreshStations,
} = useAppContext();
import {
  Fuel,
  MapPin,
  Plus,
  ShieldCheck,
  Info,
  Search,
  Wind,
} from "lucide-vue-next";
import StationMap from "../components/mapas/StationMap.vue";
import PrecosExibicao from "../components/exibicao/PrecosExibicao.vue";
</script>
<template>
  <div class="page-heading">
    <div>
      <div class="eyebrow">ESCOLHA SUA PRÓXIMA PARADA</div>
      <h1>Explore os postos</h1>
      <p>Compare preços e serviços em um só lugar.</p>
    </div>
    <button class="secondary-button" @click="newStation">
      <Plus :size="18" />Cadastrar posto
    </button>
  </div>
  <div class="filter-bar station-filters">
    <div class="search-input">
      <Search :size="18" /><input
        v-model="stationQuery"
        placeholder="Buscar posto ou bairro"
        aria-label="Buscar posto ou bairro"
      />
    </div>
    <select v-model="region" aria-label="Região">
      <option>São Luís</option>
      <option>Maranhão</option>
      <option>Brasil</option></select
    ><select v-model="stationFuel" aria-label="Combustível" :disabled="isDemo">
      <option>Gasolina comum</option>
      <option>Gasolina aditivada</option>
      <option>Etanol</option>
      <option>Diesel S10</option>
      <option>Diesel S500</option></select
    ><select
      v-model="stationPayment"
      aria-label="Pagamento do ranking"
      :disabled="isDemo"
    >
      <option>Pix</option>
      <option>Dinheiro</option>
      <option>Débito</option>
      <option>Crédito</option>
      <option>Aplicativo / desconto</option></select
    ><select
      v-model="commonPayment"
      aria-label="Preço comum de comparação"
      :disabled="isDemo"
    >
      <option value="Pix">Comum: Pix</option>
      <option value="Dinheiro">Comum: dinheiro</option>
      <option value="Débito">Comum: débito</option></select
    ><label class="filter-check"
      ><input type="checkbox" v-model="onlyAir" />Calibrador grátis</label
    >
  </div>
  <div class="map-demo-note">
    <Info :size="15" />{{
      isDemo
        ? "Os postos, preços e posições abaixo são fictícios."
        : "Preços informados nos últimos 7 dias. Os cadastros são feitos pelos usuários."
    }}
  </div>
  <p v-if="stationLoading" role="status">Atualizando preços…</p>
  <p v-if="stationError" class="form-error" role="alert">
    {{ stationError }}
    <button @click="refreshStations" class="text-button">
      Tentar novamente
    </button>
  </p>
  <div class="explore-grid">
    <section class="card ranking">
      <div class="ranking-title">
        <div>
          <h2>Ranking de preços</h2>
          <span>{{ pricedStations.length }} postos com preço informado</span>
        </div>
        <select v-model="sort" aria-label="Ordenar preços">
          <option value="cheap">Menor preço</option>
          <option value="expensive">Maior preço</option>
        </select>
      </div>
      <button
        v-for="(s, index) in rankedStations"
        :key="s.id"
        :class="['station-row', { selected: s.id === mapSelected }]"
        @click="mapSelected = s.id"
      >
        <span class="rank-number">{{
          String(index + 1).padStart(2, "0")
        }}</span>
        <div class="station-description">
          <strong>{{ s.name }}</strong
          ><small>{{ s.address }} · {{ s.state }}</small
          ><span v-if="s.air === 'Gratuito'" class="air-label"
            ><Wind :size="13" />Calibrador grátis</span
          ><span v-else class="station-update"
            >Atualizado em {{ displayDate(s.updated) }}</span
          ><PrecosExibicao :station="s" :common-payment="commonPayment" />
        </div>
        <div class="station-price">
          <strong>{{
            s.price > 0 ? priceMoney(s.price) : "Não informado"
          }}</strong
          ><span>/ L · {{ stationPayment }}</span>
        </div>
      </button>
      <div v-if="!rankedStations.length" class="empty-state">
        <MapPin :size="28" />
        <p>Nenhum posto com preço para estes filtros.</p>
      </div>
      <div class="ranking-foot">
        <ShieldCheck :size="15" /><span>{{
          isDemo
            ? "Preços de exemplo, sem validade comercial."
            : "Confirme os preços no posto antes de abastecer."
        }}</span>
      </div>
    </section>
    <div class="map-column">
      <StationMap
        :demo="isDemo"
        :stations="rankedStations"
        :selected="mapSelected"
        @select="mapSelected = $event"
      />
      <section v-if="stationDetail" class="card map-detail">
        <div>
          <h3>{{ stationDetail.name }}</h3>
          <p>{{ stationDetail.address }} · {{ stationDetail.city }}</p>
          <PrecosExibicao
            :station="stationDetail"
            :common-payment="commonPayment"
          />
          <div class="detail-tags">
            <span
              ><Wind :size="14" />Calibrador:
              {{ stationDetail.air.toLowerCase() }}</span
            ><button class="text-button" @click="openModal('report')">
              Relatar problema
            </button>
          </div>
        </div>
        <button class="primary-button" @click="fillAt(stationDetail)">
          <Fuel :size="17" />Abastecer aqui
        </button>
      </section>
    </div>
  </div>
</template>
