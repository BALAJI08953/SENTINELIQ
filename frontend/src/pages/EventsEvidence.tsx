import { Link } from 'react-router-dom'
import { Card, Empty, PageTitle, PriorityBadge, Tag, linkClass } from '../components/ui'
import { useFetch } from '../hooks/useFetch'
import type { EventItem, Page, Risk } from '../types'
import { fmtDate, label } from '../utils/format'

export default function EventsEvidence() {
  const events = useFetch<Page<EventItem>>('/events', { limit: 100 })
  const risks = useFetch<Page<Risk>>('/risk-assessments', { limit: 100 })
  const riskByEvent = new Map(risks.data?.items.map((r) => [r.event_id, r]))
  return (
    <div className="space-y-4">
      <PageTitle title="Events & Evidence" subtitle="Trace every event to stored observations, model signals, and explainable risk assessments." />
      <Card title="Evidence-backed events">
        {events.data?.items.length === 0 && <Empty title="No events" hint="Configure sources and extract events to populate this view." />}
        <div className="divide-y divide-[#263650]">{events.data?.items.map((event) => {
          const risk = riskByEvent.get(event.id)
          return <div key={event.id} className="py-3">
            <div className="flex flex-wrap items-center gap-2"><Link className={linkClass} to={`/events/${event.id}`}>{event.title}</Link><Tag>{label(event.category)}</Tag>{risk && <PriorityBadge p={risk.priority} />}<span className="ml-auto text-xs text-slate-500">{fmtDate(event.occurred_at)}</span></div>
            <p className="mt-1 text-sm text-slate-400">Open the event to review evidence excerpts, uncertainty, model classification, and response options.</p>
          </div>
        })}</div>
      </Card>
    </div>
  )
}
