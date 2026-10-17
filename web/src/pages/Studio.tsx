import { Link } from "react-router-dom";
import { toast } from "sonner";
import { PatientForm } from "../components/PatientForm";
import { Card } from "../components/ui";
import { demoPatient } from "../types";
import { useAppStore } from "../store/useAppStore";

const rooms = [
  ["/generic", "Generic GPT", "The general answer, written from this patient only."],
  ["/twin", "Doctor's Twin", "The same patient, read with this doctor's cases and graph."],
  ["/compare", "Side by side", "Both consultations on one page."],
  ["/graph", "The graph", "The links this run actually used."],
  ["/why", "Why this plan", "Cases, uniqueness, and the confidence number."],
  ["/insights", "The scores", "Which side leads on each factor, and why."],
];

export default function Studio() {
  const patient = useAppStore((s) => s.patient);
  const saveIntake = useAppStore((s) => s.savePortalIntake);
  return (
    <div>
      <p className="text-sm font-semibold uppercase tracking-[0.16em] text-[#123a6b] dark:text-[#8eb8e8]">Comparison</p>
      <h1 className="mt-2 max-w-3xl text-4xl font-semibold leading-tight text-[#0b1f3a] dark:text-white md:text-5xl">Two consultations. Then the difference.</h1>
      <p className="mt-4 max-w-2xl text-lg leading-8 text-[#2c4060] dark:text-[#d5e4f0]">
        Add this patient the same way as a consultation. Use the sample if you want a filled visit, or type your own. Then open each answer, the graph, and the scores.
      </p>
      <Card className="mt-6">
        <h2 className="text-xl font-semibold">{patient ? `Details for ${patient.name}` : "This patient's details"}</h2>
        <p className="mt-1 text-sm text-[#3d5270] dark:text-[#c9d7ea]">Use demo patient fills a sample visit. Save before you open the pages below.</p>
        <div className="mt-4">
          <PatientForm
            initial={patient || demoPatient}
            mode="analysis"
            submitLabel="Save these details"
            onSubmit={(next) => {
              saveIntake(next);
              toast.success("Details saved. Open any comparison page.");
            }}
          />
        </div>
      </Card>
      <div className="mt-8 grid gap-4 md:grid-cols-2">
        {rooms.map(([to, title, body]) => (
          <Link key={to} to={to} className="rounded-2xl border border-[#c9daee] bg-white p-5 transition hover:-translate-y-0.5 dark:border-white/10 dark:bg-[#102038]">
            <h2 className="text-2xl font-semibold">{title}</h2>
            <p className="mt-2 text-sm leading-6 text-[#2c4060] dark:text-[#d5e4f0]">{body}</p>
          </Link>
        ))}
      </div>
    </div>
  );
}
