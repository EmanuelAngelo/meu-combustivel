<script setup lang="ts">
import {onMounted,onBeforeUnmount,watch,ref} from 'vue'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import type {Station} from './data'
const props=defineProps<{stations:Station[],selected:number,demo?:boolean}>()
const emit=defineEmits<{select:[id:number]}>()
const container=ref<HTMLElement|null>(null),failed=ref(false)
let map:L.Map|undefined,layer:L.LayerGroup|undefined
function draw(){if(!map||!layer)return;layer.clearLayers();for(const s of props.stations){const icon=L.divIcon({className:'price-pin-wrapper',html:`<button type="button" aria-label="Selecionar posto a R$ ${s.price.toFixed(2)}" class="price-pin ${s.id===props.selected?'selected':''}">R$ ${s.price.toFixed(2).replace('.',',')}</button>`,iconSize:[86,36],iconAnchor:[43,36]});L.marker([s.lat,s.lng],{icon}).on('click',()=>emit('select',s.id)).addTo(layer)}}
onMounted(()=>{if(!container.value)return;map=L.map(container.value,{zoomControl:false}).setView([-2.509,-44.276],13);L.control.zoom({position:'bottomright'}).addTo(map);L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png',{attribution:'© <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener noreferrer">OpenStreetMap</a>',maxZoom:19}).on('tileerror',()=>failed.value=true).on('tileload',()=>failed.value=false).addTo(map);layer=L.layerGroup().addTo(map);draw()})
watch(()=>[props.stations,props.selected],()=>{draw();const s=props.stations.find(s=>s.id===props.selected);if(s)map?.panTo([s.lat,s.lng])},{deep:true})
onBeforeUnmount(()=>map?.remove())
</script>
<template><div class="map-shell"><div ref="container" class="station-map" :aria-label="demo?'Mapa demonstrativo de postos':'Mapa dos postos cadastrados'"></div><div class="map-legend">{{demo?'Postos e preços fictícios · demonstração':'Postos cadastrados pela comunidade'}}</div><p v-if="failed" class="map-failed">O mapa não carregou. Você pode continuar pela lista de postos.</p></div></template>
