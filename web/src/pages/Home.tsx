import { useNavigate } from "react-router-dom";
import { Button } from "../components/ui";

export default function Home() {
  const navigate = useNavigate();
  return (
    <div className="space-y-10">
      <section className="grid items-center gap-10 md:grid-cols-[1.15fr_0.85fr]">
        <div>
          <p className="text-sm font-semibold uppercase tracking-[0.16em] text-[#123a6b] dark:text-[#8eb8e8]">Dr. Vimlesh Pandey</p>
          <h1 className="mt-3 text-4xl font-semibold leading-tight text-[#0b1f3a] dark:text-white md:text-5xl">Same doctor. Same expertise. Whenever you need it.</h1>
          <p className="mt-5 max-w-xl text-lg leading-8 text-[#2c4060] dark:text-[#d5e4f0]">
            Consult your doctor’s twin anytime, built on their own knowledge, and get the guidance you need to feel better, sooner. Your doctor still oversees your care.
          </p>
          <Button className="mt-8" variant="primary" onClick={() => navigate("/patient")}>Begin a consultation</Button>
        </div>
        <img src="/doctor_photo.jpg?v=3" alt="Dr. Vimlesh Pandey" className="aspect-[4/5] w-full rounded-[2rem] object-cover object-top" />
      </section>
      <section className="rounded-[2rem] bg-[#e7f1fb] px-6 py-8 text-[#0b1f3a] md:px-10 dark:bg-[#16345c] dark:text-[#e7f0fa]">
        <p className="text-sm font-semibold uppercase tracking-[0.16em] text-[#123a6b] dark:text-[#9ec4ef]">Side by side</p>
        <h2 className="mt-2 text-3xl font-semibold text-[#0b1f3a] dark:text-white">A general answer, next to the Doctor’s Twin.</h2>
        <p className="mt-3 max-w-2xl text-[#1a4a7a] dark:text-[#d5e4f0]">
          Your consultation stays on your own visit. Open the comparison to place a general AI answer beside the Doctor’s Twin, with the graph and a short reason for each score.
        </p>
        <button className="mt-6 rounded-full bg-[#123a6b] px-6 py-3 text-base font-semibold text-white hover:bg-[#0c2d56]" onClick={() => navigate("/studio")}>
          Open the comparison
        </button>
      </section>
    </div>
  );
}
