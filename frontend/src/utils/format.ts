export const fmtDate = (s: string | null) => (s ? new Date(s).toLocaleDateString() : '—')
export const label = (s: string) => s.replace(/_/g, ' ')
export const pct = (n: number) => `${Math.round(n * 100)}%`
