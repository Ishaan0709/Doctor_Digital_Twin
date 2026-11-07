import { useNavigate } from "react-router-dom";
import { Button } from "../components/ui";

const points = [
  ["Why this exists", "Dr. Vimlesh Pandey cannot be in clinic for every question. CardioTwin carries the cases he recognises and the step he takes from a risk to a plan, so that reading is here between visits."],
  ["What a visit does", "You add your details. The consultation uses those cases and the links between a finding and a next step. Tests, follow-up, and the reason for the reading stay closed until you open them."],
  ["The doctor still decides", "Doctor’s view can accept the draft, edit it, or ask you to come to the clinic when something is serious and the twin should not explain it."],
];

export default function Home() {
  const navigate = useNavigate();
  return (
    <div className="space-y-10">
      <section className="grid items-center gap-10 md:grid-cols-[1.15fr_0.85fr]">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.22em] text-[#8a6a3b]">Dr. Vimlesh Pandey</p>
          <h1 className="mt-3 font-display text-4xl font-semibold leading-tight text-[#172033] dark:text-[#f7f4ef] md:text-5xl">Same doctor. Same expertise. Whenever you need it.</h1>
          <p className="mt-5 max-w-xl text-lg leading-8 text-[#2c4060] dark:text-[#d5e4f0]">
            Consult your doctor’s twin anytime, built on their own knowledge, and get the guidance you need to feel better, sooner. Your doctor still oversees your care.
          </p>
          <p className="mt-4 max-w-xl leading-7 text-[#2c4060] dark:text-[#d5e4f0]">
            The consultation runs on a local model. The 500 cases and the graph stay on this machine, so that longer prompt is not billed as API tokens. Compare places an ordinary GPT answer of the same visit beside it.
          </p>
          <div className="mt-8 flex flex-wrap gap-3">
            <Button className="px-8 py-4 text-base" variant="primary" onClick={() => navigate("/consultation")}>Begin a consultation</Button>
            <Button className="px-8 py-4 text-base" onClick={() => navigate("/compare")}>Compare both answers</Button>
          </div>
        </div>
        <img src="/doctor_photo.jpg?v=3" alt="Dr. Vimlesh Pandey" className="aspect-[4/5] w-full rounded-[2rem] object-cover object-top shadow-[0_30px_80px_rgba(23,32,51,0.18)] ring-1 ring-[#eadfd2]" />
      </section>
      <section className="grid gap-4 md:grid-cols-3">
        {points.map(([title, body]) => (
          <article key={title} className="rounded-[1.6rem] border border-[#eadfd2] bg-white/90 p-6 shadow-[0_18px_50px_rgba(23,32,51,0.05)] dark:border-white/10 dark:bg-[#121a2b]/90">
            <h2 className="font-display text-2xl font-semibold text-[#172033] dark:text-[#f7f4ef]">{title}</h2>
            <p className="mt-3 leading-7 text-[#2c4060] dark:text-[#d5e4f0]">{body}</p>
          </article>
        ))}
      </section>
      <section className="rounded-[2rem] bg-[#172033] px-6 py-10 text-[#f7f4ef] md:px-10">
        <p className="text-xs font-semibold uppercase tracking-[0.22em] text-[#d7c4a3]">Side by side</p>
        <h2 className="mt-2 font-display text-3xl font-semibold">A general answer, next to the Doctor’s Twin.</h2>
        <p className="mt-3 max-w-2xl text-lg leading-8 text-[#e7dfd4]">
          One click writes both. The left answer sees only this visit. The right answer also uses similar cases and the graph. You do not have to run them one page at a time.
        </p>
        <button className="mt-6 rounded-full bg-[#172033] px-8 py-4 text-base font-medium text-[#f7f4ef] transition hover:-translate-y-0.5" onClick={() => navigate("/compare")}>
          Open the comparison
        </button>
      </section>
    </div>
  );
}
