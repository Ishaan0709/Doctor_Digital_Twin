import type { ReactNode } from "react";
import { parseConsultation, type RichBlock } from "../lib/richText";

function inline(text: string, key: string): ReactNode[] {
  const nodes: ReactNode[] = [];
  const pattern = /\*\*([^*]+)\*\*/g;
  let last = 0;
  let match: RegExpExecArray | null;
  let count = 0;
  while ((match = pattern.exec(text))) {
    if (match.index > last) nodes.push(text.slice(last, match.index));
    nodes.push(
      <strong key={`${key}-${count}`} className="font-semibold text-slate-900 dark:text-white">
        {match[1]}
      </strong>,
    );
    count += 1;
    last = match.index + match[0].length;
  }
  const rest = text.slice(last);
  const open = rest.indexOf("**");
  if (open >= 0 && (rest.split("**").length - 1) % 2 === 1) {
    if (open > 0) nodes.push(rest.slice(0, open));
    const tail = rest.slice(open + 2);
    if (tail) {
      nodes.push(
        <strong key={`${key}-open`} className="font-semibold text-slate-900 dark:text-white">
          {tail}
        </strong>,
      );
    }
  } else if (rest) {
    nodes.push(rest);
  }
  return nodes;
}

function ItemText({ text, id }: { text: string; id: string }) {
  const labeled = text.match(/^\*\*([^*]+)\*\*:?\s*([\s\S]*)$/);
  if (!labeled) return <span>{inline(text, id)}</span>;
  const label = labeled[1].replace(/:$/, "");
  const rest = labeled[2].trim();
  if (!rest) return <span className="font-semibold text-slate-900 dark:text-white">{label}</span>;
  if (rest.length > 48) {
    return (
      <span className="block">
        <span className="font-semibold text-slate-900 dark:text-white">{label}</span>
        <span className="mt-0.5 block">{inline(rest, `${id}-rest`)}</span>
      </span>
    );
  }
  return (
    <span>
      <strong className="font-semibold text-slate-900 dark:text-white">{label}:</strong> {inline(rest, `${id}-rest`)}
    </span>
  );
}

function Blocks({ blocks }: { blocks: RichBlock[] }) {
  return (
    <>
      {blocks.map((block, index) => {
        if (block.type === "heading") {
          return (
            <h3 key={index} className="text-[15px] font-semibold text-slate-900 dark:text-white">
              {block.text}
            </h3>
          );
        }
        if (block.type === "paragraph") {
          return <p key={index}>{inline(block.text, `p${index}`)}</p>;
        }
        const ListTag = block.ordered ? "ol" : "ul";
        return (
          <ListTag
            key={index}
            className={block.ordered ? "list-decimal space-y-2 pl-5 marker:font-semibold marker:text-sky-600 dark:marker:text-sky-300" : "list-disc space-y-1.5 pl-5 marker:text-sky-600 dark:marker:text-sky-300"}
          >
            {block.items.map((item, itemIndex) => (
              <li key={itemIndex} className="pl-1">
                <ItemText text={item.text} id={`li${index}-${itemIndex}`} />
                {item.nested.length > 0 && (
                  <div className="mt-1">
                    <Blocks blocks={item.nested} />
                  </div>
                )}
              </li>
            ))}
          </ListTag>
        );
      })}
    </>
  );
}

export function RichText({ text, streaming = false, className = "mt-3" }: { text: string; streaming?: boolean; className?: string }) {
  if (!text.trim()) return null;
  return (
    <div className={`space-y-2.5 text-sm leading-7 text-slate-700 dark:text-slate-200 ${className}`}>
      <Blocks blocks={parseConsultation(text)} />
      {streaming && <span className="ml-1 inline-block h-3 w-1 animate-pulse bg-sky-500" />}
    </div>
  );
}

export function InlineText({ text }: { text: string }) {
  return <>{inline(text, "inline")}</>;
}
