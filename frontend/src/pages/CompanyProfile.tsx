import { useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { api, errMsg } from '../api/client'
import { useFetch } from '../hooks/useFetch'
import { Async, Button, Card, DemoTag, Empty, ErrorBox, Input, Tag } from '../components/ui'
import type { Company, EventItem, Observation, Page, Relationship, Source } from '../types'
import { fmtDate, label } from '../utils/format'

export default function CompanyProfile() {
  const { id } = useParams()
  const nav = useNavigate()
  const base = `/companies/${id}`
  const company = useFetch<Company>(base)
  const sources = useFetch<Source[]>(`${base}/sources`)
  const events = useFetch<Page<EventItem>>(`${base}/events`, { limit: 20 })
  const obs = useFetch<Page<Observation>>('/observations', { company_id: id, limit: 5 })
  const rels = useFetch<Relationship[]>(`${base}/relationships`)
  const all = useFetch<Page<Company>>('/companies', { limit: 200 })
  const [msg, setMsg] = useState<string | null>(null)
  const [err, setErr] = useState<string | null>(null)
  const [editing, setEditing] = useState(false)
  const [form, setForm] = useState({ name: '', industry: '', description: '', website: '' })
  const [src, setSrc] = useState({ kind: 'rss', url: '' })

  const run = async (fn: () => Promise<void>) => { setErr(null); setMsg(null); try { await fn() } catch (e) { setErr(errMsg(e)) } }
  const names = new Map(all.data?.items.map((c) => [c.id, c.name]))
  const startEdit = (c: Company) => { setForm({ name: c.name, industry: c.industry ?? '', description: c.description ?? '', website: c.website ?? '' }); setEditing(true) }
  const refresh = () => { sources.reload(); events.reload(); obs.reload() }

  return (
    <>
      <Async state={company}>{(c) => (
        <Card title={c.name} right={<div className="flex gap-2"><DemoTag demo={c.is_demo} />
          <Button onClick={() => startEdit(c)}>Edit</Button>
          <Button className="bg-red-700" onClick={() => run(async () => { if (window.confirm(`Delete ${c.name}?`)) { await api.delete(base); nav('/companies') } })}>Delete</Button></div>}>
          {editing ? (
            <div className="flex flex-wrap gap-2">
              {(['name', 'industry', 'website', 'description'] as const).map((k) => <Input key={k} placeholder={k} value={form[k]} onChange={(e) => setForm({ ...form, [k]: e.target.value })} />)}
              <Button onClick={() => run(async () => { await api.patch(base, { name: form.name, industry: form.industry || null, website: form.website || null, description: form.description || null }); setEditing(false); company.reload() })}>Save</Button>
              <Button className="bg-slate-500" onClick={() => setEditing(false)}>Cancel</Button>
            </div>
          ) : (
            <dl className="grid gap-1 text-sm text-slate-700">
              <div>Industry: {c.industry ?? 'not provided'}</div><div>Website: {c.website ?? 'not provided'}</div>
              <div>{c.description ?? 'No description provided.'}</div></dl>)}
        </Card>)}</Async>
      {err && <ErrorBox message={err} />}{msg && <div className="rounded border border-green-200 bg-green-50 p-2 text-sm text-green-800">{msg}</div>}

      <Card title="Monitored sources">
        <Async state={sources}>{(s) => s.length === 0 ? <Empty title="No sources yet" hint="Add an RSS feed or public page below." /> : (
          <ul className="divide-y text-sm">{s.map((x) => (
            <li key={x.id} className="flex flex-wrap items-center gap-2 py-2"><Tag>{x.kind}</Tag><span className="break-all">{x.url}</span><DemoTag demo={x.is_demo} />
              <Tag tone={x.last_status === 'error' ? 'bg-red-100 text-red-700' : 'bg-slate-100 text-slate-600'}>{x.last_status ?? 'never collected'}</Tag>
              {x.last_error && <span className="text-xs text-red-600">{x.last_error}</span>}
              <span className="ml-auto flex gap-2"><Button onClick={() => run(async () => { const r = await api.post(`/sources/${x.id}/collect`); setMsg(`Collected: ${r.data.new} new, ${r.data.duplicates} duplicate, ${r.data.events_created} events created.`); refresh() })}>Collect</Button>
                <button className="text-red-600" onClick={() => run(async () => { await api.delete(`/sources/${x.id}`); sources.reload() })}>Remove</button></span></li>))}</ul>)}</Async>
        <div className="mt-3 flex flex-wrap gap-2">
          <select className="rounded border border-slate-300 px-2 py-1.5 text-sm" value={src.kind} onChange={(e) => setSrc({ ...src, kind: e.target.value })}><option value="rss">rss</option><option value="html">html</option></select>
          <Input className="min-w-64 flex-1" placeholder="https://…" value={src.url} onChange={(e) => setSrc({ ...src, url: e.target.value })} />
          <Button disabled={!src.url} onClick={() => run(async () => { await api.post(`${base}/sources`, src); setSrc({ ...src, url: '' }); sources.reload() })}>Add source</Button>
        </div>
        <p className="mt-2 text-xs text-slate-500">Only add sources you are permitted to collect from; robots.txt is checked for HTML pages.</p>
      </Card>

      <div className="grid gap-4 md:grid-cols-2">
        <Card title="Detected events"><Async state={events}>{(p) => p.items.length === 0 ? <Empty title="No events" /> :
          <ul className="divide-y text-sm">{p.items.map((e) => <li key={e.id} className="py-2"><Link className="text-blue-700 hover:underline" to={`/events/${e.id}`}>{e.title}</Link> <Tag>{label(e.category)}</Tag> <span className="text-xs text-slate-500">{fmtDate(e.occurred_at)}</span></li>)}</ul>}</Async></Card>
        <Card title="Recent observations"><Async state={obs}>{(p) => p.items.length === 0 ? <Empty title="No observations" /> :
          <ul className="divide-y text-sm">{p.items.map((o) => <li key={o.id} className="py-2">{o.title} <DemoTag demo={o.is_demo} /><div className="text-xs text-slate-500">collected {fmtDate(o.collected_at)}</div></li>)}</ul>}</Async></Card>
      </div>
      <Card title="Related companies"><Async state={rels}>{(r) => r.length === 0 ? <Empty title="No relationships recorded" hint="Relationships are never inferred without evidence." /> :
        <ul className="text-sm">{r.map((x) => <li key={x.id} className="py-1"><Link className="text-blue-700 hover:underline" to={`/companies/${x.related_company_id}`}>{names.get(x.related_company_id) ?? `Company ${x.related_company_id}`}</Link> — {x.relationship_type} <Tag tone={x.verification_status === 'verified' ? 'bg-green-100 text-green-800' : 'bg-amber-100 text-amber-800'}>{x.verification_status}</Tag></li>)}</ul>}</Async></Card>
      <Card title="Reports"><Empty title="Report history not available yet" hint="Report generation is planned for stage 6 and has no backend yet." /></Card>
    </>
  )
}
