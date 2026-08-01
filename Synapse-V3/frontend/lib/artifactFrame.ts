const FIT_STYLE = `<style data-synapse-fit-style>
  html[data-synapse-fit="on"], html[data-synapse-fit="on"] body {
    height: 100%;
    min-height: 100%;
    overflow: hidden !important;
  }
  html[data-synapse-fit="on"] body {
    transform-origin: top left;
    zoom: var(--synapse-fit-scale, 1);
  }
</style>`;

// This runs inside the already sandboxed artifact document. It prevents a
// generated layout from gaining its own scrollbar by shrinking only when its
// natural dimensions exceed the iframe viewport. CSS zoom preserves pointer
// coordinates, so sliders and drag interactions remain usable after fitting.
const FIT_SCRIPT = `<script data-synapse-fit-script>
  (function () {
    function fitArtifact() {
      var root = document.documentElement;
      var body = document.body;
      if (!body) return;

      root.dataset.synapseFit = "on";
      root.style.setProperty("--synapse-fit-scale", "1");
      var contentWidth = Math.max(root.scrollWidth, body.scrollWidth, body.getBoundingClientRect().width);
      var contentHeight = Math.max(root.scrollHeight, body.scrollHeight, body.getBoundingClientRect().height);
      var scale = Math.min(1, window.innerWidth / contentWidth, window.innerHeight / contentHeight);
      root.style.setProperty("--synapse-fit-scale", String(Math.max(0, scale)));
    }

    [0, 100, 500].forEach(function (delay) { window.setTimeout(fitArtifact, delay); });
    window.addEventListener("resize", fitArtifact);
  })();
</script>`;

function injectBeforeClosingTag(html: string, tag: "head" | "body", content: string) {
  const closingTag = new RegExp(`</${tag}\\s*>`, "i");
  if (closingTag.test(html)) return html.replace(closingTag, `${content}</${tag}>`);
  return `${html}${content}`;
}

/**
 * Adds the host-owned viewport fitter to a generated artifact without
 * altering its scientific content or its verified source stored in the app.
 */
export function fitArtifactToFrame(html: string) {
  if (html.includes("data-synapse-fit-style")) return html;
  return injectBeforeClosingTag(
    injectBeforeClosingTag(html, "head", FIT_STYLE),
    "body",
    FIT_SCRIPT
  );
}
