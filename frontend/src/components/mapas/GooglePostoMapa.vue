<script setup lang="ts">
import { onMounted, onBeforeUnmount, ref, shallowRef } from "vue";
import {
  hasMapsKey,
  loadGoogleMaps,
  stationFromPlace,
  type StationSelection,
} from "../../services/googleMaps";
const emit = defineEmits<{ select: [station: StationSelection] }>();
const container = ref<HTMLDivElement>();
const query = ref(""),
  error = ref(""),
  busy = ref(false),
  ready = ref(false),
  searched = ref(false),
  selectedId = ref("");
const results = shallowRef<google.maps.places.Place[]>([]);
let map: google.maps.Map | undefined;
let markers: google.maps.marker.AdvancedMarkerElement[] = [];
let disposed = false;
function clearMarkers() {
  for (const marker of markers) {
    google.maps.event.clearInstanceListeners(marker);
    marker.map = null;
  }
  markers = [];
}
async function run(action: () => Promise<void>) {
  if (busy.value) return;
  busy.value = true;
  error.value = "";
  try {
    await action();
  } catch (e) {
    if (!disposed)
      error.value =
        e instanceof Error
          ? e.message
          : "Não foi possível buscar os postos. Tente novamente.";
  } finally {
    if (!disposed) busy.value = false;
  }
}
async function choose(place: google.maps.places.Place) {
  await run(async () => {
    await place.fetchFields({
      fields: [
        "id",
        "displayName",
        "formattedAddress",
        "addressComponents",
        "location",
      ],
    });
    if (disposed) return;
    const station = stationFromPlace(place);
    selectedId.value = place.id;
    map?.panTo(place.location!);
    emit("select", station);
  });
}
async function draw(places: google.maps.places.Place[]) {
  if (disposed || !map) return;
  const { AdvancedMarkerElement } = (await google.maps.importLibrary(
    "marker",
  )) as google.maps.MarkerLibrary;
  if (disposed) return;
  clearMarkers();
  results.value = places;
  searched.value = true;
  for (const place of places) {
    if (!place.location) continue;
    const marker = new AdvancedMarkerElement({
      map,
      position: place.location,
      title: place.displayName || "Selecionar posto",
    });
    marker.addListener("click", () => choose(place));
    markers.push(marker);
  }
}
async function nearby() {
  await run(async () => {
    if (!map) return;
    const { Place, SearchNearbyRankPreference } =
      (await google.maps.importLibrary("places")) as google.maps.PlacesLibrary;
    const { spherical } = (await google.maps.importLibrary(
      "geometry",
    )) as google.maps.GeometryLibrary;
    const bounds = map.getBounds();
    const radius = bounds
      ? Math.min(
          50000,
          Math.max(
            100,
            spherical.computeDistanceBetween(
              bounds.getNorthEast(),
              bounds.getSouthWest(),
            ) / 2,
          ),
        )
      : 5000;
    const { places } = await Place.searchNearby({
      fields: ["id", "displayName", "formattedAddress", "location"],
      locationRestriction: { center: map.getCenter()!, radius },
      includedTypes: ["gas_station"],
      maxResultCount: 20,
      rankPreference: SearchNearbyRankPreference.DISTANCE,
    });
    await draw(places);
  });
}
async function searchRegion() {
  if (!query.value.trim()) return;
  await run(async () => {
    const { Place } = (await google.maps.importLibrary(
      "places",
    )) as google.maps.PlacesLibrary;
    const { places } = await Place.searchByText({
      textQuery: query.value.trim(),
      fields: ["location", "viewport"],
      region: "br",
      language: "pt-BR",
      maxResultCount: 1,
    });
    if (disposed) return;
    const place = places[0];
    if (!place?.location)
      throw new Error("Região não encontrada. Tente incluir cidade e estado.");
    clearMarkers();
    results.value = [];
    searched.value = false;
    if (place.viewport) map?.fitBounds(place.viewport);
    else {
      map?.setCenter(place.location);
      map?.setZoom(14);
    }
  });
}
async function locate() {
  await run(async () => {
    if (!navigator.geolocation)
      throw new Error("Localização indisponível. Busque uma região pelo nome.");
    const position = await new Promise<GeolocationPosition>((resolve, reject) =>
      navigator.geolocation.getCurrentPosition(
        resolve,
        () =>
          reject(
            new Error(
              "Não foi possível acessar sua localização. Busque a cidade ou o bairro.",
            ),
          ),
        { timeout: 10000 },
      ),
    );
    if (disposed) return;
    map?.setCenter({
      lat: position.coords.latitude,
      lng: position.coords.longitude,
    });
    map?.setZoom(14);
  });
}
onMounted(async () => {
  if (!hasMapsKey) return;
  await run(async () => {
    await loadGoogleMaps();
    const { Map } = (await google.maps.importLibrary(
      "maps",
    )) as google.maps.MapsLibrary;
    if (disposed || !container.value) return;
    map = new Map(container.value, {
      center: { lat: -2.509, lng: -44.276 },
      zoom: 13,
      mapId: import.meta.env.VITE_GOOGLE_MAPS_MAP_ID || "DEMO_MAP_ID",
      mapTypeControl: false,
      streetViewControl: false,
      fullscreenControl: false,
    });
    ready.value = true;
  });
});
onBeforeUnmount(() => {
  disposed = true;
  clearMarkers();
  if (map) google.maps.event.clearInstanceListeners(map);
  map = undefined;
});
</script>
<template>
  <section
    class="google-station-picker"
    aria-label="Encontrar posto no Google Maps"
  >
    <template v-if="hasMapsKey">
      <label class="field"
        ><span>Cidade, bairro ou endereço</span
        ><input
          v-model="query"
          placeholder="Ex.: Cohama, São Luís, MA"
          @keydown.enter.prevent="searchRegion"
      /></label>
      <div class="map-search-actions">
        <button
          type="button"
          class="secondary-button"
          :disabled="!ready || busy || !query.trim()"
          @click="searchRegion"
        >
          Ir para região</button
        ><button
          type="button"
          class="secondary-button"
          :disabled="!ready || busy"
          @click="locate"
        >
          Minha localização
        </button>
      </div>
      <div
        ref="container"
        class="google-picker-map"
        aria-label="Mova o mapa para a região desejada"
      ></div>
      <button
        type="button"
        class="primary-button wide"
        :disabled="!ready || busy"
        @click="nearby"
      >
        {{ busy ? "Carregando…" : "Buscar postos nesta área" }}
      </button>
      <p>
        Mova o mapa, busque os postos e selecione um resultado para preencher o
        cadastro.
      </p>
      <div class="google-results">
        <button
          v-for="place in results"
          :key="place.id"
          type="button"
          :class="{ selected: selectedId === place.id }"
          :disabled="busy"
          @click="choose(place)"
        >
          <strong>{{ place.displayName }}</strong
          ><span>{{ place.formattedAddress }}</span>
        </button>
      </div>
      <p v-if="searched && !results.length">
        Nenhum posto encontrado. Tente outra região ou preencha manualmente.
      </p>
      <p v-if="selectedId" role="status">
        Posto selecionado. Confira os dados abaixo antes de salvar.
      </p>
      <p v-if="error" class="form-error" role="alert">
        {{ error }} O cadastro manual continua disponível.
      </p>
    </template>
    <p v-else>
      A busca no mapa ainda não está configurada. Preencha o cadastro
      manualmente.
    </p>
  </section>
</template>
