import ReactMarkdown from "react-markdown";
import { FileText } from "lucide-react";

interface Props {
  markdown: string;
}

export function HldView({ markdown }: Props) {
  return (
    <section className="rounded-2xl border border-white/10 bg-zagi-surface/80 p-6 shadow-card-up">
      <div className="mb-4 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="grid h-8 w-8 place-items-center rounded-lg bg-zagi-neon/10 text-zagi-neon">
            <FileText className="h-4 w-4" />
          </div>
          <div>
            <div className="text-xs font-semibold uppercase tracking-[0.2em] text-zagi-neon">
              Output
            </div>
            <h3 className="text-lg font-semibold text-white">High-Level Design</h3>
          </div>
        </div>
      </div>
      <article className="prose-zagi max-w-none">
        <ReactMarkdown>{markdown}</ReactMarkdown>
      </article>
    </section>
  );
}
