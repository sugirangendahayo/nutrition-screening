import { CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";
import { RiskBadge } from "@/components/ui/RiskBadge";
import { TrendBadge } from "@/components/ui/TrendBadge";
import { formatDate } from "@/lib/format";
import type { TrendResult } from "@/types";

export function TrendPanel({ trend }: { trend: TrendResult }) {
  if (trend.status === "insufficient_data") {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Nutrition Screening Trend</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-ink-500">
            Insufficient historical data. A trend will be shown once this child has at least two
            recorded assessments.
          </p>
        </CardContent>
      </Card>
    );
  }

  const chartData = trend.series.map((entry) => ({
    date: formatDate(entry.assessedAt),
    Stunting: entry.predictions.stunting?.probability ?? null,
    Underweight: entry.predictions.underweight?.probability ?? null,
  }));

  return (
    <Card>
      <CardHeader className="flex items-center justify-between">
        <CardTitle>Nutrition Screening Trend</CardTitle>
        <div className="flex items-center gap-2 text-sm text-ink-500">
          Overall: <TrendBadge status={trend.overall} />
        </div>
      </CardHeader>
      <CardContent className="flex flex-col gap-6">
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <div className="flex items-center justify-between rounded-md border border-ink-100 px-4 py-3">
            <span className="text-sm font-medium text-ink-700">Stunting</span>
            <TrendBadge status={trend.perTarget.stunting} />
          </div>
          <div className="flex items-center justify-between rounded-md border border-ink-100 px-4 py-3">
            <span className="text-sm font-medium text-ink-700">Underweight</span>
            <TrendBadge status={trend.perTarget.underweight} />
          </div>
        </div>

        {chartData.some((d) => d.Stunting !== null || d.Underweight !== null) && (
          <div className="h-56 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={chartData} margin={{ top: 8, right: 16, bottom: 0, left: -16 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#eceef0" />
                <XAxis dataKey="date" tick={{ fontSize: 12 }} stroke="#8691a0" />
                <YAxis
                  domain={[0, 1]}
                  tickFormatter={(v) => `${Math.round(v * 100)}%`}
                  tick={{ fontSize: 12 }}
                  stroke="#8691a0"
                />
                <Tooltip
                  formatter={(value) => `${Math.round(Number(value) * 100)}%`}
                />
                <Line type="monotone" dataKey="Stunting" stroke="#c8801c" strokeWidth={2} dot />
                <Line type="monotone" dataKey="Underweight" stroke="#2f8280" strokeWidth={2} dot />
              </LineChart>
            </ResponsiveContainer>
          </div>
        )}

        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-ink-100 text-left text-xs uppercase tracking-wide text-ink-400">
                <th className="py-2 pr-4 font-medium">Date</th>
                <th className="py-2 pr-4 font-medium">Stunting</th>
                <th className="py-2 pr-4 font-medium">Underweight</th>
              </tr>
            </thead>
            <tbody>
              {trend.series.map((entry, index) => (
                <tr key={index} className="border-b border-ink-100 last:border-0">
                  <td className="py-2 pr-4 text-ink-500">{formatDate(entry.assessedAt)}</td>
                  <td className="py-2 pr-4">
                    <RiskBadge label={entry.predictions.stunting?.predictedLabel} />
                  </td>
                  <td className="py-2 pr-4">
                    <RiskBadge label={entry.predictions.underweight?.predictedLabel} />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </CardContent>
    </Card>
  );
}
