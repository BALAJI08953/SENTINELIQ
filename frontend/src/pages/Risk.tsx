import { useState } from 'react'
import { Link } from 'react-router-dom'
import { useFetch } from '../hooks/useFetch'
import { Async, Card, Empty, PageTitle, Pager, PriorityBadge, linkClass } from '../components/ui'
import type { Page, Risk as R } from '../types'

export default function Risk() {
  const [priority, setPriority] = useState('')
  const [offset, setOffset] = useState(0)
  const list = useFetch<Page<R>>('/risk-assessments', { priority: priority || undefined, offset, limit: 10 })
  return (
    <>
      <PageTitle title="Risk assessments" subtitle="Scores combine impact, urgency, strategic relevance, and evidence quality. They are decision-support heuristics, not financial-loss predictions." />
      <select className="px-2 py-1.5 text-sm" value={priority} onChange={(e) => { setPriority(e.target.value); setOffset(0) }}>
        <option value="">All priorities</option>{['critical', 'high', 'medium', 'low'].map((p) => <option key={p}>{p}</option>)}
      </select>
      <Card><Async state={list}>{(p) => p.items.length === 0 ? <Empty title="No assessments" /> : (
        <>
          <ul className="divide-y divide-[#263650] text-sm">{p.items.map((x) => (
            <li key={x.id} className="py-2"><div className="flex items-center gap-2"><PriorityBadge p={x.priority} /><b className="text-slate-100">{x.overall_score}</b><Link className={linkClass} to={`/events/${x.event_id}`}>Event #{x.event_id}</Link></div>
              <div className="text-slate-400">impact {x.impact} - urgency {x.urgency} - strategic {x.strategic_relevance} - evidence {x.evidence_quality}</div></li>
          ))}</ul>
          <Pager total={p.total} offset={p.offset} limit={p.limit} onChange={setOffset} />
        </>
      )}</Async></Card>
    </>
  )
}
