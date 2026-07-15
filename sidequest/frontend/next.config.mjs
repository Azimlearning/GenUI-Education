const API_BASE = process.env.API_BASE_INTERNAL ?? "http://localhost:8000";

/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  headers: async () => [
    {
      // App-level CSP (SECURITY.md section 2.4). The artifact CSP is separate
      // and injected into artifact HTML by the backend post-processor.
      source: "/:path*",
      headers: [{ key: "Content-Security-Policy", value: "frame-ancestors 'self'" }],
    },
  ],
  rewrites: async () => [
    // A srcdoc iframe resolves relative URLs against the parent's base URL,
    // so generated code asking for /vendor/p5.min.js hits the frontend origin,
    // not the backend. Proxy the path so the vendored libraries really are
    // same-origin from the artifact's point of view (TECHNICAL.md section 5).
    { source: "/vendor/:path*", destination: `${API_BASE}/vendor/:path*` },
  ],
};

export default nextConfig;
