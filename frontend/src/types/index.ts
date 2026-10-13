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
export interface Overview { companies: number; observations: number; events: number; new_events: number; high_priority: number; critical: number; claims_awaiting_verification: number; sources_ok: number; sources_error: number; sources_never_collected: number; demo_events: number; real_events: number }
export interface Settings { timezone: string; display_name: string | null; show_demo_data: boolean }
export type Priority = 'low' | 'medium' | 'high' | 'critical'
export const CATEGORIES = ['pricing_change', 'product_launch', 'partnership', 'funding', 'leadership_change', 'regulatory_change', 'acquisition', 'expansion', 'other']
