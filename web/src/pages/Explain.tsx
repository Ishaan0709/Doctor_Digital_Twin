import { Link, useNavigate } from "react-router-dom";
import { Button, Card, PageHeader } from "../components/ui";
import { useAppStore } from "../store/useAppStore";

export default function Explain() {
  const patient = useAppStore((s) => s.patient);
  const generic = useAppStore((s) => s.genericResult);
  const twin = useAppStore((s) => s.twinResult);
  const navigate = useNavigate();
  if (!patient || !generic || !twin) {
    return <Card><p>Please complete intake, generic, and twin pages first.</p><Link to="/patient" className="text-sky-600">Open intake</Link></Card>;
  }
  const historyCount = twin.historical_patterns?.length || 0;
  const graphLinks = twin.graph_evidence?.links?.length || 0;
  const cb = twin.confidence_breakdown || {};
  const steps = [
    ["Datasets and what they provide", ["Doctor cases provide specialist patterns: symptoms, diagnosis, decision, and outcome.", "Graph nodes define clinical entities. Graph edges define the relationship logic.", "The live patient input is the context for this run."]],
    ["How generic output is produced", ["It uses the patient context and the generic system prompt.", "It does not retrieve specialist cases or walk the graph.", "Its job is a neutral baseline before specialist enrichment."]],
    ["How case similarity is computed", ["Patient and case texts are embedded into vectors.", "FAISS returns cosine similarity. Higher means closer context.", "A rerank layer adds a small bonus when clinical terms overlap."]],
    ["How GraphRAG contributes", ["Patient clues are mapped onto graph nodes.", "Outgoing edges capture related risks, tests, and decisions.", "Those links are written into the twin prompt as an evidence trace."]],
    ["How comparison scores are calculated", ["Scores are transparent keyword heuristics, not diagnostic truth.", "A base score plus indicator hits is capped at 100.", "Specialist signals from retrieved cases and graph links raise the twin scores."]],
  ];
  return (
    <div>
      <PageHeader eyebrow="10 · Explainability" title="Clinical Explainability Report" caption="From raw datasets to the final recommendation, in plain language." />
      <Card className="mb-4"><p className="text-sm">This report shows which data was used, what each engine contributed, where the score came from, and why the specialist recommendation has this shape.</p></Card>
      <Card>
        <h2 className="font-semibold">End-to-end pipeline</h2>
        <ol className="mt-3 list-decimal space-y-3 pl-5 text-sm leading-6">
          <li>Intake captures symptoms, duration, history, lifestyle, medicines, BP, LDL, HbA1c, and notes for {patient.name}.</li>
          <li>The generic baseline uses only that context and <code>prompts/generic_gpt.txt</code>.</li>
          <li>Case retrieval embeds the patient text and searches the specialist case index. Retrieved cases this run: <strong>{historyCount}</strong>.</li>
          <li>Reranking adds bonuses for overlap such as chest pain, LDL, diabetes, blood pressure, and CAD.</li>
          <li>Graph reasoning walks nodes and edges. Graph links activated this run: <strong>{graphLinks}</strong>.</li>
          <li>The specialist prompt combines the patient, retrieved cases, graph evidence, and uniqueness flags.</li>
          <li>Confidence is <code>min(0.98, 0.60 + 0.07×cases + 0.03×graph links)</code>. This run: base {Number(cb.base ?? 0.6).toFixed(2)} + retrieval {Number(cb.retrieval_component ?? 0).toFixed(2)} + graph {Number(cb.graph_component ?? 0).toFixed(2)} = {Number(cb.final_score ?? twin.confidence_score ?? 0).toFixed(2)}.</li>
        </ol>
      </Card>
      <div className="mt-4 space-y-3">
        {steps.map(([title, lines]) => (
          <details key={String(title)} className="rounded-2xl border border-slate-200 p-4 dark:border-white/10" open={title === steps[0][0]}>
            <summary className="cursor-pointer font-semibold">{title}</summary>
            <ul className="mt-2 list-disc space-y-1 pl-5 text-sm">{(lines as string[]).map((line) => <li key={line}>{line}</li>)}</ul>
          </details>
        ))}
      </div>
      <div className="mt-4 grid gap-4 md:grid-cols-2">
        <Card><h2 className="font-semibold">Generic GPT</h2><ul className="mt-2 list-disc space-y-1 pl-5 text-sm"><li>Broad medical language.</li><li>No specialist memory.</li><li>No graph expansion.</li><li>Useful as a neutral baseline.</li></ul></Card>
        <Card><h2 className="font-semibold">Dr. Pandey twin</h2><ul className="mt-2 list-disc space-y-1 pl-5 text-sm"><li>Uses historical decisions and outcomes.</li><li>Uses graph links for explicit paths.</li><li>More personalized recommendations.</li><li>Shows the confidence components.</li></ul></Card>
      </div>
      <Card className="mt-4"><p className="text-sm">This platform is decision-support infrastructure, not an autonomous diagnosis engine. The useful result comes from patient context, specialist history, graph-backed reasoning, and a clinician.</p></Card>
      <Button className="mt-4" variant="primary" onClick={() => navigate("/why")}>Return to Why This Recommendation</Button>
    </div>
  );
}
