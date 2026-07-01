"use client";

// Teacher view (hackAstone commercial-viability wedge): per-student diagnosed misconceptions,
// mastery, and what's due for review. This is the B2B2C hook — teachers and schools adopt it
// because they can see, at a glance, where a class is stuck. Reads GET /api/teacher.

import { useEffect, useState } from "react";
import type { CSSProperties } from "react";

import { fetchTeacher, type LearnerProfile } from "@/lib/client";

export default function TeacherPage() {
  const [students, setStudents] = useState<LearnerProfile[] | null>(null);

  useEffect(() => {
    void fetchTeacher().then(setStudents);
  }, []);

  return (
    <>
      <header style={topbar}>
        <a href="/" style={{ fontSize: 20, fontWeight: 800, color: "var(--indigo)", textDecoration: "none" }}>
          Synap<span style={{ color: "var(--teal)" }}>se</span>
        </a>
        <a href="/" style={{ marginLeft: "auto", fontSize: 13, color: "var(--indigo)", fontWeight: 700, textDecoration: "none" }}>
          ← Student view
        </a>
      </header>

      <main style={wrap}>
        <h1 style={{ fontSize: 26, fontWeight: 800, margin: "0 0 4px" }}>Teacher dashboard</h1>
        <p style={{ color: "var(--slate)", fontSize: 14, marginTop: 0 }}>
          Every learner Synapse has diagnosed, their mastery per topic, and what is due for spaced-repetition review.
        </p>

        {students === null && <p style={{ color: "var(--slate)" }}>Loading…</p>}
        {students !== null && students.length === 0 && (
          <div style={emptyBox}>
            No learners yet. Open the <a href="/" style={{ color: "var(--indigo)" }}>student view</a>, answer a
            question, and interact with the composed activity — the class will appear here.
          </div>
        )}

        <div style={{ display: "flex", flexDirection: "column", gap: 14, marginTop: 16 }}>
          {students?.map((s) => (
            <div key={s.student_id} style={cardStyle}>
              <div style={{ display: "flex", alignItems: "baseline", gap: 10 }}>
                <div style={{ fontWeight: 800, color: "var(--indigo)" }}>{s.student_id}</div>
                {s.due_now.length > 0 && (
                  <span style={{ fontSize: 12, color: "var(--amber)", fontWeight: 700 }}>
                    {s.due_now.length} due for review
                  </span>
                )}
              </div>

              <div style={{ marginTop: 8, display: "flex", flexDirection: "column", gap: 6 }}>
                {Object.entries(s.mastery).map(([topic, m]) => (
                  <div key={topic} style={{ display: "flex", alignItems: "center", gap: 10 }}>
                    <span style={{ width: 160, fontSize: 12.5, textTransform: "capitalize" }}>{topic}</span>
                    <div style={{ flex: 1, height: 9, background: "#f1f5f9", borderRadius: 6, overflow: "hidden" }}>
                      <div style={{ width: `${Math.round(m * 100)}%`, height: "100%", background: m >= 0.6 ? "#16a34a" : "var(--teal)" }} />
                    </div>
                    <span style={{ width: 38, textAlign: "right", fontSize: 12, color: "var(--slate)" }}>{Math.round(m * 100)}%</span>
                  </div>
                ))}
                {Object.keys(s.mastery).length === 0 && (
                  <span style={{ fontSize: 12.5, color: "var(--slate)" }}>No graded interactions yet.</span>
                )}
              </div>

              {s.misconceptions.length > 0 && (
                <div style={{ marginTop: 10, fontSize: 12.5 }}>
                  <span style={{ color: "var(--slate)" }}>Misconceptions: </span>
                  {s.misconceptions.map((mc) => (
                    <span key={mc.misconception_id} style={{ display: "inline-block", margin: "2px 4px 2px 0", padding: "3px 9px", borderRadius: 20, background: mc.resolved ? "#e9f9ee" : "#fff7ed", color: mc.resolved ? "#16a34a" : "var(--amber)" }}>
                      {mc.misconception_id} {mc.resolved ? "✓" : "· in review"}
                    </span>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
      </main>
    </>
  );
}

const topbar: CSSProperties = { background: "var(--white)", borderBottom: "1px solid var(--line)", padding: "14px 28px", display: "flex", alignItems: "center", gap: 12, position: "sticky", top: 0, zIndex: 50 };
const wrap: CSSProperties = { maxWidth: 820, margin: "0 auto", padding: "32px 24px 80px" };
const cardStyle: CSSProperties = { background: "var(--white)", border: "1px solid var(--line)", borderRadius: 14, boxShadow: "var(--shadow)", padding: 18 };
const emptyBox: CSSProperties = { marginTop: 16, padding: 16, borderRadius: 12, border: "1px dashed var(--line)", color: "var(--slate)", fontSize: 14 };
