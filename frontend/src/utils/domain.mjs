export function parseDecimal(value) {
  const s = String(value).trim().replace(",", ".");
  if (!/^\d+(?:\.\d+)?$/.test(s)) return NaN;
  return Number(s);
}
export function checkFuel(price, total, liters) {
  const p = parseDecimal(price),
    t = parseDecimal(total),
    l = parseDecimal(liters);
  if (![p, t, l].every((n) => Number.isFinite(n) && n > 0)) return null;
  const expected = Math.round((p * l + Number.EPSILON) * 100) / 100;
  const difference = Math.round((t - expected) * 100) / 100;
  return {
    expected,
    difference,
    effective: t / l,
    consistent: Math.abs(difference) <= 0.01,
  };
}
export function normalizedName(s) {
  return s
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLowerCase()
    .replace(/\s+/g, " ")
    .trim();
}
