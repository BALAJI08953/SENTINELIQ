import type {
  Company,
  DecisionSupport,
  EventDetail,
  EventInsight,
  EventItem,
  Observation,
  Page,
  Priority,
  Report,
  Risk,
  Settings,
  Source,
  Workflow,
} from '../types'

const STORE = 'sentineliq.prototype.v1'
const now = new Date('2026-10-13T12:00:00+05:30')

type Store = {
  companies: Company[]
  events: EventDetail[]
  observations: Observation[]
  sources: Source[]
  reports: Report[]
  workflows: Workflow[]
  settings: Settings
}

const daysAgo = (days: number) => new Date(now.getTime() - days * 86400000).toISOString()

const seed: Store = {
  companies: [
    { id: 1, name: 'Asterion Systems', industry: 'Enterprise automation', website: null, description: 'Tracks workflow automation, enterprise integrations, and platform packaging changes.', is_demo: false },
    { id: 2, name: 'Northstar Analytics', industry: 'Decision intelligence', website: null, description: 'Monitors analytics launches, partner programs, and regional expansion signals.', is_demo: false },
    { id: 3, name: 'BluePeak Robotics', industry: 'Industrial robotics', website: null, description: 'Tracks robotics deployments, supply-chain signals, and operational partnerships.', is_demo: false },
    { id: 4, name: 'Meridian Cloudworks', industry: 'Cloud infrastructure', website: null, description: 'Monitors infrastructure pricing, reliability incidents, and compliance updates.', is_demo: false },
    { id: 5, name: 'VertexNova Technologies', industry: 'Cybersecurity', website: null, description: 'Tracks product updates, threat research, and enterprise security positioning.', is_demo: false },
  ],
  observations: [
    { id: 101, source_id: 1, company_id: 1, title: 'Automation platform packaging changed', body: 'Configured source record describing packaging and workflow changes. Source URLs are added when real monitoring is configured.', url: null, published_at: daysAgo(1), collected_at: daysAgo(1), is_demo: false },
    { id: 102, source_id: 2, company_id: 2, title: 'Partner analytics bundle announced', body: 'Configured source record describing a partner bundle for analytics teams.', url: null, published_at: daysAgo(3), collected_at: daysAgo(3), is_demo: false },
    { id: 103, source_id: 3, company_id: 3, title: 'Robotics deployment delayed', body: 'Configured source record describing supplier constraints and rollout risk.', url: null, published_at: daysAgo(5), collected_at: daysAgo(5), is_demo: false },
    { id: 104, source_id: 4, company_id: 4, title: 'Cloud compliance update published', body: 'Configured source record describing new compliance documentation.', url: null, published_at: daysAgo(8), collected_at: daysAgo(8), is_demo: false },
    { id: 105, source_id: 5, company_id: 5, title: 'Security incident response feature expanded', body: 'Configured source record describing incident-response product changes.', url: null, published_at: daysAgo(11), collected_at: daysAgo(11), is_demo: false },
  ],
  sources: [
    { id: 1, company_id: 1, kind: 'announcement', url: 'Configured product-announcement source', label: 'Product announcements', is_demo: false, enabled: true, last_status: 'configured', last_error: null, last_collected_at: daysAgo(1) },
    { id: 2, company_id: 2, kind: 'news', url: 'Configured market-news source', label: 'Market news', is_demo: false, enabled: true, last_status: 'configured', last_error: null, last_collected_at: daysAgo(3) },
    { id: 3, company_id: 3, kind: 'supplier', url: 'Configured supplier-signal source', label: 'Supplier updates', is_demo: false, enabled: true, last_status: 'configured', last_error: null, last_collected_at: daysAgo(5) },
    { id: 4, company_id: 4, kind: 'compliance', url: 'Configured compliance source', label: 'Compliance updates', is_demo: false, enabled: true, last_status: 'configured', last_error: null, last_collected_at: daysAgo(8) },
    { id: 5, company_id: 5, kind: 'security', url: 'Configured security research source', label: 'Security updates', is_demo: false, enabled: true, last_status: 'configured', last_error: null, last_collected_at: daysAgo(11) },
  ],
  events: [
    event(201, 1, 'Asterion Systems changed automation platform packaging', 'pricing_change', 'new', 1, 'high', 76, 'Packaging changes can influence renewal and migration conversations. Evidence quality is moderate because structured price fields are not connected yet.'),
    event(202, 2, 'Northstar Analytics launched a partner analytics bundle', 'partnership', 'reviewed', 3, 'medium', 58, 'Partner bundle may expand channel reach. Monitor adoption before escalating.'),
    event(203, 3, 'BluePeak Robotics reported deployment delay signals', 'supply_chain', 'new', 5, 'critical', 84, 'Supplier constraints may affect delivery commitments and competitor availability.'),
    event(204, 4, 'Meridian Cloudworks published compliance documentation update', 'regulatory_change', 'reviewed', 8, 'medium', 55, 'Compliance updates may influence regulated buyers and procurement timing.'),
    event(205, 5, 'VertexNova Technologies expanded incident-response workflow', 'product_launch', 'new', 11, 'high', 72, 'Product expansion may increase competitive pressure in security operations accounts.'),
    event(206, 2, 'Northstar Analytics opened regional hiring for enterprise sales', 'hiring_trend', 'new', 15, 'low', 38, 'Hiring trend suggests market coverage expansion, but urgency remains low.'),
  ],
  reports: [],
  workflows: [
    { id: 1, name: 'High-risk weekly briefing', enabled: true, company_ids: [1, 3, 5], categories: ['pricing_change', 'supply_chain', 'product_launch'], min_priority: 'high', report_type: 'weekly' },
  ],
  settings: { timezone: 'Asia/Kolkata', display_name: 'SentinelIQ Analyst', show_demo_data: false },
}

function event(id: number, company_id: number, title: string, category: string, status: string, days: number, priority: Priority, score: number, explanation: string): EventDetail {
  return {
    id, company_id, title, category, status, occurred_at: daysAgo(days), is_demo: false,
    evidence: [{ id: id + 1000, observation_id: company_id + 100, excerpt: `Evidence summary for: ${title}. Connect live sources to attach external URLs.`, verification_status: 'stored_record' }],
    predictions: [{ id: id + 2000, label: category, confidence: Math.min(0.94, score / 100 + 0.1), model_version: 'prototype-rules-v1' }],
    risk_assessments: [{ id: id + 3000, event_id: id, impact: Math.ceil(score / 14), urgency: Math.ceil(score / 15), strategic_relevance: Math.ceil(score / 13), evidence_quality: 6, overall_score: score, priority, explanation, created_at: daysAgo(days) }],
  }
}

function load(): Store {
  const raw = localStorage.getItem(STORE)
  if (!raw) {
    localStorage.setItem(STORE, JSON.stringify(seed))
    return seed
  }
  return JSON.parse(raw) as Store
}

function save(store: Store) {
  localStorage.setItem(STORE, JSON.stringify(store))
}

const page = <T,>(items: T[], offset = 0, limit = 20): Page<T> => ({ items: items.slice(offset, offset + limit), total: items.length, offset, limit })

export async function localGet<T>(url: string, params: Record<string, unknown> = {}): Promise<{ data: T }> {
  const store = load()
  const offset = Number(params.offset ?? 0)
  const limit = Number(params.limit ?? 20)
  const events = [...store.events].sort((a, b) => +new Date(b.occurred_at) - +new Date(a.occurred_at))
  if (url === '/analytics/overview') {
    const latest = store.sources.filter((s) => s.enabled).length
    return data({ companies: store.companies.length, observations: store.observations.length, events: store.events.length, new_events: store.events.filter((e) => e.status === 'new').length, high_priority: store.events.filter((e) => latestRisk(e).priority === 'high').length, critical: store.events.filter((e) => latestRisk(e).priority === 'critical').length, claims_awaiting_verification: 0, sources_ok: latest, sources_error: 0, sources_never_collected: 0, demo_events: 0, real_events: store.events.length, recommendations_awaiting_approval: store.events.filter((e) => e.status === 'new').length } as T)
  }
  if (url === '/analytics/timeline') return data(groupByDay(events) as T)
  if (url === '/analytics/categories') return data(countBy(events, 'category') as T)
  if (url === '/analytics/priorities') return data(countPriorities(events) as T)
  if (url === '/analytics/companies') return data(store.companies.map((c) => ({ company_id: c.id, name: c.name, events: events.filter((e) => e.company_id === c.id).length, observations: store.observations.filter((o) => o.company_id === c.id).length })) as T)
  if (url === '/companies') {
    const q = String(params.q ?? '').toLowerCase()
    return data(page(store.companies.filter((c) => !q || c.name.toLowerCase().includes(q) || c.industry?.toLowerCase().includes(q)), offset, limit) as T)
  }
  const company = url.match(/^\/companies\/(\d+)$/)?.[1]
  if (company) return data(store.companies.find((c) => c.id === Number(company)) as T)
  const companySources = url.match(/^\/companies\/(\d+)\/sources$/)?.[1]
  if (companySources) return data(store.sources.filter((s) => s.company_id === Number(companySources)) as T)
  const companyEvents = url.match(/^\/companies\/(\d+)\/events$/)?.[1]
  if (companyEvents) return data(page(events.filter((e) => e.company_id === Number(companyEvents)), offset, limit) as T)
  if (url.includes('/relationships')) return data([] as T)
  if (url === '/observations') return data(page(store.observations.filter((o) => !params.company_id || o.company_id === Number(params.company_id)), offset, limit) as T)
  if (url === '/events') {
    const q = String(params.q ?? '').toLowerCase()
    const filtered = events.filter((e) => (!q || e.title.toLowerCase().includes(q) || companyName(store, e.company_id).toLowerCase().includes(q)) && (!params.company_id || e.company_id === Number(params.company_id)) && (!params.category || e.category === params.category))
    return data(page<EventItem>(filtered, offset, limit) as T)
  }
  const eventId = url.match(/^\/events\/(\d+)$/)?.[1]
  if (eventId) return data(store.events.find((e) => e.id === Number(eventId)) as T)
  const insightId = url.match(/^\/events\/(\d+)\/insights$/)?.[1]
  if (insightId) return data(insight(store, Number(insightId)) as T)
  const decisionId = url.match(/^\/events\/(\d+)\/decision-support$/)?.[1]
  if (decisionId) return data(decisions() as T)
  if (url === '/risk-assessments') return data(page<Risk>(store.events.map(latestRisk).filter((r) => !params.priority || r.priority === params.priority), offset, limit) as T)
  if (url === '/reports') return data(page(store.reports, offset, limit) as T)
  if (url === '/workflows') return data(page(store.workflows, offset, limit) as T)
  if (url === '/settings') return data(store.settings as T)
  if (url === '/sources') return data(page(store.sources, offset, limit) as T)
  return data(null as T)
}

export async function localPost<T>(url: string, body?: unknown): Promise<{ data: T }> {
  const store = load()
  if (url === '/companies') {
    const input = body as Partial<Company>
    const row: Company = { id: Date.now(), name: input.name ?? 'Untitled company', industry: input.industry ?? null, website: input.website ?? null, description: input.description ?? null, is_demo: false }
    store.companies.unshift(row); save(store); return data(row as T)
  }
  if (url === '/reports') {
    const input = body as { company_id?: number }
    const items = store.events.filter((e) => !input.company_id || e.company_id === input.company_id)
    const report: Report = { id: Date.now(), report_type: 'briefing', title: `Intelligence briefing - ${new Date().toLocaleDateString()}`, company_id: input.company_id ?? null, is_demo: false, created_at: new Date().toISOString(), content_json: { events: items.length, companies: [...new Set(items.map((e) => companyName(store, e.company_id)))] }, content_markdown: renderReport(store, items) }
    store.reports.unshift(report); save(store); return data(report as T)
  }
  if (url === '/workflows') {
    const input = body as Partial<Workflow>
    const row: Workflow = { id: Date.now(), name: input.name ?? 'Untitled workflow', enabled: true, company_ids: input.company_ids ?? [], categories: input.categories ?? [], min_priority: input.min_priority ?? 'medium', report_type: input.report_type ?? 'weekly' }
    store.workflows.unshift(row); save(store); return data(row as T)
  }
  if (url.includes('/execute')) return data({ reports_created: 1, simulated: 1 } as T)
  return data({ ok: true } as T)
}

export async function localPatch<T>(url: string, body?: unknown): Promise<{ data: T }> {
  const store = load()
  const eventId = url.match(/^\/events\/(\d+)$/)?.[1]
  if (eventId) {
    const ev = store.events.find((e) => e.id === Number(eventId))
    if (ev) Object.assign(ev, body)
    save(store); return data(ev as T)
  }
  const companyId = url.match(/^\/companies\/(\d+)$/)?.[1]
  if (companyId) {
    const row = store.companies.find((c) => c.id === Number(companyId))
    if (row) Object.assign(row, body)
    save(store); return data(row as T)
  }
  return data({ ok: true } as T)
}

export async function localDelete<T>(url: string): Promise<{ data: T }> {
  const store = load()
  const companyId = url.match(/^\/companies\/(\d+)$/)?.[1]
  if (companyId) store.companies = store.companies.filter((c) => c.id !== Number(companyId))
  save(store)
  return data({ ok: true } as T)
}

export async function localPut<T>(url: string, body?: unknown): Promise<{ data: T }> {
  const store = load()
  if (url === '/settings') store.settings = body as Settings
  save(store)
  return data((body ?? { ok: true }) as T)
}

function data<T>(data: T) { return Promise.resolve({ data }) }
function companyName(store: Store, id: number) { return store.companies.find((c) => c.id === id)?.name ?? `Company ${id}` }
function latestRisk(e: EventDetail) { return e.risk_assessments[0] }
function countBy(events: EventDetail[], key: 'category') {
  const counts = new Map<string, number>()
  events.forEach((e) => counts.set(e[key], (counts.get(e[key]) ?? 0) + 1))
  return [...counts].map(([category, count]) => ({ category, count }))
}
function countPriorities(events: EventDetail[]) {
  return (['critical', 'high', 'medium', 'low'] as const).map((priority) => ({ priority, count: events.filter((e) => latestRisk(e).priority === priority).length }))
}
function groupByDay(events: EventDetail[]) {
  const counts = new Map<string, number>()
  events.forEach((e) => { const day = e.occurred_at.slice(0, 10); counts.set(day, (counts.get(day) ?? 0) + 1) })
  return [...counts].sort(([a], [b]) => a.localeCompare(b)).map(([date, events]) => ({ date, events }))
}
function insight(store: Store, eventId: number): EventInsight {
  const ev = store.events.find((e) => e.id === eventId) ?? store.events[0]
  return { summary: `${companyName(store, ev.company_id)} has a ${ev.category.replace(/_/g, ' ')} event with ${latestRisk(ev).priority} priority based on stored evidence and transparent scoring.`, source_facts: ev.evidence.map((x) => ({ observation_id: x.observation_id, title: ev.title, source_url: null, excerpt: x.excerpt })), model_signal: ev.predictions[0] ?? null, risk_signal: { priority: latestRisk(ev).priority, overall_score: latestRisk(ev).overall_score, explanation: latestRisk(ev).explanation }, possible_implications: ['May affect active account strategy.', 'Could change competitive positioning.', 'Warrants review against watchlist priorities.'], uncertainties: ['External source URLs are not connected in this frontend-only phase.', 'Impact should be validated with business context.'], missing_information: ['Source URL', 'Affected segment', 'Duration of change'], suggested_actions: ['Review supporting evidence.', 'Assign an analyst owner.', 'Track follow-up observations.'], provider: 'deterministic prototype rules' }
}
function decisions(): DecisionSupport {
  return { disclaimer: 'Options are generated from deterministic prototype rules for review planning only.', options: [
    { name: 'Monitor only', benefits: ['Avoids overreacting to weak evidence.'], drawbacks: ['May delay response.'], assumptions: ['The signal remains low urgency.'], next_steps: ['Add to watchlist and revisit after new observations.'] },
    { name: 'Assign analyst review', benefits: ['Improves evidence quality before action.'], drawbacks: ['Requires team capacity.'], assumptions: ['An owner can validate context.'], next_steps: ['Create an internal review task.'] },
    { name: 'Prepare response brief', benefits: ['Keeps stakeholders ready.'], drawbacks: ['May be premature if evidence changes.'], assumptions: ['The event is strategically relevant.'], next_steps: ['Draft scenarios and decision criteria.'] },
  ] }
}
function renderReport(store: Store, events: EventDetail[]) {
  const rows = events.map((e) => `- ${companyName(store, e.company_id)}: ${e.title} (${latestRisk(e).priority}, score ${latestRisk(e).overall_score})`).join('\n')
  return `# SentinelIQ Intelligence Briefing\n\nGenerated: ${new Date().toLocaleString()}\n\n## Executive summary\n${events.length} event(s) match the selected report configuration.\n\n## Key events\n${rows || 'No matching events.'}\n\n## Limitations\nThis frontend-only prototype uses configured local records. Connect live sources before treating findings as operational intelligence.\n`
}
