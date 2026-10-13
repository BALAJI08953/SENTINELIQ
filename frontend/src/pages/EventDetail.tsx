import { useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { api, errMsg } from '../api/client'
import { useFetch } from '../hooks/useFetch'
import { Async, Button, Card, DemoTag, Empty, ErrorBox, Input, PriorityBadge, Tag } from '../components/ui'
import { CATEGORIES, type EventDetail as ED } from '../types'
import { fmtDate, label, pct } from '../utils/format'

export default function EventDetail() {
  const { id } = useParams()
  const ev = useFetch<ED>(`/events/${id}`)
  const [err, setErr] = useState<string | null>(null)
  const [msg, setMsg] = useState<string | null>(null)
  const [r, setR] = useState({ impact: 5, urgency: 5, strategic_relevance: 5 })
  const [fb, setFb] = useState({ correct_category: '', comment: '' })
  const run = async (fn: () => Promise<string | void>) => { setErr(null); setMsg(null); try { const m = await fn(); if (m) setMsg(m); ev.reload() } catch (e) { setErr(errMsg(e)) } }
  const sel = 'rounded border border-slate-300 px-2 py-1.5 text-sm'

  return (
    <Async state={ev}>{(e) => (
      <>
        <div><Link to="/feed" className="text-sm text-blue-700 hover:underline">← Intelligence feed</Link></div>
        <h1 className="text-xl font-bold">{e.title}</h1>
        <div className="flex flex-wrap items-center gap-2"><Tag>{label(e.category)}</Tag><Tag>status: {e.status}</Tag><DemoTag demo={e.is_demo} /><span className="text-sm text-slate-500">{fmtDate(e.occurred_at)}</span>
          <select className={sel} value={e.status} onChange={(x) => run(async () => { await api.patch(`/events/${e.id}`, { status: x.target.value }) })}>{['new', 'reviewed', 'dismissed'].map((s) => <option key={s}>{s}</option>)}</select></div>
        {err && <ErrorBox message={err} />}{msg && <div className="rounded border border-green-200 bg-green-50 p-2 text-sm text-green-800">{msg}</div>}

        <Card title="Source evidence (observed)">
          {e.evidence.length === 0 ? <Empty title="No evidence linked" hint="Claims without evidence stay unverified." /> :
            <ul className="divide-y text-sm">{e.evidence.map((x) => <li key={x.id} className="py-2"><Tag tone={x.verification_status === 'verified' ? 'bg-green-100 text-green-800' : 'bg-amber-100 text-amber-800'}>{x.verification_status}</Tag> observation #{x.observation_id}<p className="mt-1 text-slate-700">“{x.excerpt}”</p></li>)}</ul>}
          <p className="mt-2 text-xs text-slate-500">“Verified” means the excerpt exists in the stored observation. It does not confirm the claim is true.</p>
        </Card>

        <Card title="ML prediction (model output)" right={<Button onClick={() => run(async () => { const x = await api.post(`/events/${e.id}/process`); return `Predicted ${label(x.data.prediction.label)} (${pct(x.data.prediction.confidence)}); evidence verified: ${x.data.evidence.verified}, unverified: ${x.data.evidence.unverified}.` })}>Classify &amp; verify</Button>}>
          {e.predictions.length === 0 ? <Empty title="No prediction yet" hint="Train the model first: python -m app.ml.train" /> :
            <ul className="text-sm">{e.predictions.map((p) => <li key={p.id} className="py-1">{label(p.label)} — confidence {pct(p.confidence)} <span className="text-xs text-slate-500">({p.model_version})</span></li>)}</ul>}
        </Card>

        <Card title="Risk assessment (heuristic)">
          {e.risk_assessments.length === 0 ? <Empty title="Not assessed" /> : <ul className="divide-y text-sm">{e.risk_assessments.map((x) => (
            <li key={x.id} className="py-2"><div className="flex items-center gap-2"><PriorityBadge p={x.priority} /><b>{x.overall_score}</b>/100</div>
              <div className="text-slate-600">impact {x.impact} · urgency {x.urgency} · strategic {x.strategic_relevance} · evidence {x.evidence_quality}</div><div className="text-xs text-slate-500">{x.explanation}</div></li>))}</ul>}
          <div className="mt-3 flex flex-wrap items-center gap-2 text-sm">
            {(['impact', 'urgency', 'strategic_relevance'] as const).map((k) => <label key={k} className="flex items-center gap-1">{label(k)}<Input type="number" min={0} max={10} step={0.5} className="w-16" value={r[k]} onChange={(x) => setR({ ...r, [k]: Number(x.target.value) })} /></label>)}
            <Button onClick={() => run(async () => { await api.post(`/events/${e.id}/risk`, r) })}>Add assessment</Button></div>
          <p className="mt-2 text-xs text-slate-500">Decision-support heuristic, not a validated loss prediction. Evidence quality is derived from linked evidence.</p>
        </Card>

        <Card title="Business response options"><Empty title="Decision support not built yet" hint="Planned later; no response is recommended automatically from a single competitor event." /></Card>

        <Card title="Your review (human decision)">
          <div className="flex flex-wrap items-center gap-2"><select className={sel} value={fb.correct_category} onChange={(x) => setFb({ ...fb, correct_category: x.target.value })}><option value="">Category is correct</option>{CATEGORIES.map((c) => <option key={c} value={c}>{label(c)}</option>)}</select>
            <Input className="min-w-64 flex-1" placeholder="Comment (optional)" value={fb.comment} onChange={(x) => setFb({ ...fb, comment: x.target.value })} />
            <Button onClick={() => run(async () => { await api.post(`/events/${e.id}/feedback`, { correct_category: fb.correct_category || null, comment: fb.comment || null, useful: true }); setFb({ correct_category: '', comment: '' }); return 'Feedback saved.' })}>Submit feedback</Button></div>
        </Card>
      </>)}</Async>
  )
}
