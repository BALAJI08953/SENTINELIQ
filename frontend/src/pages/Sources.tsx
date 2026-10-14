import { useState } from 'react'
import { Rss } from 'lucide-react'
import { api, errMsg } from '../api/client'
import { Button, Card, Empty, ErrorBox, Input, PageTitle, Tag } from '../components/ui'
import { useFetch } from '../hooks/useFetch'
import type { Company, Page, Source } from '../types'
import { fmtDate } from '../utils/format'

export default function Sources() {
  const sources = useFetch<Page<Source>>('/sources', { limit: 100 })
  const companies = useFetch<Page<Company>>('/companies', { limit: 200 })
  const [companyId, setCompanyId] = useState('')
  const [kind, setKind] = useState<'rss' | 'html'>('rss')
  const [url, setUrl] = useState('')
  const [label, setLabel] = useState('')
  const [error, setError] = useState<string | null>(null)
  async function add() {
    if (!companyId || !url.trim()) return
    try {
      setError(null)
      await api.post(`/companies/${companyId}/sources`, { kind, url: url.trim(), label: label.trim() || null })
      setUrl('')
      setLabel('')
      sources.reload()
    } catch (e) { setError(errMsg(e)) }
  }
  return (
    <div className="space-y-4">
      <PageTitle title="Sources" subtitle="Configure permitted RSS and HTML sources, then collect them into persisted observations and evidence-linked events." />
      {error && <ErrorBox message={error} />}
      <Card title="Add source configuration">
        <div className="flex flex-wrap gap-2">
          <select className="px-2 py-1.5 text-sm" value={companyId} onChange={(e) => setCompanyId(e.target.value)}><option value="">Select company</option>{companies.data?.items.map((company) => <option key={company.id} value={company.id}>{company.name}</option>)}</select>
          <select className="px-2 py-1.5 text-sm" value={kind} onChange={(e) => setKind(e.target.value as 'rss' | 'html')}><option value="rss">RSS</option><option value="html">HTML</option></select>
          <Input className="min-w-64 flex-1" placeholder="https://..." value={url} onChange={(e) => setUrl(e.target.value)} />
          <Input placeholder="Label (optional)" value={label} onChange={(e) => setLabel(e.target.value)} />
          <Button disabled={!companyId || !url.trim()} onClick={add}>Add configuration</Button>
        </div>
        <p className="mt-2 text-xs text-slate-500">After registration, collect the source from the company profile. Only use sources you are permitted to access.</p>
      </Card>
      <Card title="Configured sources">
        {sources.data?.items.length === 0 ? <Empty title="No sources configured" /> : <div className="divide-y divide-[#263650]">{sources.data?.items.map((source) => <div key={source.id} className="flex flex-wrap items-center gap-2 py-3 text-sm"><Rss className="h-4 w-4 text-cyan-300" /><span className="font-medium text-slate-100">{source.label ?? source.kind}</span><Tag>{source.kind}</Tag><Tag>{source.enabled ? 'enabled' : 'disabled'}</Tag><span className="ml-auto text-xs text-slate-500">last checked {fmtDate(source.last_collected_at)}</span></div>)}</div>}
      </Card>
    </div>
  )
}
