export const UNIT_PRESETS: { id: string; label: string; dimension: string[] }[] = [
  { id: "1", label: "dimensionless", dimension: ["0", "0", "0", "0", "0", "0", "0"] },
  { id: "kg", label: "kg (mass)", dimension: ["1", "0", "0", "0", "0", "0", "0"] },
  { id: "m", label: "m (length)", dimension: ["0", "1", "0", "0", "0", "0", "0"] },
  { id: "s", label: "s (time)", dimension: ["0", "0", "1", "0", "0", "0", "0"] },
  { id: "m/s", label: "m/s (velocity)", dimension: ["0", "1", "-1", "0", "0", "0", "0"] },
  { id: "J", label: "J (energy)", dimension: ["1", "2", "-2", "0", "0", "0", "0"] },
  { id: "N", label: "N (force)", dimension: ["1", "1", "-2", "0", "0", "0", "0"] },
  { id: "kg m/s", label: "kg·m/s (momentum)", dimension: ["1", "1", "-1", "0", "0", "0", "0"] },
  { id: "N/m", label: "N/m (stiffness)", dimension: ["1", "0", "-2", "0", "0", "0", "0"] },
  { id: "V", label: "V (voltage)", dimension: ["1", "2", "-3", "-1", "0", "0", "0"] },
  { id: "ohm", label: "Ω (resistance)", dimension: ["1", "2", "-3", "-2", "0", "0", "0"] },
  { id: "F", label: "F (capacitance)", dimension: ["-1", "-2", "4", "2", "0", "0", "0"] },
  { id: "kg/s", label: "kg/s (damping)", dimension: ["1", "0", "-1", "0", "0", "0", "0"] },
];

export function unitIdFor(dimension: string[]) {
  const key = dimension.join(",");
  return UNIT_PRESETS.find((item) => item.dimension.join(",") === key)?.id ?? "custom";
}

export function dimensionForUnit(id: string) {
  return UNIT_PRESETS.find((item) => item.id === id)?.dimension;
}

export function formatDimension(dimension: string[]) {
  const names = ["M", "L", "T", "I", "Θ", "N", "J"];
  const parts = dimension
    .map((exp, index) => (exp === "0" ? "" : `${names[index]}^{${exp}}`))
    .filter(Boolean);
  return parts.join(" ") || "1";
}
