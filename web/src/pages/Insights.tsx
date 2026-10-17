import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { toast } from "sonner";
import { Bar, BarChart, CartesianGrid, Legend, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { Button, Card, PageHeader, Skeleton } from "../components/ui";
import { postJson } from "../lib/api";
import { useAppStore } from "../store/useAppStore";

interface Factor {
  name: string;
  meaning: string;
  generic: number;
  twin: number;
  winner: "generic" | "twin" | "close";
  reason: string;
  improve: string;
}

const winnerLabel = { generic: "Generic GPT leads", twin: "Doctor's Twin leads", close: "Close" };
const winnerClass = {
  generic: "text-amber-700 dark:text-amber-200",
  twin: "text-sky-700 dark:text-sky-200",
  close: "text-slate-500",
};

function Meter({ label, value, bar, text }: { label: string; value: number; bar: string; text: string }) {
  return (
    <div className="flex items-center gap-3 text-sm">
      <span className={`w-28 shrink-0 ${text}`}>{label}</span>
      <div className="h-2 flex-1 overflow-hidden rounded-full bg-slate-200/80 dark:bg-white/10">
        <div className={`h-full rounded-full transition-all duration-700 ${bar}`} style={{ width: `${value}%` }} />
      </div>
      <span className="w-8 shrink-0 text-right tabular-nums">{value}</span>
    </div>
  );
}

export default function Insights() {
  const generic = useAppStore((s) => s.genericResult);
  const twin = useAppStore((s) => s.twinResult);
  const navigate = useNavigate();
  const [factors, setFactors] = useState<Factor[] | null>(null);
  const [depths, setDepths] = useState<{ generic: number; twin: number } | null>(null);

  useEffect(() => {
    if (!generic || !twin) return;
    postJson<{ metrics: Record<string, number>; factors: Factor[] }>("/api/compare", { generic, twin })
      .then((data) => {
        setFactors(data.factors);
        setDepths({ generic: data.metrics["Generic Context Depth"], twin: data.metrics["Twin Context Depth"] });
      })
      .catch((error: Error) => toast.error(error.message));
  }, [generic, twin]);

  if (!generic || !twin) {
    return <Card><p>Please run the generic and twin consultations first.</p><Link to="/generic" className="text-sky-600">Open generic baseline</Link></Card>;
  }

  const twinLeads = factors?.filter((item) => item.winner === "twin").length ?? 0;
  const genericLeads = factors?.filter((item) => item.winner === "generic").length ?? 0;
  const close = factors?.filter((item) => item.winner === "close").length ?? 0;

  return (
    <div>
      <PageHeader eyebrow="8 · Insights" title="Comparison Insights" caption="Generic GPT and the Doctor's Twin, scored on the same factors." />
      {!factors && <Skeleton className="h-80" />}
      {factors && (
        <>
          <Card className="mb-4">
            <h2 className="text-base font-semibold">What each factor means</h2>
            <p className="mt-1 text-sm text-slate-600 dark:text-slate-300">Amber is Generic GPT. Blue is the Doctor's Twin. A higher bar means that answer did more of that job on this run. These scores explain the written answer and the evidence that was retrieved. They are not a diagnosis.</p>
            <dl className="mt-4 grid gap-3 sm:grid-cols-2">
              {factors.map((factor) => (
                <div key={factor.name} className="rounded-xl border border-slate-200/80 px-3 py-3 dark:border-white/10">
                  <dt className="text-sm font-semibold">{factor.name}</dt>
                  <dd className="mt-1 text-sm leading-6 text-slate-600 dark:text-slate-300">{factor.meaning}</dd>
                </div>
              ))}
            </dl>
          </Card>
          <p className="mb-3 text-sm text-slate-600 dark:text-slate-300">
            Doctor's Twin leads {twinLeads} of {factors.length}. Generic GPT leads {genericLeads === 0 ? "none" : genericLeads}. {close} {close === 1 ? "is" : "are"} close.
          </p>
          <Card className="h-[640px]">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={factors} layout="vertical" margin={{ left: 8, right: 16, top: 8, bottom: 8 }} barGap={4} barCategoryGap="22%">
                <CartesianGrid strokeDasharray="3 3" stroke="#94a3b833" horizontal={false} />
                <XAxis type="number" domain={[0, 100]} tick={{ fontSize: 12 }} axisLine={false} tickLine={false} />
                <YAxis type="category" dataKey="name" width={176} tick={{ fontSize: 12 }} axisLine={false} tickLine={false} />
                <Tooltip cursor={{ fill: "#94a3b822" }} />
                <Legend />
                <Bar dataKey="generic" name="Generic GPT" fill="#fbbf24" radius={[0, 6, 6, 0]} barSize={12} />
                <Bar dataKey="twin" name="Doctor's Twin" fill="#38bdf8" radius={[0, 6, 6, 0]} barSize={12} />
              </BarChart>
            </ResponsiveContainer>
          </Card>
          <div className="mt-4 grid gap-3 lg:grid-cols-2">
            {factors.map((factor) => (
              <Card key={factor.name}>
                <div className="flex items-start justify-between gap-3">
                  <h2 className="font-semibold">{factor.name}</h2>
                  <p className={`shrink-0 text-sm font-semibold ${winnerClass[factor.winner]}`}>{winnerLabel[factor.winner]}</p>
                </div>
                <div className="mt-3 space-y-2">
                  <Meter label="Generic GPT" value={factor.generic} bar="bg-amber-400" text="text-amber-700 dark:text-amber-200" />
                  <Meter label="Doctor's Twin" value={factor.twin} bar="bg-sky-400" text="text-sky-700 dark:text-sky-200" />
                </div>
                <p className="mt-3 text-sm leading-6 text-slate-600 dark:text-slate-300">{factor.reason}</p>
                {factor.improve && <p className="mt-2 text-sm leading-6 text-slate-700 dark:text-slate-200"><span className="font-semibold">How to improve Doctor's Twin: </span>{factor.improve}</p>}
              </Card>
            ))}
          </div>
          {depths && (
            <div className="mt-4 grid gap-3 md:grid-cols-2">
              <Card>
                <p className="text-sm text-amber-700 dark:text-amber-200">Generic context depth</p>
                <p className="text-3xl font-semibold tabular-nums">{depths.generic}</p>
                <p className="mt-1 text-xs text-slate-500">Average of all {factors.length} generic scores.</p>
              </Card>
              <Card>
                <p className="text-sm text-sky-700 dark:text-sky-200">Doctor's Twin context depth</p>
                <p className="text-3xl font-semibold tabular-nums">{depths.twin}</p>
                <p className="mt-1 text-xs text-slate-500">Average of all {factors.length} Doctor's Twin scores.</p>
              </Card>
            </div>
          )}
        </>
      )}
      <Button className="mt-4" variant="primary" onClick={() => navigate("/why")}>Open Why This Recommendation</Button>
    </div>
  );
}
