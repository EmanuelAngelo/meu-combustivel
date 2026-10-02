import { reactive, ref, type Ref } from "vue";
import type { Station } from "../types/domain";
import { api, isDemo, errorMessage } from "../services/api";
import { normalizedName } from "../utils/domain.mjs";
type Context = {
  stations: Ref<Station[]>;
  form: { station: number; price: string };
  modalSaving: Ref<boolean>;
  modalError: Ref<string>;
  openModal: (type: "station") => void;
  closeModal: () => void;
  notify: (message: string) => void;
  dateInput: () => string;
  stationChanged: () => void;
  mapStation: (s: any) => Station;
};
export function useStationForm(context: Context) {
  const {
    stations,
    form,
    modalSaving,
    modalError,
    openModal,
    closeModal,
    notify,
    dateInput,
    stationChanged,
    mapStation,
  } = context;
  const stationDraft = reactive({
    name: "",
    address: "",
    city: "São Luís",
    state: "MA",
    lat: "",
    lng: "",
    air: "Não informado",
    external_id: "",
  });
  function newStation() {
    Object.assign(stationDraft, {
      name: "",
      address: "",
      city: "São Luís",
      state: "MA",
      lat: "",
      lng: "",
      air: "Não informado",
      external_id: "",
    });
    openModal("station");
  }
  async function saveStation() {
    if (modalSaving.value) return;
    if (
      !stationDraft.name.trim() ||
      !stationDraft.address.trim() ||
      !stationDraft.city.trim() ||
      !stationDraft.state.trim()
    ) {
      modalError.value = "Preencha nome, endereço, cidade e estado.";
      return;
    }
    const duplicate = stations.value.find(
      (s) =>
        normalizedName(s.name) === normalizedName(stationDraft.name) &&
        normalizedName(s.city) === normalizedName(stationDraft.city) &&
        normalizedName(s.address) === normalizedName(stationDraft.address),
    );
    if (duplicate) {
      form.station = duplicate.id;
      closeModal();
      stationChanged();
      notify("Este posto já existe. Selecionamos o cadastro disponível.");
      return;
    }
    const lat = Number(stationDraft.lat.replace(",", ".")),
      lng = Number(stationDraft.lng.replace(",", "."));
    if (
      !stationDraft.lat ||
      !stationDraft.lng ||
      !Number.isFinite(lat) ||
      !Number.isFinite(lng) ||
      Math.abs(lat) > 90 ||
      Math.abs(lng) > 180
    ) {
      modalError.value = "Informe coordenadas válidas ou use sua localização.";
      return;
    }
    const s: Station = {
      external_id: stationDraft.external_id || null,
      id: Date.now(),
      name: stationDraft.name.trim(),
      address: stationDraft.address.trim(),
      city: stationDraft.city.trim(),
      state: stationDraft.state.toUpperCase(),
      lat,
      lng,
      price: 0,
      air: stationDraft.air as Station["air"],
      updated: dateInput(),
    };
    if (!isDemo) {
      modalSaving.value = true;
      try {
        const result = await api("stations/", "POST", { ...s, country: "BR" });
        Object.assign(s, mapStation(result));
      } catch (e) {
        modalError.value = errorMessage(e);
        return;
      } finally {
        modalSaving.value = false;
      }
    }
    if (!stations.value.some((item) => item.id === s.id))
      stations.value.push(s);
    form.station = s.id;
    form.price = "";
    closeModal();
    notify(
      isDemo
        ? "Posto adicionado apenas nesta demonstração."
        : "Posto cadastrado. Você já pode registrar o abastecimento.",
    );
  }
  const locating = ref(false);
  function locate() {
    modalError.value = "";
    if (!navigator.geolocation) {
      modalError.value =
        "Localização indisponível. Preencha as coordenadas manualmente.";
      return;
    }
    locating.value = true;
    navigator.geolocation.getCurrentPosition(
      (p) => {
        stationDraft.lat = p.coords.latitude.toFixed(6);
        stationDraft.lng = p.coords.longitude.toFixed(6);
        locating.value = false;
      },
      () => {
        modalError.value =
          "Não foi possível acessar a localização. Você pode preencher os campos manualmente.";
        locating.value = false;
      },
      { enableHighAccuracy: true, timeout: 10000 },
    );
  }
  return { stationDraft, newStation, saveStation, locating, locate };
}
