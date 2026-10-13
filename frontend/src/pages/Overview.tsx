import { Bar, BarChart, CartesianGrid, Legend, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import { Link } from 'react-router-dom'
import { useFetch } from '../hooks/useFetch'
import { Async, Card, DemoTag, Empty, Stat, Tag } from '../components/ui'
import type { EventItem, Overview as Ov, Page } from '../types'
import { fmtDate, label } from '../utils/format'

const chart = (h = 220) => ({ width: '100%', height: h })

export default function Overview() {
  const ov = useFetch<Ov>('/analytics/overview')
  const tl = useFetch<{ date: string; events: number }[]>('/analytics/timeline')
  const cat = useFetch<{ category: string; count: number }[]>('/analytics/categories')
  const pri = useFetch<{ priority: string; count: number }[]>('/analytics/priorities')
  const act = useFetch<{ name: string; events: number; observations: number }[]>('/analytics/companies')
  const recent = useFetch<Page<EventItem>>('/events', { limit: 6 })
  return (
    <>
      <h1 className="text-xl font-bold">Overview</h1>
      <Async state={ov}>{(o) => (
        <>
          {o.demo_events > 0 && <div className="rounded border border-violet-200 bg-violet-50 p-2 text-sm text-violet-800">
            {o.demo_events} of {o.events} events are fictional demo data; {o.real_events} come from real collection.</div>}
          <div className="grid grid-cols-2 gap-3 md:grid-cols-4">
            <Stat name="Companies monitored" value={o.companies} />
            <Stat name="Observations" value={o.observations} />
            <Stat name="New events" value={o.new_events} />
            <Stat name="Awaiting verification" value={o.claims_awaiting_verification} />
            <Stat name="High priority" value={o.high_priority} tone="text-orange-600" />
            <Stat name="Critical" value={o.critical} tone="text-red-600" />
            <Stat name="Sources OK / error" value={`${o.sources_ok} / ${o.sources_error}`} />
            <Stat name="Never collected" value={o.sources_never_collected} />
          </div>
        </>
      )}</Async>
      <div className="grid gap-4 md:grid-cols-2">
        <Card title="Event timeline"><Async state={tl}>{(d) => d.length === 0 ? <Empty title="No events yet" /> :
          <div style={chart()}><ResponsiveContainer><LineChart data={d}><CartesianGrid strokeDasharray="3 3" /><XAxis dataKey="date" fontSize={11} /><YAxis allowDecimals={false} /><Tooltip /><Line dataKey="events" stroke="#0f172a" /></LineChart></ResponsiveContainer></div>}</Async></Card>
        <Card title="Events by category"><Async state={cat}>{(d) =>
          <div style={chart()}><ResponsiveContainer><BarChart data={d.map((x) => ({ ...x, category: label(x.category) }))}><CartesianGrid strokeDasharray="3 3" /><XAxis dataKey="category" fontSize={10} interval={0} angle={-30} textAnchor="end" height={60} /><YAxis allowDecimals={false} /><Tooltip /><Bar dataKey="count" fill="#475569" /></BarChart></ResponsiveContainer></div>}</Async></Card>
        <Card title="Risk priority distribution"><Async state={pri}>{(d) =>
          <div style={chart()}><ResponsiveContainer><BarChart data={d}><CartesianGrid strokeDasharray="3 3" /><XAxis dataKey="priority" /><YAxis allowDecimals={false} /><Tooltip /><Bar dataKey="count" fill="#ea580c" /></BarChart></ResponsiveContainer></div>}</Async>
          <p className="mt-2 text-xs text-slate-500">Scores are a decision-support heuristic, not a validated loss prediction.</p></Card>
        <Card title="Company activity"><Async state={act}>{(d) =>
          <div style={chart()}><ResponsiveContainer><BarChart data={d}><CartesianGrid strokeDasharray="3 3" /><XAxis dataKey="name" fontSize={10} /><YAxis allowDecimals={false} /><Tooltip /><Legend /><Bar dataKey="events" fill="#0f172a" /><Bar dataKey="observations" fill="#94a3b8" /></BarChart></ResponsiveContainer></div>}</Async></Card>
      </div>
      <Card title="Recent intelligence findings"><Async state={recent}>{(p) => p.items.length === 0 ? <Empty title="No findings yet" hint="Collect a source to create events." /> :
        <ul className="divide-y">{p.items.map((e) => (
          <li key={e.id} className="flex flex-wrap items-center gap-2 py-2"><Link className="font-medium text-blue-700 hover:underline" to={`/events/${e.id}`}>{e.title}</Link>
            <Tag>{label(e.category)}</Tag><DemoTag demo={e.is_demo} /><span className="ml-auto text-xs text-slate-500">{fmtDate(e.occurred_at)}</span></li>))}</ul>}</Async></Card>
    </>
  )
}
