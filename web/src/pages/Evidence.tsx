import { useNavigate } from "react-router-dom";
import { Button, Card, Note, PageHeader } from "../components/ui";

const cards = [
  ["/cases", "Historical Case Intelligence", "Review similar specialist cases, diagnosis patterns, decisions, and outcomes.", "Open Historical Cases"],
  ["/graph", "Graph Intelligence", "Inspect relationships that connect symptoms, risks, tests, and decisions.", "Open Graph Intelligence"],
  ["/why", "Why This Recommendation", "Understand confidence, evidence traceability, and the recommendation rationale.", "Open Explainability"],
];

export default function Evidence() {
  const navigate = useNavigate();
  return (
    <div>
      <PageHeader eyebrow="5 · Evidence" title="Evidence Center" caption="Three focused screens: historical cases, graph intelligence, and why this recommendation." />
      <Note title="Evidence Center">Each evidence type stays on its own screen so the reasoning is easier to follow.</Note>
      <div className="grid gap-4 md:grid-cols-3">
        {cards.map(([to, title, body, action]) => (
          <Card key={to}>
            <h2 className="font-semibold">{title}</h2>
            <p className="mt-2 text-sm text-slate-600 dark:text-slate-300">{body}</p>
            <Button className="mt-4" onClick={() => navigate(to)}>{action}</Button>
          </Card>
        ))}
      </div>
    </div>
  );
}
