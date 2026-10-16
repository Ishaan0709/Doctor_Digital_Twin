import { useNavigate } from "react-router-dom";
import { toast } from "sonner";
import { PatientForm } from "../components/PatientForm";
import { Card, Note, PageHeader } from "../components/ui";
import { analysisDefaults } from "../types";
import { useAppStore } from "../store/useAppStore";

export default function PatientAnalysis() {
  const patient = useAppStore((s) => s.patient);
  const setPatient = useAppStore((s) => s.setPatient);
  const navigate = useNavigate();
  return (
    <div>
      <PageHeader eyebrow="1 · Intake" title="Patient Intake" caption="Enter current patient context for this consultation run." />
      <Note title="What this page means">This is the live input for the current analysis session. It is not automatically an existing patient file of Dr. Pandey unless the entered details match a historical case.</Note>
      <Card>
        <PatientForm
          initial={patient || analysisDefaults}
          mode="analysis"
          submitLabel="Analyze Patient"
          onSubmit={(next) => {
            setPatient(next);
            toast.success("Patient profile saved.");
            navigate("/generic");
          }}
        />
      </Card>
    </div>
  );
}
