import {
  money,
  priceMoney,
  num,
  displayDate,
  dateInput,
} from "../utils/format";
import { useStationForm } from "./useStationForm";
import { useVehicleForm } from "./useVehicleForm";
import {
  computed,
  reactive,
  ref,
  onMounted,
  onBeforeUnmount,
  nextTick,
  watch,
} from "vue";
import {
  Droplet,
  Fuel,
  LayoutDashboard,
  History,
  MapPin,
  Car,
  Plus,
  ChevronRight,
  ChevronDown,
  ArrowUpRight,
  Check,
  CheckCheck,
  ShieldCheck,
  Info,
  Wallet,
  CalendarDays,
  Gauge,
  Bike,
  Search,
  X,
  SlidersHorizontal,
  Navigation,
  Wind,
  CheckCircle2,
  AlertTriangle,
  ReceiptText,
  Trash2,
  Star,
  Menu,
  Globe,
  Download,
  RotateCcw,
} from "lucide-vue-next";
import {
  type Account,
  isDemo,
  currentUser,
  api,
  restoreSession,
  signOut,
  errorMessage,
} from "../services/api";
import { online, installPrompt, installApp } from "../services/pwa";
import {
  initialVehicles,
  initialStations,
  initialFills,
  type Vehicle,
  type Station,
  type Fill,
} from "../data";
import { checkFuel, parseDecimal, normalizedName } from "../utils/domain.mjs";
export function useApplication() {
  type Page = "home" | "fill" | "history" | "stations" | "vehicles";
  const nav = [
    { id: "home" as Page, label: "Visão geral", icon: LayoutDashboard },
    { id: "fill" as Page, label: "Abastecer", icon: Fuel },
    { id: "history" as Page, label: "Histórico", icon: History },
    { id: "stations" as Page, label: "Explorar postos", icon: MapPin },
    { id: "vehicles" as Page, label: "Meus veículos", icon: Car },
  ];
  const page = ref<Page>("fill"),
    mobileMenu = ref(false);
  const vehicles = ref<Vehicle[]>(
      isDemo ? structuredClone(initialVehicles) : [],
    ),
    stations = ref<Station[]>(isDemo ? structuredClone(initialStations) : []),
    fills = ref<Fill[]>(isDemo ? structuredClone(initialFills) : []);
  const booting = ref(!isDemo),
    bootError = ref(""),
    saving = ref(false),
    modalSaving = ref(false);
  const requestKey = { signature: "", id: "" };
  const form = reactive({
    vehicle: 1,
    station: 1,
    date: dateInput(),
    fuel: "Gasolina comum",
    price: "6,20",
    total: "23,04",
    liters: "3,716",
    km: "",
    full: false,
    payment: "Pix",
    common_payment: "Pix",
    common_price: "",
    credit_price: "",
    note: "",
    share: true,
    ack: false,
  });
  if (!isDemo)
    Object.assign(form, {
      vehicle: 0,
      station: 0,
      price: "",
      total: "",
      liters: "",
    });
  watch(
    () => [form.station, form.fuel, form.date],
    () => {
      form.common_price = "";
      form.credit_price = "";
    },
    { flush: "sync" },
  );
  const selectedVehicle = computed(() =>
    vehicles.value.find((v) => v.id === Number(form.vehicle))!,
  );
  const selectedStation = computed(() =>
    stations.value.find((s) => s.id === Number(form.station)),
  );
  const calculation = computed(() =>
    checkFuel(form.price, form.total, form.liters),
  );
  const overCapacity = computed(
    () =>
      parseDecimal(form.liters) > (selectedVehicle.value?.capacity ?? Infinity),
  );
  const needsCheck = computed(
    () =>
      Boolean(calculation.value && !calculation.value.consistent) ||
      overCapacity.value,
  );
  const vehicleName = (id: number) => {
    const v = vehicles.value.find((v) => v.id === id);
    return v ? `${v.brand} ${v.model}` : "Veículo";
  };
  const stationName = (id: number) =>
    stations.value.find((s) => s.id === id)?.name ?? "Posto";
  const sortedFills = computed(() =>
    [...fills.value].sort(
      (a, b) => b.date.localeCompare(a.date) || b.id - a.id,
    ),
  );
  const latest = computed(() =>
    sortedFills.value.find((f) => f.vehicle === Number(form.vehicle)),
  );
  const comparison = computed(() => {
    if (!latest.value || !calculation.value) return null;
    return (
      parseDecimal(form.total) -
      parseDecimal(form.liters) * (latest.value.total / latest.value.liters)
    );
  });
  const totalSpend = computed(() =>
      fills.value.reduce((a, f) => a + f.total, 0),
    ),
    totalLiters = computed(() => fills.value.reduce((a, f) => a + f.liters, 0));
  const average = computed(() =>
    totalLiters.value ? totalSpend.value / totalLiters.value : 0,
  );
  const toast = ref(""),
    error = ref("");
  let toastTimer: ReturnType<typeof setTimeout> | undefined;
  function notify(s: string) {
    toast.value = s;
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => (toast.value = ""), 6000);
  }
  function go(p: Page) {
    page.value = p;
    mobileMenu.value = false;
    window.scrollTo({ top: 0, behavior: "smooth" });
  }
  function stationChanged() {
    if (
      selectedStation.value &&
      form.fuel === stationFuel.value &&
      form.payment === stationPayment.value &&
      selectedStation.value.price > 0
    )
      form.price = selectedStation.value.price.toFixed(3).replace(".", ",");
    else form.price = "";
    form.ack = false;
  }
  function fuelChanged() {
    form.price = "";
    form.ack = false;
  }
  async function saveFill() {
    if (saving.value) return;
    error.value = "";
    const c = calculation.value;
    if (!c) {
      error.value = "Informe preço, total e litros maiores que zero.";
      return;
    }
    if (!selectedStation.value || !selectedVehicle.value) {
      error.value = "Selecione o veículo e o posto.";
      return;
    }
    if (!form.date || form.date > dateInput()) {
      error.value = "Escolha a data de hoje ou uma data anterior.";
      return;
    }
    if (needsCheck.value && !form.ack) {
      error.value = "Confira os valores e confirme a revisão antes de salvar.";
      return;
    }
    for (const [value, payment] of [
      [form.common_price, form.common_payment],
      [form.credit_price, "Crédito"],
    ]) {
      if (!value.trim()) continue;
      const price = parseDecimal(value);
      if (!Number.isFinite(price) || price <= 0) {
        error.value =
          "Informe preços de comparação positivos ou deixe em branco.";
        return;
      }
      if (
        form.payment === payment &&
        Math.abs(price - parseDecimal(form.price)) > 0.0001
      ) {
        error.value =
          "Para o mesmo pagamento, use o preço por litro informado na bomba.";
        return;
      }
    }
    const km = form.km.trim() ? parseDecimal(form.km) : null;
    if (
      km !== null &&
      (!Number.isFinite(km) || !Number.isInteger(km) || km < 0)
    ) {
      error.value = "Confira a quilometragem.";
      return;
    }
    const record: Fill = {
      id: Date.now(),
      vehicle: Number(form.vehicle),
      station: Number(form.station),
      date: form.date,
      fuel: form.fuel,
      price: parseDecimal(form.price),
      total: parseDecimal(form.total),
      liters: parseDecimal(form.liters),
      km,
      full: form.full,
      payment: form.payment,
      note: form.note.trim(),
    };
    if (!isDemo) {
      saving.value = true;
      try {
        const payload = {
          ...record,
          id: undefined,
          price: form.price.replace(",", "."),
          total: form.total.replace(",", "."),
          liters: form.liters.replace(",", "."),
          share: form.share,
          common_payment: form.common_payment,
          common_price: form.common_price.trim()
            ? form.common_price.replace(",", ".")
            : null,
          credit_price: form.credit_price.trim()
            ? form.credit_price.replace(",", ".")
            : null,
          acknowledged: form.ack,
        };
        const signature = JSON.stringify(payload);
        if (signature !== requestKey.signature) {
          requestKey.signature = signature;
          requestKey.id = crypto.randomUUID();
        }
        const result = await api("refuelings/", "POST", {
          ...payload,
          client_id: requestKey.id,
        });
        record.id = result.id;
        requestKey.signature = "";
      } catch (e) {
        error.value = errorMessage(e);
        return;
      } finally {
        saving.value = false;
      }
    }
    if (!fills.value.some((f) => f.id === record.id))
      fills.value.unshift(record);
    if (
      isDemo &&
      form.share &&
      form.fuel === "Gasolina comum" &&
      form.payment === "Pix" &&
      form.date >= selectedStation.value.updated
    ) {
      selectedStation.value.price = record.price;
      selectedStation.value.updated = form.date;
    }
    form.common_price = "";
    form.credit_price = "";
    form.total = "";
    form.liters = "";
    form.km = "";
    form.note = "";
    form.ack = false;
    notify(
      isDemo
        ? "Abastecimento salvo nesta sessão de demonstração."
        : "Abastecimento salvo na sua conta.",
    );
    go("history");
    if (!isDemo) refreshStations().catch(() => {});
  }
  function resetForm() {
    Object.assign(form, {
      vehicle:
        vehicles.value.find((v) => v.primary)?.id ?? vehicles.value[0]?.id ?? 0,
      station: stations.value[0]?.id ?? 0,
      date: dateInput(),
      fuel: "Gasolina comum",
      price: isDemo ? "6,20" : "",
      total: "",
      liters: "",
      km: "",
      full: false,
      payment: "Pix",
      common_payment: "Pix",
      common_price: "",
      credit_price: "",
      note: "",
      share: true,
      ack: false,
    });
    error.value = "";
  }
  const historyQuery = ref(""),
    historyVehicle = ref("all"),
    historyMonth = ref("all");
  const historyMonths = computed(() =>
    [...new Set(fills.value.map((f) => f.date.slice(0, 7)))].sort().reverse(),
  );
  const filteredFills = computed(() =>
    sortedFills.value.filter(
      (f) =>
        (historyVehicle.value === "all" ||
          f.vehicle === Number(historyVehicle.value)) &&
        (historyMonth.value === "all" ||
          f.date.startsWith(historyMonth.value)) &&
        normalizedName(
          stationName(f.station) + " " + vehicleName(f.vehicle) + " " + f.fuel,
        ).includes(normalizedName(historyQuery.value)),
    ),
  );
  const stationFuel = ref("Gasolina comum"),
    stationPayment = ref("Pix"),
    commonPayment = ref("Pix"),
    stationLoading = ref(false),
    stationError = ref("");
  const stationQuery = ref(""),
    region = ref("São Luís"),
    sort = ref("cheap"),
    onlyAir = ref(false),
    mapSelected = ref(1);
  const rankedStations = computed(() =>
    stations.value
      .filter(
        (s) =>
          normalizedName(s.name + " " + s.address).includes(
            normalizedName(stationQuery.value),
          ) &&
          (region.value === "Brasil" ||
            (region.value === "Maranhão"
              ? s.state.toUpperCase() === "MA"
              : normalizedName(s.city) === "sao luis")) &&
          (!onlyAir.value || s.air === "Gratuito"),
      )
      .sort((a, b) =>
        a.price <= 0
          ? 1
          : b.price <= 0
            ? -1
            : sort.value === "cheap"
              ? a.price - b.price
              : b.price - a.price,
      ),
  );
  const stationDetail = computed(() =>
    stations.value.find((s) => s.id === mapSelected.value),
  );
  function fillAt(s: Station) {
    form.station = s.id;
    form.fuel = stationFuel.value;
    form.payment = stationPayment.value;
    form.price = s.price > 0 ? s.price.toFixed(3).replace(".", ",") : "";
    form.ack = false;
    go("fill");
  }
  const modalOpen = ref(false);
  const modal = ref<HTMLDialogElement | null>(null),
    modalType = ref<"vehicle" | "station" | "fillDetail" | "report">("vehicle"),
    modalError = ref(""),
    editingId = ref<number | null>(null),
    detailFill = ref<Fill | null>(null);
  const { vehicleDraft, newVehicle, editVehicle, saveVehicle } = useVehicleForm(
    {
      vehicles,
      form,
      editingId,
      modalSaving,
      modalError,
      openModal,
      closeModal,
      notify,
    },
  );
  const { stationDraft, newStation, saveStation, locating, locate } =
    useStationForm({
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
    });
  const reportDraft = reactive({
      type: "Falhas após abastecer",
      description: "",
      date: dateInput(),
    }),
    reports = ref<{ station: number; type: string }[]>([]);
  function openModal(type: typeof modalType.value) {
    modalType.value = type;
    modalOpen.value = true;
    modalError.value = "";
    nextTick(() => modal.value?.showModal());
  }
  function closeModal() {
    modal.value?.close();
    modalOpen.value = false;
  }
  function openFill(f: Fill) {
    detailFill.value = f;
    openModal("fillDetail");
  }
  async function submitReport() {
    if (modalSaving.value) return;
    if (reportDraft.description.trim().length < 15) {
      modalError.value = "Descreva o ocorrido em pelo menos 15 caracteres.";
      return;
    }
    if (!isDemo) {
      modalSaving.value = true;
      try {
        await api("reports/", "POST", {
          station: mapSelected.value,
          ...reportDraft,
        });
      } catch (e) {
        modalError.value = errorMessage(e);
        return;
      } finally {
        modalSaving.value = false;
      }
    }
    reports.value.push({ station: mapSelected.value, type: reportDraft.type });
    closeModal();
    reportDraft.description = "";
    notify(
      isDemo
        ? "Relato simulado: aguardando moderação. Nenhuma denúncia foi publicada."
        : "Relato enviado para moderação. Não foi publicado automaticamente.",
    );
  }
  function exportHistory() {
    const csv =
      "\uFEFFData;Veículo;Posto;Combustível;Preço por litro;Total;Litros\n" +
      filteredFills.value
        .map((f) =>
          [
            f.date,
            vehicleName(f.vehicle),
            stationName(f.station),
            f.fuel,
            f.price.toFixed(3).replace(".", ","),
            f.total.toFixed(2).replace(".", ","),
            f.liters.toFixed(3).replace(".", ","),
          ]
            .map(
              (x) =>
                '"' +
                (/^[=+@\-\t\r]/.test(String(x)) ? "'" : "") +
                String(x).replace(/"/g, '""') +
                '"',
            )
            .join(";"),
        )
        .join("\n");
    const u = URL.createObjectURL(
      new Blob([csv], { type: "text/csv;charset=utf-8;" }),
    );
    const a = document.createElement("a");
    a.href = u;
    a.download = isDemo
      ? "meu-combustivel-demonstracao.csv"
      : "meu-combustivel-historico.csv";
    a.click();
    URL.revokeObjectURL(u);
  }
  const pricedStations = computed(() =>
    rankedStations.value.filter((s) => s.price > 0),
  );
  const cheapest = computed(
    () =>
      [...stations.value]
        .filter((s) => s.price > 0)
        .sort((a, b) => a.price - b.price)[0],
  );
  function mapStation(s: any): Station {
    return {
      ...s,
      lat: Number(s.lat),
      lng: Number(s.lng),
      price: Number(s.price ?? 0),
      common_price: s.common_price == null ? null : Number(s.common_price),
      credit_price: s.credit_price == null ? null : Number(s.credit_price),
      updated: s.updated ?? "",
    };
  }
  let stationRequest = 0;
  async function refreshStations() {
    const request = ++stationRequest;
    stationLoading.value = true;
    stationError.value = "";
    const query = new URLSearchParams({
      fuel: stationFuel.value,
      payment: stationPayment.value,
      common_payment: commonPayment.value,
    });
    try {
      const data = (await api<any[]>("stations/?" + query)).map(mapStation);
      if (request === stationRequest) stations.value = data;
    } catch (e) {
      if (request === stationRequest) {
        stations.value = [];
        stationError.value = errorMessage(e);
      }
      throw e;
    } finally {
      if (request === stationRequest) stationLoading.value = false;
    }
  }
  watch([stationFuel, stationPayment, commonPayment], () => {
    if (!isDemo) refreshStations().catch(() => {});
  });
  async function loadAccount() {
    const [vs, ss, fs] = await Promise.all([
      api<any[]>("vehicles/"),
      api<any[]>("stations/"),
      api<any[]>("refuelings/"),
    ]);
    vehicles.value = vs.map((v) => ({ ...v, capacity: Number(v.capacity) }));
    stations.value = ss.map(mapStation);
    fills.value = fs.map((f) => ({
      ...f,
      price: Number(f.price),
      total: Number(f.total),
      liters: Number(f.liters),
    }));
    resetForm();
    mapSelected.value = stations.value[0]?.id ?? 0;
    if (!vehicles.value.length) page.value = "vehicles";
  }
  async function startAccount() {
    booting.value = true;
    bootError.value = "";
    try {
      await restoreSession();
      if (currentUser.value) await loadAccount();
    } catch (e) {
      bootError.value = errorMessage(e);
    } finally {
      booting.value = false;
    }
  }
  async function enterAccount(account: Account) {
    currentUser.value = account;
    booting.value = true;
    bootError.value = "";
    try {
      await loadAccount();
    } catch (e) {
      bootError.value = errorMessage(e);
    } finally {
      booting.value = false;
    }
  }
  function clearPrivateState() {
    vehicles.value = [];
    fills.value = [];
    stations.value = [];
    reports.value = [];
    detailFill.value = null;
    closeModal();
    resetForm();
    Object.assign(vehicleDraft, { brand: "", model: "", capacity: "" });
    reportDraft.description = "";
    requestKey.signature = "";
    requestKey.id = "";
    page.value = "fill";
  }
  async function logoutAccount() {
    try {
      await signOut();
      clearPrivateState();
    } catch (e) {
      notify(errorMessage(e));
    }
  }
  watch(rankedStations, (list) => {
    if (!list.some((s) => s.id === mapSelected.value))
      mapSelected.value = list[0]?.id ?? 0;
  });
  onMounted(() => {
    if (!isDemo) {
      startAccount();
      window.addEventListener("session-expired", clearPrivateState);
    }
  });
  onBeforeUnmount(() =>
    window.removeEventListener("session-expired", clearPrivateState),
  );
  const webmcpLifecycle = new AbortController();
  onMounted(() => {
    const context = (document as any).modelContext;
    if (!context?.registerTool) return;
    Promise.resolve(
      context.registerTool(
        {
          name: "conferir_abastecimento",
          title: "Conferir abastecimento",
          description:
            "Calcula a consistência entre preço por litro, total e litros. Não salva dados.",
          inputSchema: {
            type: "object",
            properties: {
              preco: { type: "number", exclusiveMinimum: 0 },
              total: { type: "number", exclusiveMinimum: 0 },
              litros: { type: "number", exclusiveMinimum: 0 },
            },
            required: ["preco", "total", "litros"],
            additionalProperties: false,
          },
          annotations: { readOnlyHint: true },
          execute(input: any) {
            if (
              !input ||
              typeof input.preco !== "number" ||
              typeof input.total !== "number" ||
              typeof input.litros !== "number"
            )
              throw new Error("Valores numéricos são obrigatórios.");
            const r = checkFuel(input.preco, input.total, input.litros);
            if (!r)
              throw new Error("Os valores devem ser positivos e finitos.");
            return r;
          },
        },
        { signal: webmcpLifecycle.signal },
      ),
    ).catch(() => {});
  });
  onBeforeUnmount(() => {
    webmcpLifecycle.abort();
    clearTimeout(toastTimer);
  });
  return {
    priceMoney,
    modalOpen,
    isDemo,
    currentUser,
    api,
    restoreSession,
    signOut,
    errorMessage,
    online,
    installPrompt,
    installApp,
    initialVehicles,
    initialStations,
    initialFills,
    checkFuel,
    parseDecimal,
    normalizedName,
    nav,
    page,
    mobileMenu,
    vehicles,
    stations,
    fills,
    booting,
    bootError,
    saving,
    modalSaving,
    requestKey,
    dateInput,
    form,
    selectedVehicle,
    selectedStation,
    calculation,
    overCapacity,
    needsCheck,
    money,
    num,
    displayDate,
    vehicleName,
    stationName,
    sortedFills,
    latest,
    comparison,
    totalSpend,
    totalLiters,
    average,
    toast,
    error,
    toastTimer,
    notify,
    go,
    stationChanged,
    fuelChanged,
    saveFill,
    resetForm,
    historyQuery,
    historyVehicle,
    historyMonth,
    historyMonths,
    filteredFills,
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
    rankedStations,
    stationDetail,
    fillAt,
    modal,
    modalType,
    modalError,
    editingId,
    detailFill,
    vehicleDraft,
    stationDraft,
    reportDraft,
    reports,
    openModal,
    closeModal,
    newVehicle,
    editVehicle,
    saveVehicle,
    newStation,
    saveStation,
    locating,
    locate,
    openFill,
    submitReport,
    exportHistory,
    pricedStations,
    cheapest,
    mapStation,
    stationRequest,
    refreshStations,
    loadAccount,
    startAccount,
    enterAccount,
    clearPrivateState,
    logoutAccount,
    webmcpLifecycle,
  };
}
