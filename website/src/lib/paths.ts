/** Prefix internal links for GitHub Pages project site (`/Portfolio/`). */
export function withBase(path: string): string {
  const base = import.meta.env.BASE_URL;
  if (path === "/") return base;
  return `${base}${path.replace(/^\//, "")}`;
}

export function currentPath(pathname: string): string {
  const base = import.meta.env.BASE_URL.replace(/\/$/, "");
  if (!base) return pathname;
  const stripped = pathname.startsWith(base) ? pathname.slice(base.length) : pathname;
  return stripped || "/";
}
