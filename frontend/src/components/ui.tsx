import type { ReactNode } from 'react'
import { AlertCircle, Inbox, Loader2 } from 'lucide-react'
import type { Priority } from '../types'

export const PageTitle = ({ title, subtitle }: { title: string; subtitle?: string }) => (
  <header className="flex flex-wrap items-end justify-between gap-3">
    <div>
      <h1 className="text-xl font-semibold text-slate-50">{title}</h1>
      {subtitle && <p className="mt-1 max-w-2xl text-sm leading-6 text-slate-400">{subtitle}</p>}
    </div>
  </header>
)

export const Card = ({ title, children, right }: { title?: string; children: ReactNode; right?: ReactNode }) => (
  <section className="rounded-lg border border-[#263650] bg-[#111B32]/95 p-4 shadow-[0_18px_50px_rgba(0,0,0,0.24)] backdrop-blur-xl">
    {(title || right) && <div className="mb-3 flex items-center justify-between gap-3"><h2 className="font-semibold text-slate-50">{title}</h2>{right}</div>}
    {children}
  </section>
)

export const Stat = ({ name, value, tone }: { name: string; value: number | string; tone?: string }) => (
  <div className="rounded-lg border border-[#263650] bg-[#111B32] p-4 shadow-[0_14px_40px_rgba(0,0,0,0.2)]">
    <div className="text-xs uppercase text-slate-400">{name}</div>
    <div className={`mt-1 text-2xl font-bold ${tone ?? 'text-slate-50'}`}>{value}</div>
  </div>
)

const PRIO: Record<Priority, string> = {
  low: 'bg-slate-100/80 text-slate-700 ring-slate-200',
  medium: 'bg-amber-100/80 text-amber-800 ring-amber-200',
  high: 'bg-orange-100/80 text-orange-800 ring-orange-200',
  critical: 'bg-red-100/80 text-red-800 ring-red-200',
}

export const PriorityBadge = ({ p }: { p: Priority }) => <span className={`rounded px-2 py-0.5 text-xs font-medium ring-1 ring-inset ${PRIO[p]}`}>{p}</span>
export const Tag = ({ children, tone = 'bg-slate-100/80 text-slate-700 ring-slate-200' }: { children: ReactNode; tone?: string }) => <span className={`rounded px-2 py-0.5 text-xs ring-1 ring-inset ${tone}`}>{children}</span>
export const DemoTag = (props: { demo: boolean }) => props.demo ? null : null
export const Loading = () => <div className="flex items-center gap-2 p-6 text-slate-400"><Loader2 className="h-4 w-4 animate-spin" />Loading...</div>
export const ErrorBox = ({ message }: { message: string }) => <div role="alert" className="flex items-center gap-2 rounded-lg border border-red-500/40 bg-red-950/50 p-3 text-sm text-red-100 shadow-sm backdrop-blur"><AlertCircle className="h-4 w-4" />{message}</div>
export const SuccessBox = ({ message }: { message: string }) => <div className="rounded-lg border border-emerald-400/30 bg-emerald-950/50 p-3 text-sm text-emerald-100 shadow-sm backdrop-blur">{message}</div>
export const Empty = ({ title, hint }: { title: string; hint?: string }) => (
  <div className="flex flex-col items-center gap-1 p-8 text-center text-slate-400"><Inbox className="h-6 w-6" /><div className="font-medium text-slate-200">{title}</div>{hint && <div className="text-sm">{hint}</div>}</div>
)

export const Button = ({ children, ...p }: React.ButtonHTMLAttributes<HTMLButtonElement>) => (
  <button {...p} className={`rounded-md border border-cyan-300/30 bg-[#3B82F6] px-3 py-1.5 text-sm font-medium text-white shadow-sm transition hover:bg-cyan-500 disabled:opacity-50 ${p.className ?? ''}`}>{children}</button>
)

export const linkClass = 'font-medium text-cyan-300 underline-offset-2 hover:text-cyan-100 hover:underline'

export const Input = (p: React.InputHTMLAttributes<HTMLInputElement>) => <input {...p} className={`rounded-md border border-[#263650] bg-[#0B1020]/80 px-2 py-1.5 text-sm text-slate-50 shadow-sm outline-none placeholder:text-slate-500 focus:border-cyan-300 focus:ring-2 focus:ring-cyan-300/20 ${p.className ?? ''}`} />

export function Pager({ total, offset, limit, onChange }: { total: number; offset: number; limit: number; onChange: (o: number) => void }) {
  if (total <= limit) return null
  return (
    <div className="mt-3 flex items-center justify-between text-sm text-slate-400">
      <span>{offset + 1} to {Math.min(offset + limit, total)} of {total}</span>
      <div className="flex gap-2">
        <Button disabled={offset === 0} onClick={() => onChange(Math.max(0, offset - limit))}>Previous</Button>
        <Button disabled={offset + limit >= total} onClick={() => onChange(offset + limit)}>Next</Button>
      </div>
    </div>
  )
}

export function Async<T>({ state, children }: { state: { data: T | null; loading: boolean; error: string | null; reload?: () => void }; children: (d: T) => ReactNode }) {
  if (state.loading && !state.data) return <Loading />
  if (state.error) return <div className="space-y-2"><ErrorBox message={state.error} />{state.reload && <Button onClick={state.reload}>Retry</Button>}</div>
  return state.data ? <>{children(state.data)}</> : null
}
