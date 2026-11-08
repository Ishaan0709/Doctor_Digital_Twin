import { useEffect, useState } from "react";
import { toast } from "sonner";
import { PatientForm } from "../components/PatientForm";
import { RichText } from "../components/RichText";
import { Card, ModelNote, PageHeader, Skeleton } from "../components/ui";
import { streamConsult } from "../lib/api";
import { useAppStore } from "../store/useAppStore";
import { demoPatient, type GenericResult, type Patient, type TwinResult } from "../types";

function visitKey(person: Patient) {
  return `${person.name}|${person.age}|${person.symptoms}|${person.medical_history}`;
}

async function runSide(kind: "generic" | "twin", person: Patient, signal: AbortSignal, onText: (text: string) => void) {
  let received: (GenericResult & TwinResult) | null = null;
  let acc = "";
  await streamConsult({ kind, patient: person }, (event) => {
    if (event.type === "meta" && event.result) received = event.result;
    if (event.type === "token" && event.text) {
      acc += event.text;
      onText(acc);
    }
    if (event.type === "done") {
      const text = event.text || acc;
      onText(text);
      if (kind === "generic") {
        useAppStore.getState().setGenericResult({ ...(received || {}), consultation_summary: text } as GenericResult);
      } else {
        useAppStore.getState().setTwinResult({
          unique_factors: [],
          historical_patterns: [],
          recommended_tests: [],
          immediate_actions: [],
          follow_up_plan: [],
          confidence_score: 0,
          ...(received || {}),
          assessment: text,
        });
      }
    }
  }, signal);
}

export default function Comparison() {
  const patient = useAppStore((s) => s.patient);
  const portalPatient = useAppStore((s) => s.portal.patient);
  const generic = useAppStore((s) => s.genericResult);
  const twin = useAppStore((s) => s.twinResult);
  const attachVisit = useAppStore((s) => s.attachVisit);
  const saveIntake = useAppStore((s) => s.savePortalIntake);
  const person = patient || portalPatient;
  const [genericLive, setGenericLive] = useState("");
  const [twinLive, setTwinLive] = useState("");
  const [running, setRunning] = useState(false);

  useEffect(() => {
    if (!person) return;
    attachVisit();
    const current = useAppStore.getState();
    const needGeneric = !current.genericResult;
    const needTwin = !(current.twinResult || current.portal.twin);
    if (current.portal.twin && !current.twinResult) current.setTwinResult(current.portal.twin);
    if (!needGeneric && !needTwin) return;
    const ctrl = new AbortController();
    setRunning(true);
    const jobs: Promise<void>[] = [];
    if (needGeneric) jobs.push(runSide("generic", person, ctrl.signal, setGenericLive));
    if (needTwin) jobs.push(runSide("twin", person, ctrl.signal, setTwinLive));
    Promise.all(jobs)
      .catch((error: Error) => {
        if (error.name !== "AbortError") toast.error(error.message);
      })
      .finally(() => {
        if (!ctrl.signal.aborted) setRunning(false);
      });
    return () => ctrl.abort();
  }, [person ? visitKey(person) : "", attachVisit]);

  if (!person) {
    return (
      <div>
        <PageHeader eyebrow="Compare" title="Both answers, from one set of details." caption="Save the visit once. The general answer and Dr. Pandey’s twin are written for you." />
        <Card>
          <PatientForm
            initial={demoPatient}
            mode="portal"
            submitLabel="Write both answers"
            onSubmit={(next) => {
              saveIntake(next);
              toast.success("Writing both answers.");
            }}
          />
        </Card>
      </div>
    );
  }

  const genericText = generic?.consultation_summary || genericLive;
  const twinText = twin?.assessment || twinLive;
  const waitingGeneric = !genericText;
  const waitingTwin = !twinText;

  return (
    <div>
      <PageHeader eyebrow="Compare" title={`Two readings for ${person.name}`} caption="The left answer is ordinary GPT, from this visit only. The right answer is the local model, with the retrieved cases and the graph. The case file never has to leave the machine for that reading." />
      <div className="mb-4 flex flex-wrap gap-4">
        <ModelNote role="gpt" />
        <ModelNote role="visit" />
      </div>
      <div className="grid gap-4 lg:grid-cols-2">
        <Card>
          <p className="text-xs uppercase tracking-[0.18em] text-[#8a6a3b]">GPT · this visit only</p>
          <h2 className="mt-1 font-display text-2xl font-semibold">General answer</h2>
          {waitingGeneric ? <Skeleton className="mt-4 h-40" /> : <RichText text={genericText} />}
          {running && waitingGeneric && <p className="mt-3 text-sm text-[#5c5348]">Writing the general answer…</p>}
        </Card>
        <Card>
          <p className="text-xs uppercase tracking-[0.18em] text-[#8a6a3b]">Local SLM · cases and graph</p>
          <h2 className="mt-1 font-display text-2xl font-semibold">Dr. Pandey’s twin</h2>
          {waitingTwin ? <Skeleton className="mt-4 h-40" /> : <RichText text={twinText} />}
          {running && waitingTwin && <p className="mt-3 text-sm text-[#5c5348]">Writing the twin…</p>}
        </Card>
      </div>
      <Verdict />
    </div>
  );
}

const vimleshPoints = {
  pros: [
    ["Written in his voice", "The twin follows Dr. Pandey’s preventive-cardiology instructions and the eight style rules, so the reading sounds like his clinic rather than a general medical note."],
    ["His 500 cases stay in the answer", "Five similar consultations are retrieved and placed beside this visit. The next step can point at a case he has already decided, and that case is a reference, not this patient."],
    ["The graph ties a finding to a step", "Blood pressure, diabetes, chest pain, and the tests he orders are linked. The answer can say which link it used, instead of offering a plan with no path back to the record."],
    ["The case file stays here", "Those cases and the graph are not sent out with the twin’s prompt. A longer, more specific reading does not become a token bill."],
    ["The same patient can continue", "A follow-up stays on this visit, with the retrieved cases and the graph still attached, so the second question does not start from a blank page."],
  ],
  cons: [
    ["A smaller model", "Llama 3.2 writes a narrower paragraph than a large general model. The value is the cases and the graph around it, not a bigger vocabulary."],
    ["One reading at a time", "The local model answers the twin while it is free. A second consultation waits, rather than scaling like a hosted API."],
  ],
};

const gptPoints = {
  pros: [
    ["Fluent general language", "GPT writes a smooth note from this visit alone, which is useful when you want a second wording that has not seen the case file."],
    ["No local model required", "That column calls OpenAI directly, so it still answers when Ollama is not running on this machine."],
  ],
  cons: [
    ["This visit only", "GPT is not given the 500 cases or the graph, so it cannot cite a consultation Dr. Pandey has already handled."],
    ["Not his clinic", "The note is a general model’s wording. It does not follow his style rules or the way he moves from a risk to a test."],
    ["The visit leaves the machine", "The patient text is sent to OpenAI, and each answer is billed in tokens. The twin path is the one built to avoid that."],
    ["A complete tone without his records", "A fluent paragraph can sound finished even when it never opened his case file. That is why it sits beside the twin, not in place of it."],
  ],
};

function PointList({ items, mark }: { items: [string, string][]; mark: "pro" | "con" }) {
  const pro = mark === "pro";
  return (
    <ul className="mt-3 space-y-3">
      {items.map(([title, body]) => (
        <li key={title} className="flex gap-3">
          <span className={`mt-0.5 flex h-6 w-6 shrink-0 items-center justify-center rounded-full text-xs font-semibold ${pro ? "bg-[#172033] text-[#f7f4ef] dark:bg-[#d7c4a3] dark:text-[#172033]" : "bg-[#f3eadf] text-[#8a6a3b] dark:bg-white/10 dark:text-[#d7c4a3]"}`}>
            {pro ? "+" : "–"}
          </span>
          <span>
            <span className="block text-sm font-semibold text-[#172033] dark:text-[#f7f4ef]">{title}</span>
            <span className="mt-1 block text-sm leading-6 text-[#5c5348] dark:text-[#d5e4f0]">{body}</span>
          </span>
        </li>
      ))}
    </ul>
  );
}

function Verdict() {
  return (
    <section className="mt-6 overflow-hidden rounded-[1.8rem] border border-[#eadfd2] bg-white/90 shadow-[0_18px_50px_rgba(23,32,51,0.06)] dark:border-white/10 dark:bg-[#121a2b]/90">
      <div className="bg-[#172033] px-6 py-6 text-[#f7f4ef] md:px-8">
        <p className="text-xs font-semibold uppercase tracking-[0.22em] text-[#d7c4a3]">Verdict</p>
        <h2 className="mt-2 font-display text-2xl font-semibold md:text-3xl">Keep Dr. Pandey’s twin. Use GPT as the second reading.</h2>
        <p className="mt-3 max-w-3xl text-sm leading-7 text-[#e7dfd4]">
          Both answers start from the same visit. The twin is the one that also opens his cases, his graph, and his way of writing a plan. GPT is a clear general note, and it is the weaker fit for this clinic because that note never sees those records.
        </p>
      </div>
      <div className="grid gap-0 lg:grid-cols-2">
        <article className="border-b border-[#eadfd2] bg-[#fbf8f3] p-6 dark:border-white/10 dark:bg-[#172033]/40 md:p-8 lg:border-b-0 lg:border-r">
          <p className="text-xs font-semibold uppercase tracking-[0.18em] text-[#8a6a3b]">Favoured reading</p>
          <h3 className="mt-1 font-display text-2xl font-semibold text-[#172033] dark:text-[#f7f4ef]">Dr. Vimlesh Pandey</h3>
          <p className="mt-2 text-sm leading-6 text-[#5c5348] dark:text-[#d5e4f0]">Llama 3.2, with the retrieved cases and the graph.</p>
          <h4 className="mt-5 text-xs font-semibold uppercase tracking-[0.16em] text-[#8a6a3b]">Why this side leads</h4>
          <PointList items={vimleshPoints.pros} mark="pro" />
          <h4 className="mt-5 text-xs font-semibold uppercase tracking-[0.16em] text-[#8a6a3b]">Where it is thinner</h4>
          <PointList items={vimleshPoints.cons} mark="con" />
        </article>
        <article className="p-6 md:p-8">
          <p className="text-xs font-semibold uppercase tracking-[0.18em] text-[#8a6a3b]">Second reading</p>
          <h3 className="mt-1 font-display text-2xl font-semibold text-[#172033] dark:text-[#f7f4ef]">Ordinary GPT</h3>
          <p className="mt-2 text-sm leading-6 text-[#5c5348] dark:text-[#d5e4f0]">gpt-4o-mini, from this visit only.</p>
          <h4 className="mt-5 text-xs font-semibold uppercase tracking-[0.16em] text-[#8a6a3b]">What it still offers</h4>
          <PointList items={gptPoints.pros} mark="pro" />
          <h4 className="mt-5 text-xs font-semibold uppercase tracking-[0.16em] text-[#8a6a3b]">What it cannot do here</h4>
          <PointList items={gptPoints.cons} mark="con" />
        </article>
      </div>
      <p className="border-t border-[#eadfd2] px-6 py-4 text-xs leading-5 text-[#5c5348] dark:border-white/10 dark:text-[#d5e4f0] md:px-8">
        This verdict is about fit for Dr. Pandey’s records, privacy, and token cost. It is not a measured claim that one answer is the more correct diagnosis.
      </p>
    </section>
  );
}
