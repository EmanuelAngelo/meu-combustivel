// Loaded only when the user opens the station registration map.
let loading: Promise<void> | undefined;
export const hasMapsKey = Boolean(
  import.meta.env.VITE_GOOGLE_MAPS_API_KEY?.trim(),
);
export function loadGoogleMaps(): Promise<void> {
  if (
    typeof google !== "undefined" &&
    typeof google.maps?.importLibrary === "function"
  )
    return Promise.resolve();
  if (loading) return loading;
  if (!hasMapsKey)
    return Promise.reject(
      new Error(
        "Busca no mapa indisponível. Você pode cadastrar o posto manualmente.",
      ),
    );
  loading = new Promise<void>((resolve, reject) => {
    const script = document.createElement("script");
    const callback = "__meuCombustivelMapsReady";
    const globals = window as unknown as Record<string, unknown>;
    const timeout = window.setTimeout(() => fail(), 20000);
    const cleanup = () => {
      window.clearTimeout(timeout);
      delete globals[callback];
    };
    const fail = () => {
      cleanup();
      script.remove();
      loading = undefined;
      reject(
        new Error(
          "Não foi possível carregar o Google Maps. Confira a conexão, a chave e os domínios autorizados.",
        ),
      );
    };
    globals[callback] = () => {
      cleanup();
      resolve();
    };
    const query = new URLSearchParams({
      key: import.meta.env.VITE_GOOGLE_MAPS_API_KEY,
      v: "weekly",
      loading: "async",
      callback,
      language: "pt-BR",
      region: "BR",
    });
    script.src = `https://maps.googleapis.com/maps/api/js?${query}`;
    script.async = true;
    script.onerror = fail;
    document.head.append(script);
  });
  return loading;
}
export type StationSelection = {
  name: string;
  address: string;
  city: string;
  state: string;
  lat: string;
  lng: string;
  external_id: string;
};
export function stationFromPlace(
  place: google.maps.places.Place,
): StationSelection {
  const parts = place.addressComponents || [];
  const component = (type: string, short = false) => {
    const item = parts.find((part) => part.types.includes(type));
    return (short ? item?.shortText : item?.longText) || "";
  };
  if (component("country", true) !== "BR")
    throw new Error("Selecione um posto no Brasil.");
  if (!place.location)
    throw new Error(
      "Este posto não informou sua localização. Use o cadastro manual.",
    );
  return {
    name: place.displayName || "",
    address: place.formattedAddress || "",
    city: component("administrative_area_level_2") || component("locality"),
    state: component("administrative_area_level_1", true),
    lat: place.location.lat().toFixed(6),
    lng: place.location.lng().toFixed(6),
    external_id: place.id,
  };
}
