/**
 * The saved-labs library: verified artifacts persisted in localStorage so a
 * student (or a demo) can reopen an experiment without re-running the
 * pipeline. Regeneration costs real tokens; reopening a saved lab costs
 * nothing. The HTML stored here has already passed the Verifier and the
 * post-processor, and it still renders through the same sandboxed iframe,
 * so saving does not create a second, weaker delivery path.
 */
import { z } from "zod";

import { MetaSchema } from "@/types/events";

const KEY = "synapse-labs";
const MAX_LABS = 20;
// localStorage quota is ~5MB; artifacts are capped at 300KB each server-side.
const MAX_TOTAL_CHARS = 3_500_000;

const SavedLabSchema = z.object({
  id: z.string(),
  title: z.string(),
  question: z.string(),
  html: z.string(),
  meta: MetaSchema.nullable(),
  // Older saved labs predate the flag; treat them as verified.
  verified: z.boolean().default(true),
  savedAt: z.number(),
});

export type SavedLab = z.infer<typeof SavedLabSchema>;

export function listSavedLabs(): SavedLab[] {
  try {
    const raw = localStorage.getItem(KEY);
    if (!raw) return [];
    const parsed = z.array(SavedLabSchema).safeParse(JSON.parse(raw));
    return parsed.success ? parsed.data : [];
  } catch {
    return [];
  }
}

/** Write newest-first, evicting from the tail until the list fits both the
 *  count cap and the quota. Returns what actually got persisted. */
function persist(labs: SavedLab[]): SavedLab[] {
  let list = labs.slice(0, MAX_LABS);
  while (list.length > 0) {
    const raw = JSON.stringify(list);
    if (raw.length <= MAX_TOTAL_CHARS) {
      try {
        localStorage.setItem(KEY, raw);
        return list;
      } catch {
        /* quota exceeded: fall through and evict one more */
      }
    }
    list = list.slice(0, -1);
  }
  try {
    localStorage.removeItem(KEY);
  } catch {
    /* storage unavailable (private mode): the session just isn't persistent */
  }
  return [];
}

export function saveLab(lab: SavedLab): SavedLab[] {
  const rest = listSavedLabs().filter((existing) => existing.id !== lab.id);
  return persist([lab, ...rest]);
}

export function removeLab(id: string): SavedLab[] {
  return persist(listSavedLabs().filter((existing) => existing.id !== id));
}
