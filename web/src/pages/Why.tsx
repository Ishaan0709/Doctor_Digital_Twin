import { Link, useNavigate } from "react-router-dom";
import { BulletList, Button, Card, Confidence, PageHeader } from "../components/ui";
import { useAppStore } from "../store/useAppStore";

export default function Why() {
  const twin = useAppStore((s) => s.twinResult);
  const navigate = useNavigate();
  if (!twin) return <Card><p>Please generate the twin consultation first.</p><Link to="/twin" className="text-sky-600">Open the twin</Link></Card>;
  return (
    <div>
      <PageHeader eyebrow="9 · Why" title="Why This Recommendation" caption="Evidence traceability and the confidence view." />
      <Card className="mb-4"><p className="text-sm">This page explains why the recommendation was generated: historical evidence, patient-specific modifiers, safety checks, and final confidence.</p></Card>
      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <h2 className="font-semibold">Retrieved historical signals</h2>
          <ul className="mt-3 space-y-2 text-sm">
            {twin.historical_patterns?.map((item) => <li key={String(item.case_id)}>Case {item.case_id}: {item.diagnosis} → {item.outcome}</li>)}
          </ul>
        </Card>
        <Card>
          <h2 className="font-semibold">Differences from matched cases</h2>
          <BulletList items={["Current symptoms and risk markers are prioritized over historical templates.", "Medication context and present labs reshape urgency and testing pathways."]} />
        </Card>
        <Card>
          <h2 className="font-semibold">Contraindication checks</h2>
          <BulletList items={["Medication overlap is reviewed for bleeding and renal safety concerns.", "Escalation advice is linked to symptom worsening and red-flag patterns."]} />
        </Card>
      </div>
      <div className="mt-4"><Confidence result={twin} /></div>
      <div className="mt-4 flex flex-wrap gap-3">
        <Button variant="primary" onClick={() => navigate("/explain")}>Open Full Explainability Report</Button>
        <Button onClick={() => navigate("/admin")}>Open Admin / Dataset</Button>
      </div>
    </div>
  );
}
