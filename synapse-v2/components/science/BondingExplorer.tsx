"use client";

/**
 * Electron bonding explorer — the flagship.
 *
 * v1 classified bonds by looking the elements up in a metal/non-metal set. That
 * gets NaCl right and then quietly lies about HCl, which it calls covalent with
 * no more to say — leaving polar covalent unrepresentable and the whole idea of
 * a bonding *spectrum* invisible.
 *
 * Here classification comes from the Pauling electronegativity difference, which
 * is what actually decides it, and which puts every pair on one scale a student
 * can see and reason about.
 */

import { useState } from "react";
import { Predict, SciencePanel, Verdict, slotArr, slotBool, slotStr, type ScienceProps } from "./shared";

/** Pauling electronegativity. Blanks (noble gases) are deliberately absent. */
const EN: Record<string, number> = {
  H: 2.2, Li: 0.98, Be: 1.57, B: 2.04, C: 2.55, N: 3.04, O: 3.44, F: 3.98,
  Na: 0.93, Mg: 1.31, Al: 1.61, Si: 1.9, P: 2.19, S: 2.58, Cl: 3.16,
  K: 0.82, Ca: 1.0, Sc: 1.36, Ti: 1.54, V: 1.63, Cr: 1.66, Mn: 1.55,
  Fe: 1.83, Co: 1.88, Ni: 1.91, Cu: 1.9, Zn: 1.65, Ga: 1.81, Ge: 2.01,
  As: 2.18, Se: 2.55, Br: 2.96, Rb: 0.82, Sr: 0.95, Ag: 1.93, Sn: 1.96,
  I: 2.66, Ba: 0.89, Pt: 2.28, Au: 2.54, Hg: 2.0, Pb: 2.33,
};

const METALS = new Set([
  "Li","Be","Na","Mg","Al","K","Ca","Sc","Ti","V","Cr","Mn","Fe","Co","Ni","Cu",
  "Zn","Ga","Rb","Sr","Ag","Sn","Ba","Pt","Au","Hg","Pb",
]);

type BondType = "ionic" | "polar-covalent" | "covalent" | "metallic";

interface Analysis {
  type: BondType;
  delta: number;
  donor: string | null;
  acceptor: string | null;
  label: string;
}

/**
 * The classification. Thresholds are the standard teaching boundaries
 * (Δ ≥ 1.7 ionic, 0.4–1.7 polar covalent, < 0.4 covalent) — approximate by
 * nature, which the UI says out loud rather than hiding.
 */
function analyse(a: string, b: string): Analysis | null {
  const ea = EN[a];
  const eb = EN[b];
  if (ea === undefined || eb === undefined) return null;

  const delta = Math.abs(ea - eb);
  const bothMetals = METALS.has(a) && METALS.has(b);

  if (bothMetals) {
    return { type: "metallic", delta, donor: null, acceptor: null, label: "Metallic" };
  }

  const acceptor = ea > eb ? a : b;
  const donor = ea > eb ? b : a;

  if (delta >= 1.7) return { type: "ionic", delta, donor, acceptor, label: "Ionic" };
  if (delta >= 0.4)
    return { type: "polar-covalent", delta, donor, acceptor, label: "Polar covalent" };
  return { type: "covalent", delta, donor: null, acceptor: null, label: "Pure covalent" };
}

export default function BondingExplorer({ slots, onInteraction }: ScienceProps) {
  const showScale = slotBool(slots, "show_electronegativity", true);
  const predictPrompt = slotStr(
    slots,
    "predict_prompt",
    "Will these atoms transfer electrons, or share them?",
  );
  const pairs = slotArr<{ a: string; b: string }>(slots, "pairs", [
    { a: "Na", b: "Cl" },
    { a: "H", b: "Cl" },
    { a: "O", b: "O" },
  ]).filter((p) => p && typeof p.a === "string" && typeof p.b === "string");

  const [index, setIndex] = useState(0);
  const [guess, setGuess] = useState<string | null>(null);
  const [revealed, setRevealed] = useState(false);

  const pair = pairs[Math.min(index, pairs.length - 1)] ?? { a: "Na", b: "Cl" };
  const result = analyse(pair.a, pair.b);

  const reveal = () => {
    if (!guess || !result) return;
    setRevealed(true);
    const predictedType = guess === "transfer" ? "ionic" : "covalent";
    const actualFamily = result.type === "ionic" ? "ionic" : "covalent";
    onInteraction?.("revealed the bond type", {
      pair: `${pair.a}-${pair.b}`,
      predicted: guess,
      actual: result.type,
      electronegativity_difference: Number(result.delta.toFixed(2)),
      correct: predictedType === actualFamily,
    });
  };

  const next = () => {
    setIndex((i) => (i + 1) % pairs.length);
    setGuess(null);
    setRevealed(false);
  };

  if (!result) {
    return (
      <SciencePanel title="Electron bonding explorer" subject="chemistry">
        <p className="sci-status">
          No electronegativity data for {pair.a}–{pair.b}. Try a main-group pair such as Na–Cl.
        </p>
      </SciencePanel>
    );
  }

  return (
    <SciencePanel
      title="Electron bonding explorer"
      subject="chemistry"
      badge={`${pair.a} + ${pair.b}`}
    >
      <BondView pair={pair} result={result} revealed={revealed} />

      {showScale ? <ENScale a={pair.a} b={pair.b} delta={result.delta} revealed={revealed} /> : null}

      {!revealed ? (
        <>
          <Predict
            prompt={predictPrompt}
            options={[
              { id: "transfer", label: "Transfer (one atom takes)" },
              { id: "share", label: "Share (both hold)" },
            ]}
            chosen={guess}
            onChoose={setGuess}
          />
          <button className="btn-primary" disabled={!guess} onClick={reveal}>
            {guess ? "Show me the electrons" : "Predict first"}
          </button>
        </>
      ) : (
        <>
          <Verdict
            correct={
              (guess === "transfer" && result.type === "ionic") ||
              (guess === "share" && result.type !== "ionic")
            }
          >
            <BondExplanation pair={pair} result={result} />
          </Verdict>
          {pairs.length > 1 ? (
            <button className="btn-secondary" onClick={next}>
              Next pair ({pairs[(index + 1) % pairs.length].a}–{pairs[(index + 1) % pairs.length].b})
            </button>
          ) : null}
        </>
      )}
    </SciencePanel>
  );
}

function BondExplanation({ pair, result }: { pair: { a: string; b: string }; result: Analysis }) {
  const d = result.delta.toFixed(2);
  if (result.type === "metallic") {
    return (
      <>
        Both {pair.a} and {pair.b} are metals, so neither has a strong pull on electrons. They
        pool their outer electrons into a shared sea that flows between fixed positive ions — which
        is exactly why metals conduct and can be hammered flat without shattering.
      </>
    );
  }
  if (result.type === "ionic") {
    return (
      <>
        The electronegativity difference is <strong>{d}</strong>, at or above 1.7, so this is{" "}
        <strong>ionic</strong>. {result.acceptor} pulls hard enough to take the electron outright
        from {result.donor}: you get {result.donor}<sup>+</sup> and {result.acceptor}<sup>−</sup>,
        held by the attraction between opposite charges. No sharing happens here at all.
      </>
    );
  }
  if (result.type === "polar-covalent") {
    return (
      <>
        Difference of <strong>{d}</strong> — between 0.4 and 1.7, so this is{" "}
        <strong>polar covalent</strong>, and this is the case textbooks flatten. The electrons are{" "}
        <em>shared</em>, so it is covalent. But {result.acceptor} pulls harder, so the pair sits
        closer to it, giving it a partial negative charge (δ−) and leaving {result.donor} partially
        positive (δ+). Not a transfer, not an even share. Bonding is a spectrum, and this pair sits
        in the middle of it.
      </>
    );
  }
  return (
    <>
      The difference is <strong>{d}</strong>, below 0.4, so this is a{" "}
      <strong>pure covalent</strong> bond. Both atoms pull on the shared pair about equally, so the
      electrons sit midway between them and neither end carries a partial charge.
    </>
  );
}

/* ------------------------------------------------------------- visuals */

function BondView({
  pair,
  result,
  revealed,
}: {
  pair: { a: string; b: string };
  result: Analysis;
  revealed: boolean;
}) {
  // Where the shared pair sits: dead centre for pure covalent, pulled toward
  // the more electronegative atom as Δ grows, fully transferred when ionic.
  const bias = result.type === "ionic" ? 1 : Math.min(1, result.delta / 1.7) * 0.35;
  const toB = result.acceptor === pair.b;
  const offset = revealed ? (toB ? bias : -bias) * 30 : 0;

  return (
    <div className="bondview">
      <Atom symbol={pair.a} charge={revealed && result.type === "ionic" ? (result.donor === pair.a ? "+" : "−") : null} />

      <div className="bond-gap">
        {result.type === "metallic" ? (
          <span className="bond-sea">{revealed ? "e⁻ sea" : ""}</span>
        ) : (
          <>
            <span
              className={`bond-pair${revealed ? " is-revealed" : ""}`}
              style={{ transform: `translateX(${offset}px)` }}
            >
              <span className="e-dot" />
              <span className="e-dot" />
            </span>
            {revealed && result.type === "polar-covalent" ? (
              <span className="bond-delta">
                <em style={{ left: 0 }}>δ{toB ? "+" : "−"}</em>
                <em style={{ right: 0 }}>δ{toB ? "−" : "+"}</em>
              </span>
            ) : null}
          </>
        )}
        {revealed ? <span className="bond-label">{result.label}</span> : null}
      </div>

      <Atom symbol={pair.b} charge={revealed && result.type === "ionic" ? (result.donor === pair.b ? "+" : "−") : null} />
    </div>
  );
}

function Atom({ symbol, charge }: { symbol: string; charge: string | null }) {
  return (
    <div className="atom">
      <span className="atom-symbol">{symbol}</span>
      {charge ? <span className="atom-charge">{charge}</span> : null}
      <span className="atom-en">EN {EN[symbol]?.toFixed(2) ?? "?"}</span>
    </div>
  );
}

/** The spectrum, drawn. The point is that the thresholds are regions, not walls. */
function ENScale({
  a,
  b,
  delta,
  revealed,
}: {
  a: string;
  b: string;
  delta: number;
  revealed: boolean;
}) {
  const pct = Math.min(100, (delta / 3.2) * 100);
  return (
    <figure className="enscale">
      <figcaption>Electronegativity difference (Δ)</figcaption>
      <div className="enscale-bar">
        <span className="enscale-zone" style={{ width: "12.5%" }}>covalent</span>
        <span className="enscale-zone is-polar" style={{ width: "40.6%" }}>polar covalent</span>
        <span className="enscale-zone is-ionic" style={{ width: "46.9%" }}>ionic</span>
        {revealed ? (
          <span className="enscale-marker" style={{ left: `${pct}%` }}>
            <b>{delta.toFixed(2)}</b>
          </span>
        ) : null}
      </div>
      <p className="enscale-note">
        {a}–{b}. Thresholds (0.4, 1.7) are teaching conventions, not hard walls — real bonds shade
        into each other.
      </p>
    </figure>
  );
}
