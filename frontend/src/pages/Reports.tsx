import { useState } from 'react'
import { Download, FileText, Plus } from 'lucide-react'
import { api, errMsg } from '../api/client'
import { Button, Card, Empty, ErrorBox, Loading, PageTitle } from '../components/ui'
import { useFetch } from '../hooks/useFetch'
import type { Company, Page, Report } from '../types'

export default function Reports() {
  const companies = useFetch<Page<Company>>('/companies', { limit: 100 })
  const [companyId, setCompanyId] = useState('')
  const reports = useFetch<Page<Report>>('/reports', { limit: 20 })
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)

  async function generate() {
    if (!companyId) return
    setBusy(true)
    setError(null)
    try {
      await api.post<Report>('/reports', { company_id: Number(companyId) })
      reports.reload()
    } catch (e) {
      setError(errMsg(e))
    } finally {
      setBusy(false)
    }
  }

  const exportClass = 'inline-flex items-center rounded-md border border-cyan-300/30 bg-[#0B1020]/70 px-2 py-1.5 text-sm text-cyan-100 shadow-sm transition hover:bg-[#111B32]'
  const downloadHref = (report: Report, format: 'markdown' | 'json') => `/api/v1/reports/${report.id}/export?format=${format}`

  return (
    <div className="space-y-5">
      <PageTitle title="Reports" subtitle="Generate evidence-backed Markdown and JSON exports from persisted intelligence." />
      <Card title="Generate a report">
        {companies.loading && <Loading />}
        {companies.error && <ErrorBox message={companies.error} />}
        {companies.data && (
          <div className="flex flex-wrap items-end gap-3">
            <label className="text-sm text-slate-300">
              Company
              <select className="mt-1 block min-w-56 px-2 py-1.5 text-sm" value={companyId} onChange={(e) => setCompanyId(e.target.value)}>
                <option value="">Select a company</option>
                {companies.data.items.map((company) => <option key={company.id} value={company.id}>{company.name}</option>)}
              </select>
            </label>
            <Button type="button" disabled={!companyId || busy} onClick={generate}>
              <Plus className="mr-1 inline h-4 w-4" />{busy ? 'Generating...' : 'Generate report'}
            </Button>
          </div>
        )}
        {error && <div className="mt-3"><ErrorBox message={error} /></div>}
      </Card>
      <Card title="Generated reports">
        {reports.loading && !reports.data && <Loading />}
        {reports.error && <ErrorBox message={reports.error} />}
        {reports.data && reports.data.items.length === 0 && <Empty title="No reports yet" hint="Choose a company above to create the first report." />}
        {reports.data && reports.data.items.length > 0 && (
          <div className="divide-y divide-[#263650]">
            {reports.data.items.map((report) => (
              <div key={report.id} className="flex flex-wrap items-center justify-between gap-3 py-3">
                <div className="flex items-start gap-3">
                  <FileText className="mt-0.5 h-5 w-5 text-cyan-300" />
                  <div>
                    <div className="font-medium text-slate-100">{report.title}</div>
                    <div className="text-xs text-slate-500">{new Date(report.created_at).toLocaleString()}</div>
                  </div>
                </div>
                <div className="flex gap-2">
                  <a className={exportClass} href={downloadHref(report, 'markdown')} download>
                    <Download className="mr-1 h-4 w-4" />Markdown
                  </a>
                  <a className={exportClass} href={downloadHref(report, 'json')} download>
                    <Download className="mr-1 h-4 w-4" />JSON
                  </a>
                </div>
              </div>
            ))}
          </div>
        )}
      </Card>
    </div>
  )
}
