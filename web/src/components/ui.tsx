import { useEffect, useState, type ButtonHTMLAttributes, type ReactNode } from "react";
import { InlineText } from "./RichText";
import { getJson } from "../lib/api";
import { cn } from "../lib/utils";
import type { Source, TwinResult } from "../types";

export function Button({
  variant = "ghost",
  className,
  ...props
}: ButtonHTMLAttributes<HTMLButtonElement> & { variant?: "primary" | "ghost" | "danger" }) {
  return (
    <button
      className={cn(
        "inline-flex items-center justify-center gap-2 rounded-xl px-4 py-2 text-sm font-semibold transition disabled:cursor-not-allowed disabled:opacity-50",
        variant === "primary" && "rounded-full bg-[#172033] text-[#f7f4ef] shadow-sm hover:-translate-y-0.5 hover:bg-[#2a2118] dark:bg-[#f3eadf] dark:text-[#172033]",
        variant === "ghost" && "rounded-full border border-[#e4d8c8] bg-white/80 text-[#172033] hover:-translate-y-0.5 hover:border-[#b8956a] dark:border-white/10 dark:bg-white/5 dark:text-[#f4efe8]",
        variant === "danger" && "border border-amber-400/40 bg-amber-500/10 text-amber-800 dark:text-amber-200",
        className,
      )}
      {...props}
    />
  );
}

export function Card({ children, className }: { children: ReactNode; className?: string }) {
  return (
    <section className={cn("rounded-[1.6rem] border border-[#eadfd2] bg-white/90 p-5 shadow-[0_18px_50px_rgba(23,32,51,0.06)] backdrop-blur transition duration-200 hover:shadow-[0_22px_60px_rgba(23,32,51,0.1)] dark:border-white/10 dark:bg-[#121a2b]/90", className)}>
      {children}
    </section>
  );
}

export function PageHeader({ eyebrow, title, caption }: { eyebrow?: string; title: string; caption?: string }) {
  return (
    <header className="mb-5">
      {eyebrow && <p className="text-xs font-semibold uppercase tracking-[0.22em] text-[#8a6a3b]">{eyebrow}</p>}
      <h1 className="mt-2 font-display text-3xl font-semibold tracking-tight text-[#172033] dark:text-[#f7f4ef] md:text-4xl">{title}</h1>
      {caption && <p className="mt-2 max-w-3xl text-sm text-slate-600 dark:text-slate-300">{caption}</p>}
    </header>
  );
}

export function Fold({ title, children }: { title: string; children: ReactNode }) {
  return (
    <details className="rounded-[1.4rem] border border-[#eadfd2] bg-white/90 dark:border-white/10 dark:bg-[#121a2b]">
      <summary className="cursor-pointer list-none px-5 py-4 font-medium text-[#172033] dark:text-[#f7f4ef]">{title}</summary>
      <div className="px-5 pb-5">{children}</div>
    </details>
  );
}

export function Note({ title, children }: { title: string; children: ReactNode }) {
  return (
    <Card className="mb-4">
      <h2 className="text-base font-semibold">{title}</h2>
      <p className="mt-1 text-sm leading-6 text-slate-600 dark:text-slate-300">{children}</p>
    </Card>
  );
}

export function Skeleton({ className }: { className?: string }) {
  return <div className={cn("animate-pulse rounded-xl bg-slate-200/90 dark:bg-white/10", className)} />;
}

export function Disclaimer({ text }: { text?: string }) {
  return (
    <p className="mt-4 rounded-xl border border-amber-400/30 bg-amber-500/10 px-3 py-2 text-xs leading-5 text-amber-900 dark:text-amber-100">
      {text || "This is clinical decision support and is not a substitute for a real doctor or emergency care."}
    </p>
  );
}

export function BulletList({ items }: { items?: string[] }) {
  if (!items?.length) return <p className="text-sm text-slate-500">None listed.</p>;
  return (
    <ul className="space-y-2 text-sm leading-6">
      {items.map((item) => (
        <li key={item} className="flex gap-2">
          <span className="mt-2 h-1.5 w-1.5 shrink-0 rounded-full bg-sky-500" />
          <span><InlineText text={item} /></span>
        </li>
      ))}
    </ul>
  );
}

export function SourceList({ sources }: { sources?: Source[] }) {
  if (!sources?.length) return null;
  return (
    <div className="mt-4">
      <h3 className="text-sm font-semibold">Sources used</h3>
      <ul className="mt-2 space-y-1 text-sm text-slate-600 dark:text-slate-300">
        {sources.map((source, index) => (
          <li key={`${source.type}-${source.id || index}`}>
            {source.type === "case"
              ? `Case ${source.id}: ${source.diagnosis || "pattern"}${source.score != null ? ` (similarity ${Number(source.score).toFixed(2)})` : ""}`
              : source.text}
          </li>
        ))}
      </ul>
    </div>
  );
}

export function Confidence({ result }: { result: Pick<TwinResult, "confidence_score" | "confidence_breakdown"> }) {
  const score = result.confidence_score || 0;
  const pct = Math.round(score * 100);
  const breakdown = result.confidence_breakdown || {};
  const help = `Confidence = min(0.98, base + retrieval + graph). base=${(breakdown.base ?? 0.6).toFixed(2)}, retrieval=${(breakdown.retrieval_component ?? 0).toFixed(2)}, graph=${(breakdown.graph_component ?? 0).toFixed(2)}`;
  return (
    <div title={help} className="rounded-2xl border border-sky-400/30 bg-sky-500/10 p-4">
      <p className="text-xs font-semibold uppercase tracking-wide text-sky-700 dark:text-sky-200">Confidence</p>
      <p className="mt-1 text-3xl font-semibold">{pct}%</p>
      <div className="mt-3 h-2 overflow-hidden rounded-full bg-slate-200 dark:bg-white/10">
        <div className="h-full rounded-full bg-[#123a6b]" style={{ width: `${pct}%` }} />
      </div>
      <p className="mt-2 text-xs text-slate-600 dark:text-slate-300">{help}</p>
    </div>
  );
}

export function ModelNote({ role = "pair", className }: { role?: "visit" | "gpt" | "pair"; className?: string }) {
  const [label, setLabel] = useState("");
  useEffect(() => {
    getJson<{ visit_model?: string; comparison_model?: string; llm_model?: string }>("/health")
      .then((data) => {
        const visit = data.visit_model || "llama3.2";
        const plain = data.comparison_model || "gpt-4o-mini";
        if (role === "visit") setLabel(`Local SLM · ${visit} · cases and graph stay on this machine`);
        else if (role === "gpt") setLabel(`GPT · ${plain} · this visit only`);
        else setLabel(`Vimlesh visit · local SLM ${visit} · comparison · GPT ${plain}`);
      })
      .catch(() => setLabel(""));
  }, [role]);
  if (!label) return null;
  return <p className={cn("text-[11px] uppercase tracking-[0.16em] text-[#8a6a3b]", className)}>{label}</p>;
}

export const fieldClass =
  "w-full rounded-xl border border-[#c5d7ea] bg-white px-3 py-2 text-sm text-[#0b1f3a] outline-none ring-[#123a6b]/25 transition placeholder:text-[#5c7190] focus:ring-2 dark:border-white/15 dark:bg-[#071422] dark:text-[#e7f0fa] dark:placeholder:text-[#9eb0c8]";
