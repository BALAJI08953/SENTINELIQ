import { useState } from 'react'
import { Link } from 'react-router-dom'
import { api, errMsg } from '../api/client'
import { useFetch } from '../hooks/useFetch'
import { Async, Button, Card, DemoTag, Empty, ErrorBox, Input, Pager, Tag } from '../components/ui'
import { CATEGORIES, type Company, type EventItem, type Observation, type Page } from '../types'
import { fmtDate, label } from '../utils/format'

export default function Feed() {
  const [tab, setTab] = useState<'observations' | 'events'>('events')
  const [q, setQ] = useState('')
  const [company, setCompany] = useState('')
  const [category, setCategory] = useState('')
  const [demo, setDemo] = useState('')
  const [offset, setOffset] = useState(0)
  const [err, setErr] = useState<string | null>(null)
  const companies = useFetch<Page<Company>>('/companies', { limit: 200 })
  const reset = () => setOffset(0)
  const obs = useFetch<Page<Observation>>(tab === 'observations' ? '/observations' : null, { q: q || undefined, company_id: company || undefined, is_demo: demo || undefined, offset, limit: 10 })
  const evs = useFetch<Page<EventItem>>(tab === 'events' ? '/events' : null, { q: q || undefined, company_id: company || undefined, category: category || undefined, offset, limit: 10 })
  const names = new Map(companies.data?.items.map((c) => [c.id, c.name]))
  const sel = 'rounded border border-slate-300 px-2 py-1.5 text-sm'

  return (
    <>
      <h1 className="text-xl font-bold">Intelligence feed</h1>
      <div className="flex flex-wrap items-center gap-2">
        {(['events', 'observations'] as const).map((t) => <Button key={t} className={tab === t ? '' : 'bg-slate-400'} onClick={() => { setTab(t); reset() }}>{t}</Button>)}
        <Input placeholder="Search…" value={q} onChange={(e) => { setQ(e.target.value); reset() }} />
        <select className={sel} value={company} onChange={(e) => { setCompany(e.target.value); reset() }}><option value="">All companies</option>{companies.data?.items.map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}</select>
        {tab === 'events' ? <select className={sel} value={category} onChange={(e) => { setCategory(e.target.value); reset() }}><option value="">All categories</option>{CATEGORIES.map((c) => <option key={c} value={c}>{label(c)}</option>)}</select>
          : <select className={sel} value={demo} onChange={(e) => { setDemo(e.target.value); reset() }}><option value="">Real + demo</option><option value="false">Real only</option><option value="true">Demo only</option></select>}
      </div>
      {err && <ErrorBox message={err} />}
      <Card>
        {tab === 'events' ? <Async state={evs}>{(p) => p.items.length === 0 ? <Empty title="No events match" /> : (<>
          <ul className="divide-y">{p.items.map((e) => <li key={e.id} className="flex flex-wrap items-center gap-2 py-2"><Link className="font-medium text-blue-700 hover:underline" to={`/events/${e.id}`}>{e.title}</Link><Tag>{label(e.category)}</Tag><Tag>{e.status}</Tag><DemoTag demo={e.is_demo} /><span className="text-xs text-slate-500">{names.get(e.company_id)}</span><span className="ml-auto text-xs text-slate-500">{fmtDate(e.occurred_at)}</span></li>)}</ul>
          <Pager total={p.total} offset={p.offset} limit={p.limit} onChange={setOffset} /></>)}</Async>
        : <Async state={obs}>{(p) => p.items.length === 0 ? <Empty title="No observations match" /> : (<>
          <ul className="divide-y">{p.items.map((o) => <li key={o.id} className="py-2"><div className="flex flex-wrap items-center gap-2"><span className="font-medium">{o.title}</span><DemoTag demo={o.is_demo} /><span className="text-xs text-slate-500">{names.get(o.company_id)} · collected {fmtDate(o.collected_at)}</span>
            <Button className="ml-auto" onClick={async () => { setErr(null); try { await api.post(`/observations/${o.id}/extract-event`); obs.reload() } catch (e) { setErr(errMsg(e)) } }}>Create event</Button></div>
            <p className="mt-1 line-clamp-2 text-sm text-slate-600">{o.body}</p>{o.url && <div className="break-all text-xs text-slate-400">{o.url}</div>}</li>)}</ul>
          <Pager total={p.total} offset={p.offset} limit={p.limit} onChange={setOffset} /></>)}</Async>}
      </Card>
    </>
  )
}
