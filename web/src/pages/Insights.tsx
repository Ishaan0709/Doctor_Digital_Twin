import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { toast } from "sonner";
import { Bar, BarChart, CartesianGrid, Legend, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { Button, Card, PageHeader, Skeleton } from "../components/ui";
import { getJson, postJson } from "../lib/api";
import { useAppStore } from "../store/useAppStore";

interface CalcLine {
  label: string;
  detail: string;
  value: number;
}

interface CalcSide {
  lines: CalcLine[];
  passed: number;
  checks: number;
  total: number;
}

interface Factor {
  name: string;
  meaning: string;
  generic: number;
  twin: number;
  winner: "generic" | "twin" | "close";
  reason: string;
  improve: string;
  calculation: {
    formula: string;
    generic: CalcSide;
    twin: CalcSide;
  };
}

interface DepthWork {
  sum: number;
  count: number;
  raw: string;
  total: number;
}

const winnerLabel = { generic: "Generic GPT leads", twin: "Doctor's Twin leads", close: "Close" };
const winnerClass = {
  generic: "text-amber-700 dark:text-amber-200",
  twin: "text-sky-700 dark:text-sky-200",
  close: "text-slate-500",
};

function mark(value: number) {
  return value === 1 ? "Pass" : "Miss";
}

interface EvalSummary {
  n: number;
  test_precision: number | null;
  test_recall: number | null;
  risk_agreement: number | null;
  followup_agreement: number | null;
}

interface EvalPayload {
  available: boolean;
  holdout_size: number;
  source?: string;
  summary?: Record<string, EvalSummary> | null;
  gold?: { tests: string; risk: string; followup: string } | null;
  judge?: { n: number; generic: EvalJudge; rag: EvalJudge; twin: EvalJudge } | null;
}

interface EvalJudge {
  caution: number | null;
  specificity: number | null;
  traceability: number | null;
}

function shown(value: number | null | undefined) {
  if (value == null) return "—";
  return value.toFixed(2);
}

function Ledger({ title, side, tone }: { title: string; side: CalcSide; tone: string }) {
  return (
    <div>
      <p className={`text-sm font-semibold ${tone}`}>{title}</p>
      <ul className="mt-2 divide-y divide-[#c5d7ea] dark:divide-white/10">
        {side.lines.map((line, index) => (
          <li key={`${line.label}-${index}`} className="flex items-start justify-between gap-3 py-2">
            <div>
              <p className="text-sm font-medium text-[#0b1f3a] dark:text-white">{line.label}</p>
              <p className="text-xs leading-5 text-[#2c4060] dark:text-[#d5e4f0]">{line.detail}</p>
            </div>
            <span className="shrink-0 text-sm font-semibold text-[#0b1f3a] dark:text-white">{mark(line.value)}</span>
          </li>
        ))}
      </ul>
      <p className="mt-2 border-t border-[#c5d7ea] pt-2 text-sm font-semibold text-[#0b1f3a] dark:border-white/10 dark:text-white">
        {side.passed} of {side.checks} checks passed. {side.passed} / {side.checks} × 100 = {side.total}.
      </p>
    </div>
  );
}

function Calculation({ factor }: { factor: Factor }) {
  return (
    <details className="mt-3 rounded-xl border border-[#c5d7ea] bg-[#f3f7fc] dark:border-white/10 dark:bg-[#071422]">
      <summary className="cursor-pointer px-3 py-2 text-sm font-semibold text-[#123a6b] dark:text-[#8eb8e8]">How this score was calculated</summary>
      <div className="space-y-4 px-3 pb-3">
        <p className="text-sm leading-6 text-[#2c4060] dark:text-[#d5e4f0]">{factor.calculation.formula}</p>
        <Ledger title="Generic GPT" side={factor.calculation.generic} tone="text-amber-700 dark:text-amber-200" />
        <Ledger title="Doctor's Twin" side={factor.calculation.twin} tone="text-sky-700 dark:text-sky-200" />
      </div>
    </details>
  );
}

function DepthMath({ scores, work }: { scores: { name: string; value: number }[]; work: DepthWork }) {
  return (
    <details className="mt-3 rounded-xl border border-[#c5d7ea] bg-[#f3f7fc] dark:border-white/10 dark:bg-[#071422]">
      <summary className="cursor-pointer px-3 py-2 text-sm font-semibold text-[#123a6b] dark:text-[#8eb8e8]">How this average was calculated</summary>
      <div className="px-3 pb-3">
        <ul className="divide-y divide-[#c5d7ea] dark:divide-white/10">
          {scores.map((item) => (
            <li key={item.name} className="flex items-center justify-between gap-3 py-1.5 text-sm text-[#0b1f3a] dark:text-white">
              <span>{item.name}</span>
              <span className="tabular-nums">{item.value}</span>
            </li>
          ))}
        </ul>
        <p className="mt-2 text-sm leading-6 text-[#2c4060] dark:text-[#d5e4f0]">
          {scores.map((item) => item.value).join(" + ")} = {work.sum}. {work.sum} ÷ {work.count} = {work.raw}, which rounds to {work.total}. A value of .50 rounds up.
        </p>
      </div>
    </details>
  );
}

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

const EVAL_ROWS = [
  ["generic", "Generic GPT"],
  ["rag", "GPT + retrieved cases"],
  ["twin", "Doctor's Twin"],
] as const;

function Evaluation() {
  const [report, setReport] = useState<EvalPayload | null>(null);
  const [failed, setFailed] = useState(false);

  useEffect(() => {
    getJson<EvalPayload>("/api/eval/results")
      .then(setReport)
      .catch(() => setFailed(true));
  }, []);

  return (
    <Card className="mt-4">
      <h2 className="text-base font-semibold">Evaluation</h2>
      <p className="mt-1 text-sm leading-6 text-[#2c4060] dark:text-[#d5e4f0]">
        Thirty cases are held out of the doctor’s case file and excluded from retrieval. Generic GPT, Generic GPT with those same cases, and the Doctor’s Twin are each compared with the doctor’s recorded decision.
      </p>
      {failed && <p className="mt-3 text-sm text-[#0b1f3a] dark:text-white">The evaluation results could not be loaded.</p>}
      {report && !report.available && (
        <p className="mt-3 text-sm leading-6 text-[#0b1f3a] dark:text-white">
          No held-out results are saved yet. The run scores {report.holdout_size} cases. Start it with <span className="font-semibold">python eval/run_eval.py</span>.
        </p>
      )}
      {report?.available && report.summary && (
        <>
          <p className="mt-3 text-sm font-semibold text-[#0b1f3a] dark:text-white">{report.holdout_size} held-out cases</p>
          <div className="mt-3 overflow-x-auto">
            <table className="w-full min-w-[640px] text-left text-sm text-[#0b1f3a] dark:text-white">
              <thead className="text-[#123a6b] dark:text-[#8eb8e8]">
                <tr>
                  <th className="py-2 pr-3 font-semibold">System</th>
                  <th className="py-2 pr-3 font-semibold">Cases scored</th>
                  <th className="py-2 pr-3 font-semibold">Test precision</th>
                  <th className="py-2 pr-3 font-semibold">Test recall</th>
                  <th className="py-2 pr-3 font-semibold">Risk agreement</th>
                  <th className="py-2 font-semibold">Follow-up agreement</th>
                </tr>
              </thead>
              <tbody>
                {EVAL_ROWS.map(([key, label]) => {
                  const item = report.summary?.[key];
                  return (
                    <tr key={key} className="border-t border-[#c5d7ea] dark:border-white/10">
                      <td className="py-2 pr-3">{label}</td>
                      <td className="py-2 pr-3 tabular-nums">{item?.n ?? "—"}</td>
                      <td className="py-2 pr-3 tabular-nums">{shown(item?.test_precision)}</td>
                      <td className="py-2 pr-3 tabular-nums">{shown(item?.test_recall)}</td>
                      <td className="py-2 pr-3 tabular-nums">{shown(item?.risk_agreement)}</td>
                      <td className="py-2 tabular-nums">{shown(item?.followup_agreement)}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
          {report.gold && (
            <p className="mt-3 text-sm leading-6 text-[#2c4060] dark:text-[#d5e4f0]">
              Tests: {report.gold.tests} Risk: {report.gold.risk} Follow-up: {report.gold.followup}
            </p>
          )}
          {report.judge && (
            <p className="mt-2 text-sm leading-6 text-[#2c4060] dark:text-[#d5e4f0]">
              A blinded judge scored {report.judge.n} of these cases. Doctor’s Twin traceability {shown(report.judge.twin.traceability)}, GPT with cases {shown(report.judge.rag.traceability)}, Generic GPT {shown(report.judge.generic.traceability)}, each out of 5.
            </p>
          )}
        </>
      )}
    </Card>
  );
}

export default function Insights() {
  const generic = useAppStore((s) => s.genericResult);
  const twin = useAppStore((s) => s.twinResult);
  const navigate = useNavigate();
  const [factors, setFactors] = useState<Factor[] | null>(null);
  const [depths, setDepths] = useState<{ generic: number; twin: number } | null>(null);
  const [depthWork, setDepthWork] = useState<{ generic: DepthWork; twin: DepthWork } | null>(null);

  useEffect(() => {
    if (!generic || !twin) return;
    postJson<{ metrics: Record<string, number>; factors: Factor[]; depth: { generic: DepthWork; twin: DepthWork } }>("/api/compare", { generic, twin })
      .then((data) => {
        setFactors(data.factors);
        setDepths({ generic: data.metrics["Generic Context Depth"], twin: data.metrics["Twin Context Depth"] });
        setDepthWork(data.depth);
      })
      .catch((error: Error) => toast.error(error.message));
  }, [generic, twin]);

  const ready = Boolean(generic && twin);

  const twinLeads = factors?.filter((item) => item.winner === "twin").length ?? 0;
  const genericLeads = factors?.filter((item) => item.winner === "generic").length ?? 0;
  const close = factors?.filter((item) => item.winner === "close").length ?? 0;

  return (
    <div>
      <PageHeader eyebrow="8 · Insights" title="Comparison Insights" caption="Generic GPT and the Doctor's Twin, scored on the same factors." />
      <p className="mb-4 rounded-xl border border-[#c5d7ea] bg-[#e7f1fb] px-4 py-3 text-sm leading-6 text-[#0b1f3a] dark:border-white/10 dark:bg-[#16345c] dark:text-white">
        These scores measure traceability, not clinical correctness. Each number is the share of checks the written answer passed. A higher bar means more of those checks were found in the answer and its evidence. It is not a rate of correct diagnoses.
      </p>
      {!ready && (
        <Card className="mb-4">
          <p>Please run the generic and twin consultations first.</p>
          <Link to="/generic" className="text-[#123a6b] dark:text-[#8eb8e8]">Open generic baseline</Link>
        </Card>
      )}
      {ready && !factors && <Skeleton className="h-80" />}
      {ready && factors && (
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
                <YAxis type="category" dataKey="name" width={210} tick={{ fontSize: 12 }} axisLine={false} tickLine={false} />
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
                {factor.calculation && <Calculation factor={factor} />}
              </Card>
            ))}
          </div>
          {depths && depthWork && (
            <div className="mt-4 grid gap-3 md:grid-cols-2">
              <Card>
                <p className="text-sm text-amber-700 dark:text-amber-200">Generic context depth</p>
                <p className="text-3xl font-semibold tabular-nums">{depths.generic}</p>
                <p className="mt-1 text-xs text-slate-500">Average of all {factors.length} generic scores.</p>
                <DepthMath scores={factors.map((item) => ({ name: item.name, value: item.generic }))} work={depthWork.generic} />
              </Card>
              <Card>
                <p className="text-sm text-sky-700 dark:text-sky-200">Doctor's Twin context depth</p>
                <p className="text-3xl font-semibold tabular-nums">{depths.twin}</p>
                <p className="mt-1 text-xs text-slate-500">Average of all {factors.length} Doctor's Twin scores.</p>
                <DepthMath scores={factors.map((item) => ({ name: item.name, value: item.twin }))} work={depthWork.twin} />
              </Card>
            </div>
          )}
        </>
      )}
      <Evaluation />
      <Button className="mt-4" variant="primary" onClick={() => navigate("/why")}>Open Why This Recommendation</Button>
    </div>
  );
}
