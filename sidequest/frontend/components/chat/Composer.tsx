"use client";

import { useState } from "react";

export function Composer({
  onSend,
  disabled,
}: {
  onSend: (message: string) => void;
  disabled: boolean;
}) {
  const [value, setValue] = useState("");

  const submit = () => {
    const message = value.trim();
    if (!message || disabled) return;
    setValue("");
    onSend(message);
  };

  return (
    <form
      className="study-composer mt-2 flex items-end gap-2 pb-4 pt-3"
      onSubmit={(e) => {
        e.preventDefault();
        submit();
      }}
    >
      <textarea
        value={value}
        onChange={(e) => setValue(e.target.value)}
        onKeyDown={(e) => {
          if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            submit();
          }
        }}
        rows={1}
        maxLength={2000}
        placeholder="Ask a science question…"
        aria-label="Your science question"
        className="min-h-[52px] flex-1 resize-none rounded-xl px-4 py-3 text-[15px] outline-none focus:ring-1"
        style={{
          background: "var(--bg-raised)",
          border: "1px solid var(--rule)",
          color: "var(--ink)",
        }}
      />
      <button
        type="submit"
        disabled={disabled || value.trim().length === 0}
        className="min-h-[52px] min-w-[52px] rounded-xl px-4 text-sm font-medium disabled:opacity-40"
        style={{ background: "var(--accent)", color: "#0d1412" }}
      >
        Study
      </button>
    </form>
  );
}
