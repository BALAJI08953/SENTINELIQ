export interface Page<T> { items: T[]; total: number; offset: number; limit: number }
export interface Company { id: number; name: string; website: string | null; industry: string | null; description: string | null; is_demo: boolean }
export interface Source { id: number; company_id: number; kind: string; url: string; label: string | null; is_demo: boolean; enabled: boolean; last_status: string | null; last_error: string | null; last_collected_at: string | null }
export interface Observation { id: number; source_id: number; company_id: number; title: string; body: string; url: string | null; published_at: string | null; collected_at: string; is_demo: boolean }
export interface Evidence { id: number; observation_id: number; excerpt: string | null; verification_status: string }
export interface Prediction { id: number; label: string; confidence: number; model_version: string }
export interface Risk { id: number; event_id: number; impact: number; urgency: number; strategic_relevance: number; evidence_quality: number; overall_score: number; priority: Priority; explanation: string; created_at: string }
export interface EventItem { id: number; company_id: number; title: string; category: string; status: string; occurred_at: string; is_demo: boolean }
export interface EventDetail extends EventItem { evidence: Evidence[]; predictions: Prediction[]; risk_assessments: Risk[] }
export interface Relationship { id: number; company_id: number; related_company_id: number; relationship_type: string; verification_status: string; evidence_observation_id: number | null }
export interface Overview { companies: number; observations: number; events: number; new_events: number; high_priority: number; critical: number; claims_awaiting_verification: number; sources_ok: number; sources_error: number; sources_never_collected: number; demo_events: number; real_events: number; recommendations_awaiting_approval?: number }
export interface Settings { timezone: string; display_name: string | null; show_demo_data: boolean }
export interface Report {
  id: number
  report_type: string
  title: string
  company_id: number | null
  content_json: Record<string, unknown>
  content_markdown: string
  is_demo: boolean
  created_at: string
}
export interface Workflow {
  id: number
  name: string
  enabled: boolean
  company_ids: number[]
  categories: string[]
  min_priority: Priority
  report_type: string
  channel?: string
  schedule?: string
  timezone?: string
  recipients?: string[]
}
export interface EventInsight {
  summary: string
  source_facts: { observation_id: number; title: string; source_url: string | null; excerpt: string | null }[]
  evidence_assessments?: { evidence_id: number; observation_id: number; text_match: boolean; provenance: boolean; source_accessible: boolean; claim_consistency: string; corroboration: string; conflicting_evidence: boolean; verification_status: string; limitation: string }[]
  model_signal: { label: string; confidence: number; model_version: string } | null
  risk_signal: { priority: string; overall_score: number; explanation: string } | null
  possible_implications: string[]
  uncertainties: string[]
  missing_information: string[]
  suggested_actions: string[]
  provider: string
}
export interface DecisionSupport {
  disclaimer: string
  options: { name: string; benefits: string[]; drawbacks: string[]; assumptions: string[]; next_steps: string[] }[]
}
export interface SentrixCitation {
  id: number
  type: string
  record_id: number
  title: string
  url: string | null
  published_at: string | null
  collected_at: string
  source_status: string | null
  verification_status: string
  excerpt: string | null
}
export interface SentrixResponse {
  assistant: 'SENTRIX'
  answer: string
  provider: string
  citations: SentrixCitation[]
  records: { companies: number[]; events: number[]; experiments: string[] }
}
export interface WorkflowTask {
  id: string
  title: string
  related_company: string
  event_id: number
  created_at: string
  status: 'Pending' | 'In Progress' | 'Completed'
  recommendation: string
  next_step: string
  is_demo: boolean
}
export type Priority = 'low' | 'medium' | 'high' | 'critical'
export const CATEGORIES = ['pricing_change', 'product_launch', 'partnership', 'funding', 'leadership_change', 'regulatory_change', 'acquisition', 'expansion', 'supply_chain', 'cybersecurity', 'hiring_trend', 'other']
