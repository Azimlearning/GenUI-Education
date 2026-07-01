import path from "path";
import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  reactStrictMode: true,
  // Pin the workspace root to this folder — otherwise Next.js finds the stray
  // package-lock.json in the user's home directory and watches the whole home
  // tree, which causes spurious dev-server rebuilds and ENOENT races.
  outputFileTracingRoot: path.join(__dirname),
};

export default nextConfig;
