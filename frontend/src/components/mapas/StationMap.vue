<script setup lang="ts">
import { onMounted, onBeforeUnmount, watch, ref } from "vue";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import type { Station } from "../../types/domain";
import { hasMapsKey, loadGoogleMaps } from "../../services/googleMaps";
const props = defineProps<{
  stations: Station[];
  selected: number;
  demo?: boolean;
}>();
const emit = defineEmits<{ select: [id: number] }>();
const container = ref<HTMLElement | null>(null),
  failed = ref(false);
let map: L.Map | undefined, layer: L.LayerGroup | undefined;
let googleMap: google.maps.Map | undefined;
let markerClass: typeof google.maps.marker.AdvancedMarkerElement | undefined;
let googleMarkers: google.maps.marker.AdvancedMarkerElement[] = [];
let disposed = false;
const label = (station: Station) =>
  station.price > 0
    ? `R$ ${station.price.toFixed(3).replace(".", ",")}`
    : "Sem preço";
function draw() {
  if (disposed) return;
  if (googleMap && markerClass) {
    for (const marker of googleMarkers) {
      google.maps.event.clearInstanceListeners(marker);
      marker.map = null;
    }
    googleMarkers = [];
    for (const station of props.stations) {
      const button = document.createElement("button");
      button.type = "button";
      button.className = `price-pin ${station.id === props.selected ? "selected" : ""}`;
      button.textContent = label(station);
      button.setAttribute(
        "aria-label",
        `Selecionar ${station.name}: ${label(station)}`,
      );
      button.addEventListener("click", () => emit("select", station.id));
      const marker = new markerClass({
        map: googleMap,
        position: { lat: station.lat, lng: station.lng },
        title: station.name,
        content: button,
      });
      googleMarkers.push(marker);
    }
  } else if (map && layer) {
    layer.clearLayers();
    // Google-linked stations are never plotted on the OpenStreetMap fallback.
    for (const station of props.stations.filter((s) => !s.external_id)) {
      const button = document.createElement("button");
      button.type = "button";
      button.textContent = label(station);
      button.className = `price-pin ${station.id === props.selected ? "selected" : ""}`;
      button.setAttribute(
        "aria-label",
        `Selecionar ${station.name}: ${label(station)}`,
      );
      const icon = L.divIcon({
        className: "price-pin-wrapper",
        html: button,
        iconSize: [98, 36],
        iconAnchor: [49, 36],
      });
      L.marker([station.lat, station.lng], { icon })
        .on("click", () => emit("select", station.id))
        .addTo(layer);
    }
  }
}
function panToSelected() {
  const station = props.stations.find((s) => s.id === props.selected);
  if (!station) return;
  googleMap?.panTo({ lat: station.lat, lng: station.lng });
  if (!station.external_id) map?.panTo([station.lat, station.lng]);
}
onMounted(async () => {
  if (!container.value) return;
  if (hasMapsKey && !props.demo) {
    try {
      await loadGoogleMaps();
      const [{ Map }, { AdvancedMarkerElement }] = (await Promise.all([
        google.maps.importLibrary("maps"),
        google.maps.importLibrary("marker"),
      ])) as [google.maps.MapsLibrary, google.maps.MarkerLibrary];
      if (disposed || !container.value) return;
      markerClass = AdvancedMarkerElement;
      googleMap = new Map(container.value, {
        center: { lat: -2.509, lng: -44.276 },
        zoom: 13,
        mapId: import.meta.env.VITE_GOOGLE_MAPS_MAP_ID || "DEMO_MAP_ID",
        streetViewControl: false,
        mapTypeControl: false,
      });
      draw();
      panToSelected();
    } catch {
      if (!disposed) failed.value = true;
    }
  } else {
    map = L.map(container.value, { zoomControl: false }).setView(
      [-2.509, -44.276],
      13,
    );
    L.control.zoom({ position: "bottomright" }).addTo(map);
    L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
      attribution:
        '© <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener noreferrer">OpenStreetMap</a>',
      maxZoom: 19,
    })
      .on("tileerror", () => (failed.value = true))
      .on("tileload", () => (failed.value = false))
      .addTo(map);
    layer = L.layerGroup().addTo(map);
    draw();
    panToSelected();
  }
});
watch(
  () => [props.stations, props.selected],
  () => {
    draw();
    panToSelected();
  },
  { deep: true },
);
onBeforeUnmount(() => {
  disposed = true;
  map?.remove();
  for (const marker of googleMarkers) {
    google.maps.event.clearInstanceListeners(marker);
    marker.map = null;
  }
  if (googleMap) google.maps.event.clearInstanceListeners(googleMap);
});
</script>
<template>
  <div class="map-shell">
    <div
      ref="container"
      class="station-map"
      :aria-label="
        demo ? 'Mapa demonstrativo de postos' : 'Mapa dos postos cadastrados'
      "
    ></div>
    <div class="map-legend">
      {{
        demo
          ? "Postos e preços fictícios · demonstração"
          : "Preços compartilhados pela comunidade"
      }}
    </div>
    <p v-if="failed" class="map-failed">
      O mapa não carregou. Você pode continuar pela lista de postos.
    </p>
  </div>
</template>
