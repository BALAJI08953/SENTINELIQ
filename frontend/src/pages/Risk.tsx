import { useState } from 'react'
import { Link } from 'react-router-dom'
import { useFetch } from '../hooks/useFetch'
import { Async, Card, Empty, Pager, PriorityBadge } from '../components/ui'
import type { Page, Risk as R } from '../types'

export default function Risk() {
  const [priority, setPriority] = useState('')
  const [offset, setOffset] = useState(0)
  const list = useFetch<Page<R>>('/risk-assessments', { priority: priority || undefined, offset, limit: 10 })
  return (
    <>
      <h1 className="text-xl font-bold">Risk assessments</h1>
      <p className="text-sm text-slate-600">Scores combine impact (35%), urgency (25%), strategic relevance (25%) and evidence quality (15%). This is a decision-support heuristic, not a validated financial-loss prediction.</p>
      <select className="rounded border border-slate-300 px-2 py-1.5 text-sm" value={priority} onChange={(e) => { setPriority(e.target.value); setOffset(0) }}>
        <option value="">All priorities</option>{['critical', 'high', 'medium', 'low'].map((p) => <option key={p}>{p}</option>)}</select>
      <Card><Async state={list}>{(p) => p.items.length === 0 ? <Empty title="No assessments" /> : (<>
        <ul className="divide-y text-sm">{p.items.map((x) => (
          <li key={x.id} className="py-2"><div className="flex items-center gap-2"><PriorityBadge p={x.priority} /><b>{x.overall_score}</b><Link className="text-blue-700 hover:underline" to={`/events/${x.event_id}`}>Event #{x.event_id}</Link></div>
            <div className="text-slate-600">impact {x.impact} · urgency {x.urgency} · strategic {x.strategic_relevance} · evidence {x.evidence_quality}</div></li>))}</ul>
        <Pager total={p.total} offset={p.offset} limit={p.limit} onChange={setOffset} /></>)}</Async></Card>
    </>
  )
}
