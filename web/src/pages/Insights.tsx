import { Link } from "react-router-dom";
import { Card, PageHeader } from "../components/ui";

const sides = [
  {
    title: "Generic answer",
    body: "Written from this visit alone. It does not search the doctor’s past cases, and it does not walk the graph.",
  },
  {
    title: "Patient-specific twin",
    body: "The same visit, plus similar past cases and the links those records support. Each cited case is a reference, not this patient.",
  },
];

export default function Insights() {
  return (
    <div>
      <PageHeader
        eyebrow="Comparison"
        title="Two ways of answering"
        caption="The difference is what the answer is allowed to see. This page does not rank the models with a score."
      />
      <div className="grid gap-4 md:grid-cols-2">
        {sides.map((side) => (
          <Card key={side.title} className="transition duration-200 hover:-translate-y-0.5 hover:shadow-md">
            <h2 className="text-xl font-semibold">{side.title}</h2>
            <p className="mt-3 text-sm leading-7 text-[#2c4060] dark:text-[#d5e4f0]">{side.body}</p>
          </Card>
        ))}
      </div>
      <Card className="mt-4">
        <h2 className="text-lg font-semibold">What you can say about it</h2>
        <p className="mt-3 text-sm leading-7 text-[#2c4060] dark:text-[#d5e4f0]">
          The twin is built to ground a reply in retrieved records and in graph links that name a case. A smaller local model can run that same path when Ollama is selected. That is a design difference, not a measured win. The four-way comparison on the same 30 held-out cases has not been run here, so this screen does not claim the smaller model is more reliable. A clinician still decides. Detailed counts, when a run exists, stay in the evaluation report and are not shown in the product.
        </p>
        <p className="mt-3 text-sm leading-7 text-[#2c4060] dark:text-[#d5e4f0]">
          Reliability still depends on the records, the retrieval, the model, and a doctor reading the draft. An answer on this site is not a diagnosis.
        </p>
        <Link to="/studio" className="mt-4 inline-block text-sm font-semibold text-[#123a6b] dark:text-[#8eb8e8]">Open the comparison</Link>
      </Card>
    </div>
  );
}
