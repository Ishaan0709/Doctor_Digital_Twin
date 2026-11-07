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
      <PageHeader eyebrow="Compare" title={`Two readings for ${person.name}`} caption="The left answer sees only this visit. The right answer also uses similar cases and the graph. Neither one is a diagnosis." />
      <ModelNote className="mb-4" />
      <div className="grid gap-4 lg:grid-cols-2">
        <Card>
          <p className="text-xs uppercase tracking-[0.18em] text-[#8a6a3b]">This visit only</p>
          <h2 className="mt-1 font-display text-2xl font-semibold">General answer</h2>
          {waitingGeneric ? <Skeleton className="mt-4 h-40" /> : <RichText text={genericText} />}
          {running && waitingGeneric && <p className="mt-3 text-sm text-[#5c5348]">Writing the general answer…</p>}
        </Card>
        <Card>
          <p className="text-xs uppercase tracking-[0.18em] text-[#8a6a3b]">Cases and graph</p>
          <h2 className="mt-1 font-display text-2xl font-semibold">Dr. Pandey’s twin</h2>
          {waitingTwin ? <Skeleton className="mt-4 h-40" /> : <RichText text={twinText} />}
          {running && waitingTwin && <p className="mt-3 text-sm text-[#5c5348]">Writing the twin…</p>}
        </Card>
      </div>
    </div>
  );
}
