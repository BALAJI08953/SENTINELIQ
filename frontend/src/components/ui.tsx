import type { ReactNode } from 'react'
import { AlertCircle, Inbox, Loader2 } from 'lucide-react'
import type { Priority } from '../types'

export const Card = ({ title, children, right }: { title?: string; children: ReactNode; right?: ReactNode }) => (
  <section className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
    {(title || right) && <div className="mb-3 flex items-center justify-between"><h2 className="font-semibold text-slate-800">{title}</h2>{right}</div>}
    {children}
  </section>
)
export const Stat = ({ name, value, tone }: { name: string; value: number | string; tone?: string }) => (
  <div className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
    <div className="text-xs uppercase tracking-wide text-slate-500">{name}</div>
    <div className={`mt-1 text-2xl font-bold ${tone ?? 'text-slate-900'}`}>{value}</div>
  </div>
)
const PRIO: Record<Priority, string> = { low: 'bg-slate-100 text-slate-700', medium: 'bg-amber-100 text-amber-800', high: 'bg-orange-100 text-orange-800', critical: 'bg-red-100 text-red-800' }
export const PriorityBadge = ({ p }: { p: Priority }) => <span className={`rounded px-2 py-0.5 text-xs font-medium ${PRIO[p]}`}>{p}</span>
export const Tag = ({ children, tone = 'bg-slate-100 text-slate-700' }: { children: ReactNode; tone?: string }) => <span className={`rounded px-2 py-0.5 text-xs ${tone}`}>{children}</span>
export const DemoTag = ({ demo }: { demo: boolean }) => demo ? <Tag tone="bg-violet-100 text-violet-800">demo (fictional)</Tag> : null
export const Loading = () => <div className="flex items-center gap-2 p-6 text-slate-500"><Loader2 className="h-4 w-4 animate-spin" />Loading…</div>
export const ErrorBox = ({ message }: { message: string }) => <div role="alert" className="flex items-center gap-2 rounded border border-red-200 bg-red-50 p-3 text-sm text-red-700"><AlertCircle className="h-4 w-4" />{message}</div>
export const Empty = ({ title, hint }: { title: string; hint?: string }) => (
  <div className="flex flex-col items-center gap-1 p-8 text-center text-slate-500"><Inbox className="h-6 w-6" /><div className="font-medium text-slate-700">{title}</div>{hint && <div className="text-sm">{hint}</div>}</div>
)
export const Button = ({ children, ...p }: React.ButtonHTMLAttributes<HTMLButtonElement>) => (
  <button {...p} className={`rounded bg-slate-900 px-3 py-1.5 text-sm text-white hover:bg-slate-700 disabled:opacity-50 ${p.className ?? ''}`}>{children}</button>
)
export const Input = (p: React.InputHTMLAttributes<HTMLInputElement>) => <input {...p} className={`rounded border border-slate-300 px-2 py-1.5 text-sm ${p.className ?? ''}`} />
export function Pager({ total, offset, limit, onChange }: { total: number; offset: number; limit: number; onChange: (o: number) => void }) {
  if (total <= limit) return null
  return (
    <div className="mt-3 flex items-center justify-between text-sm text-slate-600">
      <span>{offset + 1}–{Math.min(offset + limit, total)} of {total}</span>
      <div className="flex gap-2">
        <Button disabled={offset === 0} onClick={() => onChange(Math.max(0, offset - limit))}>Previous</Button>
        <Button disabled={offset + limit >= total} onClick={() => onChange(offset + limit)}>Next</Button>
      </div>
    </div>
  )
}
export function Async<T>({ state, children }: { state: { data: T | null; loading: boolean; error: string | null }; children: (d: T) => ReactNode }) {
  if (state.loading && !state.data) return <Loading />
  if (state.error) return <ErrorBox message={state.error} />
  return state.data ? <>{children(state.data)}</> : null
}
