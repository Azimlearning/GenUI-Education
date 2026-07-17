"use client";

import { useState } from "react";

/**
 * The one clear next step (design/FLOW.md sections 1-2). Two placements share the
 * same logic: "hero" is the big front-door prompt, "bar" is the pinned composer
 * once a conversation is going.
 */
export function Composer({
  onSend,
  disabled,
  variant = "bar",
}: {
  onSend: (message: string) => void;
  disabled: boolean;
  variant?: "bar" | "hero";
}) {
  const [value, setValue] = useState("");

  const submit = () => {
    const message = value.trim();
    if (!message || disabled) return;
    setValue("");
    onSend(message);
  };

  const hero = variant === "hero";

  return (
    <form
      className={hero ? "flex items-stretch gap-3" : "flex items-end gap-2.5 pb-5 pt-2"}
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
        placeholder={hero ? "Why does ice float?" : "Ask a science question…"}
        aria-label="Your science question"
        className={`flex-1 resize-none rounded-card border-2 border-line-2 bg-card text-ink outline-none placeholder:text-ink-faint focus:border-primary focus:ring-4 focus:ring-primary-soft ${
          hero
            ? "min-h-[58px] px-5 py-4 text-lg font-semibold"
            : "min-h-[48px] px-4 py-3 text-[15px] font-medium"
        }`}
      />
      <button
        type="submit"
        disabled={disabled || value.trim().length === 0}
        className={`btn btn-primary ${hero ? "px-7 text-base" : "min-h-[48px] px-5 text-[15px]"}`}
      >
        Build it
      </button>
    </form>
  );
}
