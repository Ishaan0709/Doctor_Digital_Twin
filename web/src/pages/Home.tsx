import { useNavigate } from "react-router-dom";
import { Button, Card } from "../components/ui";

const metrics = [
  ["AI Modes", "2", "Generic + Twin"],
  ["Reasoning Layers", "3", "Patient + RAG + GraphRAG"],
  ["Audience", "3", "Teachers, leaders, doctors"],
];

export default function Home() {
  const navigate = useNavigate();
  return (
    <div className="space-y-5">
      <section className="overflow-hidden rounded-3xl border border-slate-200/80 bg-white/70 p-6 shadow-card dark:border-white/10 dark:bg-white/[0.06] md:p-8">
        <div className="grid items-center gap-6 md:grid-cols-[1.4fr_0.8fr]">
          <div>
            <img src="/logo.png" alt="" className="mb-4 h-14 w-14 rounded-2xl object-cover" />
            <h1 className="text-4xl font-semibold tracking-tight">CardioTwin AI</h1>
            <p className="mt-3 max-w-xl text-lg text-slate-600 dark:text-slate-300">Scaling the reasoning of elite cardiologists using AI digital twins.</p>
            <div className="mt-6 flex flex-wrap gap-3">
              <Button variant="primary" onClick={() => navigate("/patient")}>Start Analysis</Button>
              <Button onClick={() => navigate("/consultation")}>Open Consultation Portal</Button>
            </div>
          </div>
          <img src="/doctor_photo.png" alt="Dr. Vimlesh Pandey" className="h-64 w-full rounded-2xl object-cover" />
        </div>
      </section>
      <div className="grid gap-3 md:grid-cols-3">
        {metrics.map(([label, value, hint]) => (
          <Card key={label}>
            <p className="text-sm text-slate-500">{label}</p>
            <p className="text-3xl font-semibold">{value}</p>
            <p className="text-sm text-sky-700 dark:text-sky-200">{hint}</p>
          </Card>
        ))}
      </div>
      <div className="grid gap-3 md:grid-cols-2">
        <Card><h2 className="font-semibold">What problem it solves</h2><p className="mt-2 text-sm text-slate-600 dark:text-slate-300">CardioTwin AI standardizes expert preventive cardiology reasoning into an auditable intelligence layer for high-stakes decision support.</p></Card>
        <Card><h2 className="font-semibold">Why doctors need it</h2><p className="mt-2 text-sm text-slate-600 dark:text-slate-300">It accelerates triage quality, risk interpretation, and follow-up planning while keeping physician judgment central.</p></Card>
        <Card><h2 className="font-semibold">Why hospitals need it</h2><p className="mt-2 text-sm text-slate-600 dark:text-slate-300">It improves consistency, governance visibility, and scalable specialist-aligned care pathways.</p></Card>
        <Card><h2 className="font-semibold">Key features</h2><p className="mt-2 text-sm text-slate-600 dark:text-slate-300">Patient intake, generic consultation, digital twin consultation, historical case intelligence, graph evidence, comparison, and recommendation traceability.</p></Card>
      </div>
    </div>
  );
}
