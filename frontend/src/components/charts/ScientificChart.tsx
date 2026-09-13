import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import type { InvestigationChart } from "@/lib/types";
import { Card } from "@/components/ui/card";

function sampleNumber(row: Record<string, string>, keys: string[]) {
  for (const key of keys) {
    if (row[key] !== undefined) return Number(row[key]);
  }
  return 0;
}

export function ScientificChart({ spec }: { spec: InvestigationChart }) {
  if (spec.kind === "units") {
    return (
      <figure className="space-y-2">
        <h3 className="text-base font-semibold">{spec.title}</h3>
        <p className="text-sm text-muted">
          {spec.subtitle} Provenance: {spec.role} educational illustration, not backend-derived evidence.
        </p>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <caption className="sr-only">Dimension comparison</caption>
            <thead>
              <tr>
                <th>Quantity</th>
                <th>Familiar unit</th>
                <th>Dimension vector</th>
              </tr>
            </thead>
            <tbody>
              {(spec.rows ?? []).map((row) => (
                <tr key={row.quantity} className="border-t border-line">
                  <td className="py-2">{row.quantity}</td>
                  <td>{row.unit}</td>
                  <td>{row.vector}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </figure>
    );
  }

  const series = spec.series ?? [
    { name: spec.y_label || "value", samples: spec.samples ?? [] },
  ];
  const xKeys = ["v", "x", "t"];
  const yKeys = ["Ek", "y", "E", "U", "V"];
  const data = series[0]?.samples.map((row, index) => {
    const point: Record<string, number | string> = {
      x: sampleNumber(row, xKeys),
    };
    series.forEach((item) => {
      const sample = item.samples[index] ?? item.samples.find((s) => sampleNumber(s, xKeys) === point.x);
      if (sample) point[item.name] = sampleNumber(sample, yKeys);
    });
    return point;
  });

  return (
    <figure className="space-y-2">
      <h3 className="text-base font-semibold">{spec.title}</h3>
      <p className="text-sm text-muted">
        {spec.subtitle} A plot is not a proof. Sampling a curve does not establish a universal claim.
      </p>
      <Card className="p-3">
        <ResponsiveContainer width="100%" height={240}>
          <LineChart data={data}>
            <CartesianGrid stroke="#d5ddd9" />
            <XAxis dataKey="x" label={{ value: spec.x_label ?? "x", position: "insideBottom", offset: -2 }} />
            <YAxis label={{ value: spec.y_label ?? "y", angle: -90, position: "insideLeft" }} />
            <Tooltip />
            {series.map((item, index) => (
              <Line
                key={item.name}
                type="monotone"
                dataKey={item.name}
                stroke={index === 0 ? "#0f766e" : "#b91c1c"}
                dot={false}
                isAnimationActive={false}
              />
            ))}
          </LineChart>
        </ResponsiveContainer>
      </Card>
      <div className="overflow-x-auto">
        <table className="w-full text-left text-sm">
          <caption className="mb-1 text-left text-muted">Accessible data table · educational illustration</caption>
          <thead>
            <tr>
              <th>series</th>
              {Object.keys(series[0]?.samples[0] ?? {}).map((key) => (
                <th key={key}>{key}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {series.flatMap((item) =>
              item.samples.map((row, index) => (
                <tr key={`${item.name}-${index}`} className="border-t border-line">
                  <td className="py-1">{item.name}</td>
                  {Object.values(row).map((value, i) => (
                    <td key={i}>{value}</td>
                  ))}
                </tr>
              )),
            )}
          </tbody>
        </table>
      </div>
    </figure>
  );
}
