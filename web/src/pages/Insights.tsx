import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { toast } from "sonner";
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { Button, Card, PageHeader, Skeleton } from "../components/ui";
import { postJson } from "../lib/api";
import { useAppStore } from "../store/useAppStore";

const keys = ["Personalization Score", "Use of Historical Evidence", "Risk Sensitivity", "Explainability", "Actionability", "Specialist Alignment"];
const help: Record<string, string> = {
  "Personalization Score": "How specifically the twin text refers to this patient's history and risk markers.",
  "Use of Historical Evidence": "How clearly the twin refers to cases, patterns, and outcomes.",
  "Risk Sensitivity": "How often the twin uses warning, monitor, or escalate language.",
  "Explainability": "How often the twin uses because, based on, or evidence.",
  "Actionability": "How concrete the tests, follow-up, and adjustments are.",
  "Specialist Alignment": "How often preventive cardiology markers such as ECG, echo, or lipids appear.",
};

export default function Insights() {
  const generic = useAppStore((s) => s.genericResult);
  const twin = useAppStore((s) => s.twinResult);
  const navigate = useNavigate();
  const [metrics, setMetrics] = useState<Record<string, number> | null>(null);

  useEffect(() => {
    if (!generic || !twin) return;
    postJson<{ metrics: Record<string, number> }>("/api/compare", { generic, twin })
      .then((data) => setMetrics(data.metrics))
      .catch((error: Error) => toast.error(error.message));
  }, [generic, twin]);

  if (!generic || !twin) {
    return <Card><p>Please run the generic and twin consultations first.</p><Link to="/generic" className="text-sky-600">Open generic baseline</Link></Card>;
  }
  const chart = keys.map((key) => ({ metric: key.replace(" Score", "").replace("Use of ", ""), score: metrics?.[key] || 0, full: key }));
  return (
    <div>
      <PageHeader eyebrow="8 · Insights" title="Comparison Insights" caption="Executive scores for personalization, evidence, risk framing, and actionability." />
      <Card className="mb-4"><p className="text-sm">Scores summarize depth of personalization, evidence usage, risk framing, and actionability. They compare baseline AI with the specialist twin. They are explainability metrics, not diagnostic truth.</p></Card>
      {!metrics && <Skeleton className="h-40" />}
      {metrics && (
        <>
          <div className="grid gap-3 md:grid-cols-3 xl:grid-cols-6">
            {keys.map((key) => (
              <Card key={key}>
                <p className="text-xs text-slate-500" title={help[key]}>{key}</p>
                <p className="text-2xl font-semibold">{metrics[key]}</p>
              </Card>
            ))}
          </div>
          <Card className="mt-4 h-80">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chart}>
                <CartesianGrid strokeDasharray="3 3" stroke="#94a3b833" />
                <XAxis dataKey="metric" tick={{ fontSize: 11 }} interval={0} />
                <YAxis domain={[0, 100]} />
                <Tooltip />
                <Bar dataKey="score" fill="#0ea5e9" radius={[8, 8, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </Card>
          <div className="mt-4 grid gap-3 md:grid-cols-2">
            <Card><p className="text-sm text-slate-500">Generic context depth</p><p className="text-3xl font-semibold">{metrics["Generic Context Depth"]}</p></Card>
            <Card><p className="text-sm text-slate-500">Twin context depth</p><p className="text-3xl font-semibold">{metrics["Twin Context Depth"]}</p></Card>
          </div>
        </>
      )}
      <p className="mt-4 text-sm text-slate-600 dark:text-slate-300">Twin consultation is more context-aware through patient-first reasoning, specialist historical evidence, and graph-based risk links.</p>
      <Button className="mt-4" variant="primary" onClick={() => navigate("/why")}>Open Why This Recommendation</Button>
    </div>
  );
}
