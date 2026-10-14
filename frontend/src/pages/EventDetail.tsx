import { useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { api, errMsg } from '../api/client'
import { useFetch } from '../hooks/useFetch'
import { Async, Button, Card, DemoTag, Empty, ErrorBox, Input, PageTitle, PriorityBadge, SuccessBox, Tag, linkClass } from '../components/ui'
import { CATEGORIES, type DecisionSupport, type EventDetail as ED, type EventInsight } from '../types'
import { fmtDate, label, pct } from '../utils/format'

export default function EventDetail() {
  const { id } = useParams()
  const ev = useFetch<ED>(`/events/${id}`)
  const insight = useFetch<EventInsight>(id ? `/events/${id}/insights` : null)
  const decisions = useFetch<DecisionSupport>(id ? `/events/${id}/decision-support` : null)
  const [err, setErr] = useState<string | null>(null)
  const [msg, setMsg] = useState<string | null>(null)
  const [r, setR] = useState({ impact: 5, urgency: 5, strategic_relevance: 5 })
  const [fb, setFb] = useState({ correct_category: '', comment: '' })
  const selectClass = 'px-2 py-1.5 text-sm'

  const run = async (fn: () => Promise<string | void>) => {
    setErr(null)
    setMsg(null)
    try {
      const message = await fn()
      if (message) setMsg(message)
      ev.reload()
    } catch (e) {
      setErr(errMsg(e))
    }
  }

  return (
    <Async state={ev}>{(e) => (
      <>
        <Link to="/feed" className={`text-sm ${linkClass}`}>Back to intelligence feed</Link>
        <PageTitle title={e.title} subtitle={`Observed ${fmtDate(e.occurred_at)}. Evidence, risk scoring, and recommendations are separated for human review.`} />
        <div className="flex flex-wrap items-center gap-2">
          <Tag>{label(e.category)}</Tag><Tag>status: {e.status}</Tag><DemoTag demo={e.is_demo} />
          <select className={selectClass} value={e.status} onChange={(x) => run(async () => { await api.patch(`/events/${e.id}`, { status: x.target.value }) })}>{['new', 'reviewed', 'dismissed'].map((s) => <option key={s}>{s}</option>)}</select>
        </div>
        {err && <ErrorBox message={err} />}{msg && <SuccessBox message={msg} />}

        <Card title="What changed">
          <div className="grid gap-3 text-sm md:grid-cols-3">
            <div className="rounded-lg border border-[#263650] bg-[#0B1020]/60 p-3"><div className="text-xs uppercase text-slate-500">Finding</div><div className="mt-1 font-medium text-slate-100">{e.title}</div></div>
            <div className="rounded-lg border border-[#263650] bg-[#0B1020]/60 p-3"><div className="text-xs uppercase text-slate-500">Category</div><div className="mt-1 font-medium text-slate-100">{label(e.category)}</div></div>
            <div className="rounded-lg border border-amber-400/30 bg-amber-950/30 p-3"><div className="text-xs uppercase text-amber-200">Structured comparison</div><div className="mt-1 font-medium text-amber-100">Available when source data includes previous and current values</div></div>
          </div>
          <p className="mt-3 text-xs text-slate-400">This view is generalized for any event category. Future dataset integrations can populate source-backed previous/current values when those fields exist.</p>
        </Card>

        <Card title="Source evidence">
          {e.evidence.length === 0 ? <Empty title="No evidence linked" hint="Claims without evidence stay unverified." /> :
            <ul className="divide-y divide-[#263650] text-sm">{e.evidence.map((x) => <li key={x.id} className="py-2"><Tag tone={x.verification_status === 'verified' ? 'bg-green-950/80 text-green-200 ring-green-400/30' : 'bg-amber-950/80 text-amber-200 ring-amber-400/30'}>{x.verification_status}</Tag> <span className="text-slate-300">observation #{x.observation_id}</span><p className="mt-1 text-slate-300">"{x.excerpt}"</p><div className="mt-1 text-xs text-slate-500">Source URL: future implementation</div></li>)}</ul>}
          <p className="mt-2 text-xs text-slate-500">Verified means the excerpt exists in stored observation text. It does not confirm the business claim is true.</p>
          {insight.data?.evidence_assessments?.length ? <div className="mt-3 border-t border-[#263650] pt-3 text-xs text-slate-400">
            <div className="mb-2 font-medium text-slate-200">Automated evidence assessment</div>
            {insight.data.evidence_assessments.map((item) => <div key={item.evidence_id} className="mb-2">
              Evidence #{item.evidence_id}: text match {item.text_match ? 'yes' : 'no'}, provenance {item.provenance ? 'yes' : 'no'}, source accessible {item.source_accessible ? 'yes' : 'no'}, corroboration {item.corroboration}.
            </div>)}
          </div> : null}
        </Card>

        <Card title="ML prediction">
          {e.predictions.length === 0 ? <Empty title="No prediction yet" hint="Train the model first: python -m app.ml.train" /> :
            <ul className="text-sm">{e.predictions.map((p) => <li key={p.id} className="py-1 text-slate-300">{label(p.label)} - confidence {pct(p.confidence)} <span className="text-xs text-slate-500">({p.model_version})</span></li>)}</ul>}
        </Card>

        <Card title="Risk assessment">
          {e.risk_assessments.length === 0 ? <Empty title="Not assessed" /> : <ul className="divide-y divide-[#263650] text-sm">{e.risk_assessments.map((x) => (
            <li key={x.id} className="py-2"><div className="flex items-center gap-2"><PriorityBadge p={x.priority} /><b className="text-slate-100">{x.overall_score}</b><span className="text-slate-400">/100</span></div>
              <div className="text-slate-400">impact {x.impact} - urgency {x.urgency} - strategic {x.strategic_relevance} - evidence {x.evidence_quality}</div><div className="text-xs text-slate-500">{x.explanation}</div></li>
          ))}</ul>}
          <div className="mt-3 flex flex-wrap items-center gap-2 text-sm text-slate-300">
            {(['impact', 'urgency', 'strategic_relevance'] as const).map((k) => <label key={k} className="flex items-center gap-1">{label(k)}<Input type="number" min={0} max={10} step={0.5} className="w-16" value={r[k]} onChange={(x) => setR({ ...r, [k]: Number(x.target.value) })} /></label>)}
            <Button onClick={() => run(async () => { await api.post(`/events/${e.id}/risk`, r) })}>Add assessment</Button></div>
          <p className="mt-2 text-xs text-slate-500">Decision-support heuristic, not a validated loss prediction. Evidence quality is derived from linked evidence.</p>
        </Card>

        <Card title="Rule-based interpretation">
          <Async state={insight}>{(data) => (
            <div className="space-y-3 text-sm">
              <p className="text-slate-300">{data.summary}</p>
              <div className="grid gap-3 md:grid-cols-2">
                <div><div className="mb-1 font-medium text-slate-100">Why it may matter</div><ul className="list-disc space-y-1 pl-5 text-slate-400">{data.possible_implications.map((item) => <li key={item}>{item}</li>)}</ul></div>
                <div><div className="mb-1 font-medium text-slate-100">Confidence and uncertainty</div><ul className="list-disc space-y-1 pl-5 text-slate-400">{data.uncertainties.map((item) => <li key={item}>{item}</li>)}</ul></div>
              </div>
              <div className="text-xs text-slate-500">Provider: {data.provider}. This is not claimed as LLM-generated analysis.</div>
            </div>
          )}</Async>
        </Card>

        <Card title="Business response options">
          <Async state={decisions}>{(data) => (
            <div className="space-y-3">
              <p className="text-xs text-slate-500">{data.disclaimer}</p>
              <div className="grid gap-3 md:grid-cols-3">{data.options.map((option) => (
                <div key={option.name} className="rounded-lg border border-[#263650] bg-[#0B1020]/60 p-3 text-sm">
                  <div className="font-medium text-slate-100">{option.name}</div>
                  <div className="mt-2 text-xs text-emerald-300">Benefits: {option.benefits.join(' ')}</div>
                  <div className="mt-2 text-xs text-rose-300">Drawbacks: {option.drawbacks.join(' ')}</div>
                  <div className="mt-2 text-xs text-slate-400">Next: {option.next_steps.join(' ')}</div>
                </div>
              ))}</div>
              <p className="text-xs text-slate-500">Use the Workflows page to create or update follow-up work after human review.</p>
            </div>
          )}</Async>
        </Card>

        <Card title="Your review">
          <div className="flex flex-wrap items-center gap-2"><select className={selectClass} value={fb.correct_category} onChange={(x) => setFb({ ...fb, correct_category: x.target.value })}><option value="">Category is correct</option>{CATEGORIES.map((c) => <option key={c}>{label(c)}</option>)}</select>
            <Input className="min-w-64 flex-1" placeholder="Comment (optional)" value={fb.comment} onChange={(x) => setFb({ ...fb, comment: x.target.value })} />
            <Button onClick={() => run(async () => { await api.post(`/events/${e.id}/feedback`, { correct_category: fb.correct_category || null, comment: fb.comment || null, useful: true }); setFb({ correct_category: '', comment: '' }); return 'Feedback saved.' })}>Submit feedback</Button></div>
        </Card>
      </>
    )}</Async>
  )
}
