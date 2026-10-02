import { reactive, type Ref } from "vue";
import type { Vehicle } from "../types/domain";
import { api, isDemo, errorMessage } from "../services/api";
import { parseDecimal } from "../utils/domain.mjs";
type Context = {
  vehicles: Ref<Vehicle[]>;
  form: { vehicle: number };
  editingId: Ref<number | null>;
  modalSaving: Ref<boolean>;
  modalError: Ref<string>;
  openModal: (type: "vehicle") => void;
  closeModal: () => void;
  notify: (message: string) => void;
};
export function useVehicleForm(context: Context) {
  const {
    vehicles,
    form,
    editingId,
    modalSaving,
    modalError,
    openModal,
    closeModal,
    notify,
  } = context;
  const vehicleDraft = reactive({
    type: "Moto",
    brand: "",
    model: "",
    year: 2023,
    capacity: "",
    fuel: "Gasolina comum",
    primary: false,
  });
  function newVehicle() {
    editingId.value = null;
    Object.assign(vehicleDraft, {
      type: "Moto",
      brand: "",
      model: "",
      year: 2023,
      capacity: "",
      fuel: "Gasolina comum",
      primary: false,
    });
    openModal("vehicle");
  }
  function editVehicle(v: Vehicle) {
    editingId.value = v.id;
    Object.assign(vehicleDraft, {
      ...v,
      capacity: String(v.capacity).replace(".", ","),
    });
    openModal("vehicle");
  }
  async function saveVehicle() {
    if (modalSaving.value) return;
    const capacity = parseDecimal(vehicleDraft.capacity);
    if (
      !vehicleDraft.brand.trim() ||
      !vehicleDraft.model.trim() ||
      !Number.isFinite(capacity) ||
      capacity <= 0
    ) {
      modalError.value =
        "Preencha marca, modelo e capacidade válida do tanque.";
      return;
    }
    if (
      vehicleDraft.year < 1900 ||
      vehicleDraft.year > new Date().getFullYear() + 1
    ) {
      modalError.value = "Confira o ano do veículo.";
      return;
    }
    const data: Vehicle = {
      id: editingId.value ?? Date.now(),
      type: vehicleDraft.type,
      brand: vehicleDraft.brand.trim(),
      model: vehicleDraft.model.trim(),
      year: Number(vehicleDraft.year),
      capacity,
      fuel: vehicleDraft.fuel,
      primary: vehicleDraft.primary,
    };
    if (!isDemo) {
      modalSaving.value = true;
      try {
        const result = await api(
          editingId.value ? `vehicles/${editingId.value}/` : "vehicles/",
          editingId.value ? "PATCH" : "POST",
          data,
        );
        data.id = result.id;
        data.capacity = Number(result.capacity);
        data.primary = result.primary;
      } catch (e) {
        modalError.value = errorMessage(e);
        return;
      } finally {
        modalSaving.value = false;
      }
    }
    if (data.primary) vehicles.value.forEach((v) => (v.primary = false));
    if (editingId.value) {
      const i = vehicles.value.findIndex((v) => v.id === editingId.value);
      vehicles.value[i] = data;
    } else {
      vehicles.value.push(data);
      form.vehicle = data.id;
    }
    if (!vehicles.value.some((v) => v.primary))
      vehicles.value[0].primary = true;
    closeModal();
    notify(
      isDemo ? "Veículo salvo nesta sessão." : "Veículo salvo na sua conta.",
    );
  }
  return { vehicleDraft, newVehicle, editVehicle, saveVehicle };
}
