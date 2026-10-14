import { Bar, BarChart, CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import { Activity, ArrowUpRight, CheckCircle2 } from 'lucide-react'
import { Link } from 'react-router-dom'
import { useFetch } from '../hooks/useFetch'
import { Async, Card, DemoTag, Empty, Stat, Tag, linkClass } from '../components/ui'
import type { EventItem, Overview as Ov, Page } from '../types'
import { fmtDate, label } from '../utils/format'

const chart = (height = 220) => ({ width: '100%', height })

export default function Overview() {
  const ov = useFetch<Ov>('/analytics/overview')
  const tl = useFetch<{ date: string; events: number }[]>('/analytics/timeline')
  const cat = useFetch<{ category: string; count: number }[]>('/analytics/categories')
  const pri = useFetch<{ priority: string; count: number }[]>('/analytics/priorities')
  const act = useFetch<{ name: string; events: number; observations: number }[]>('/analytics/companies')
  const recent = useFetch<Page<EventItem>>('/events', { limit: 6 })
  return (
    <>
      <header className="rounded-lg border border-cyan-300/20 bg-[#111B32] p-5 text-white shadow-[0_22px_60px_rgba(0,0,0,0.3)] md:flex md:items-end md:justify-between md:gap-6">
        <div>
          <div className="mb-3 inline-flex items-center gap-2 rounded-full border border-cyan-300/30 bg-cyan-300/10 px-2.5 py-1 text-xs text-cyan-100">
            <Activity className="h-3.5 w-3.5" />Live intelligence workspace
          </div>
          <h1 className="text-3xl font-semibold tracking-tight">SentinelIQ competitive intelligence</h1>
          <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-300">Detect competitor changes, inspect evidence, compare business impact, and turn approved recommendations into follow-up work.</p>
        </div>
        <Link to="/feed" className="mt-4 inline-flex items-center gap-1 text-sm text-cyan-200 hover:text-white md:mt-0">Open intelligence feed <ArrowUpRight className="h-4 w-4" /></Link>
      </header>
      <Async state={ov}>{(o) => (
        <>
          {o.events === 0 && <div className="rounded-lg border border-[#263650] bg-[#111B32] p-3 text-sm text-slate-300">No recent intelligence is available. Connect a permitted source to begin monitoring.</div>}
          <div className="grid grid-cols-2 gap-3 md:grid-cols-4">
            <Stat name="Monitored companies" value={o.companies} />
            <Stat name="Changes detected" value={o.events} />
            <Stat name="Potential threats" value={o.high_priority + o.critical} tone="text-amber-300" />
            <Stat name="Awaiting approval" value={o.recommendations_awaiting_approval ?? o.new_events} tone="text-cyan-200" />
          </div>
        </>
      )}</Async>
      <div className="grid gap-4 md:grid-cols-2">
        <Card title="Competitor activity timeline"><Async state={tl}>{(d) => d.length === 0 ? <Empty title="No events yet" /> :
          <div style={chart()}><ResponsiveContainer><LineChart data={d}><CartesianGrid stroke="#263650" strokeDasharray="3 3" /><XAxis dataKey="date" fontSize={11} stroke="#94A3B8" /><YAxis allowDecimals={false} stroke="#94A3B8" /><Tooltip contentStyle={{ background: '#111B32', border: '1px solid #263650', color: '#F8FAFC' }} /><Line dataKey="events" stroke="#22D3EE" strokeWidth={2} /></LineChart></ResponsiveContainer></div>}</Async></Card>
        <Card title="Changes by category"><Async state={cat}>{(d) =>
          <div style={chart()}><ResponsiveContainer><BarChart data={d.map((x) => ({ ...x, category: label(x.category) }))}><CartesianGrid stroke="#263650" strokeDasharray="3 3" /><XAxis dataKey="category" fontSize={10} interval={0} angle={-30} textAnchor="end" height={60} stroke="#94A3B8" /><YAxis allowDecimals={false} stroke="#94A3B8" /><Tooltip contentStyle={{ background: '#111B32', border: '1px solid #263650', color: '#F8FAFC' }} /><Bar dataKey="count" fill="#3B82F6" /></BarChart></ResponsiveContainer></div>}</Async></Card>
        <Card title="Risk priority distribution"><Async state={pri}>{(d) =>
          <div style={chart()}><ResponsiveContainer><BarChart data={d}><CartesianGrid stroke="#263650" strokeDasharray="3 3" /><XAxis dataKey="priority" stroke="#94A3B8" /><YAxis allowDecimals={false} stroke="#94A3B8" /><Tooltip contentStyle={{ background: '#111B32', border: '1px solid #263650', color: '#F8FAFC' }} /><Bar dataKey="count" fill="#8B5CF6" /></BarChart></ResponsiveContainer></div>}</Async>
          <p className="mt-2 text-xs text-slate-400">Scores are a decision-support heuristic, not a validated loss prediction.</p></Card>
        <Card title="Latest monitoring status"><Async state={act}>{(d) =>
          <div className="space-y-2 text-sm">{d.map((x) => <div key={x.name} className="flex items-center gap-2 rounded-md border border-[#263650] bg-[#0B1020]/50 p-2"><CheckCircle2 className="h-4 w-4 text-cyan-300" /><span className="font-medium text-slate-100">{x.name}</span><span className="ml-auto text-slate-400">{x.events} findings, {x.observations} observations</span></div>)}</div>}</Async></Card>
      </div>
      <Card title="Recent intelligence findings"><Async state={recent}>{(p) => p.items.length === 0 ? <Empty title="No findings yet" hint="Collect a source to create events." /> :
        <ul className="divide-y divide-[#263650]">{p.items.map((e) => (
          <li key={e.id} className="flex flex-wrap items-center gap-2 py-2"><Link className={linkClass} to={`/events/${e.id}`}>{e.title}</Link>
            <Tag>{label(e.category)}</Tag><DemoTag demo={e.is_demo} /><span className="ml-auto text-xs text-slate-400">{fmtDate(e.occurred_at)}</span></li>))}</ul>}</Async></Card>
    </>
  )
}
