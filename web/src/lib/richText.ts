export type RichBlock =
  | { type: "heading"; text: string }
  | { type: "paragraph"; text: string }
  | { type: "list"; ordered: boolean; items: RichItem[] };

export type RichItem = { text: string; nested: RichBlock[] };

const HEADING = /^\*\*([^*]+)\*\*:?\s*$/;
const BULLET = /^[-*•]\s+(.*)$/;
const NUMBER = /^\d+[.)]\s+(.*)$/;

function indentWidth(line: string): number {
  return (line.match(/^[ \t]*/)?.[0] ?? "").replace(/\t/g, "  ").length;
}

function isHeading(text: string): boolean {
  return HEADING.test(text);
}

function marker(text: string, ordered: boolean): string | null {
  const match = text.match(ordered ? NUMBER : BULLET);
  return match ? match[1].trim() : null;
}

export function parseConsultation(source: string): RichBlock[] {
  const lines = source.replace(/\r\n/g, "\n").replace(/\r/g, "\n").split("\n");
  return readBlocks(lines, 0).blocks;
}

function readBlocks(lines: string[], minIndent: number): { blocks: RichBlock[]; consumed: number } {
  const blocks: RichBlock[] = [];
  let i = 0;

  while (i < lines.length) {
    if (!lines[i].trim()) {
      i += 1;
      continue;
    }
    if (indentWidth(lines[i]) < minIndent) break;

    const trimmed = lines[i].trim();
    if (BULLET.test(trimmed) || NUMBER.test(trimmed)) {
      const ordered = NUMBER.test(trimmed);
      const markerIndent = indentWidth(lines[i]);
      const items: RichItem[] = [];

      while (i < lines.length) {
        if (!lines[i].trim()) {
          let next = i + 1;
          while (next < lines.length && !lines[next].trim()) next += 1;
          if (next >= lines.length) {
            i = next;
            break;
          }
          const nextText = lines[next].trim();
          const nextIndent = indentWidth(lines[next]);
          const continues = nextIndent > markerIndent || (marker(nextText, ordered) !== null && nextIndent === markerIndent);
          if (!continues || isHeading(nextText)) break;
          i = next;
          continue;
        }

        const indent = indentWidth(lines[i]);
        if (indent < markerIndent) break;
        const text = lines[i].trim();
        if (isHeading(text)) break;

        const sameItem = marker(text, ordered);
        if (sameItem !== null && indent === markerIndent) {
          items.push({ text: sameItem, nested: [] });
          i += 1;
          continue;
        }
        if (indent === markerIndent && (BULLET.test(text) || NUMBER.test(text))) break;

        if (!items.length) break;

        if (indent > markerIndent && (BULLET.test(text) || NUMBER.test(text))) {
          const nestedIndent = indent;
          const start = i;
          i += 1;
          while (i < lines.length) {
            if (!lines[i].trim()) {
              let next = i + 1;
              while (next < lines.length && !lines[next].trim()) next += 1;
              if (next >= lines.length || indentWidth(lines[next]) < nestedIndent) break;
              i += 1;
              continue;
            }
            if (indentWidth(lines[i]) < nestedIndent) break;
            i += 1;
          }
          items[items.length - 1].nested.push(...readBlocks(lines.slice(start, i), nestedIndent).blocks);
          continue;
        }

        items[items.length - 1].text = `${items[items.length - 1].text} ${text}`.trim();
        i += 1;
      }

      blocks.push({ type: "list", ordered, items });
      continue;
    }

    const heading = trimmed.match(HEADING);
    if (heading) {
      blocks.push({ type: "heading", text: heading[1].replace(/:$/, "") });
      i += 1;
      continue;
    }

    const parts = [trimmed];
    i += 1;
    while (i < lines.length && lines[i].trim()) {
      const text = lines[i].trim();
      if (indentWidth(lines[i]) < minIndent || BULLET.test(text) || NUMBER.test(text) || isHeading(text)) break;
      parts.push(text);
      i += 1;
    }
    blocks.push({ type: "paragraph", text: parts.join(" ") });
  }

  return { blocks, consumed: i };
}
