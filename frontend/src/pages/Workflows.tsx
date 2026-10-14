import { useState } from 'react'
import { Play, Plus, Workflow as WorkflowIcon } from 'lucide-react'
import { api, errMsg } from '../api/client'
import { useFetch } from '../hooks/useFetch'
import { Button, Card, Empty, ErrorBox, Input, PageTitle, SuccessBox, Tag } from '../components/ui'
import type { Page, Workflow } from '../types'

export default function Workflows() {
  const list = useFetch<Page<Workflow>>('/workflows', { limit: 50 })
  const [name, setName] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [message, setMessage] = useState<string | null>(null)
  const [busy, setBusy] = useState<number | null>(null)

  async function create() {
    if (!name.trim()) return
    setError(null)
    setMessage(null)
    try {
      await api.post('/workflows', { name: name.trim(), report_type: 'daily', min_priority: 'low' })
      setName('')
      setMessage('Workflow created.')
      list.reload()
    } catch (e) {
      setError(errMsg(e))
    }
  }

  async function execute(id: number) {
    setBusy(id)
    setError(null)
    setMessage(null)
    try {
      const response = await api.post<{ reports_created: number; simulated: number }>(`/workflows/${id}/execute`)
      setMessage(`Workflow executed: ${response.data.reports_created} report(s), ${response.data.simulated} simulated delivery(s).`)
    } catch (e) {
      setError(errMsg(e))
    } finally {
      setBusy(null)
    }
  }

  return (
    <div className="space-y-5">
      <PageTitle title="Alerts and workflows" subtitle="Configure report runs and review delivery outcomes from persisted intelligence." />
      {error && <ErrorBox message={error} />}
      {message && <SuccessBox message={message} />}
      <Card title="Create workflow">
        <div className="flex flex-wrap gap-2">
          <Input className="min-w-72 flex-1" placeholder="Workflow name" value={name} onChange={(e) => setName(e.target.value)} />
          <Button disabled={!name.trim()} onClick={create}><Plus className="mr-1 inline h-4 w-4" />Create</Button>
        </div>
      </Card>
      <Card title="Configured workflows">
        {list.loading && !list.data && <div className="p-4 text-sm text-slate-400">Loading workflows...</div>}
        {list.error && <ErrorBox message={list.error} />}
        {list.data && list.data.items.length === 0 && <Empty title="No workflows configured" hint="Create a workflow to generate reports from persisted intelligence." />}
        {list.data && list.data.items.length > 0 && (
          <div className="divide-y divide-[#263650]">
            {list.data.items.map((workflow) => (
              <div key={workflow.id} className="flex flex-wrap items-center justify-between gap-3 py-3">
                <div className="flex items-start gap-3">
                  <WorkflowIcon className="mt-0.5 h-5 w-5 text-cyan-300" />
                  <div>
                    <div className="font-medium text-slate-100">{workflow.name}</div>
                    <div className="mt-1 flex flex-wrap gap-1 text-xs">
                      <Tag>{workflow.report_type}</Tag>
                      <Tag>minimum priority: {workflow.min_priority}</Tag>
                      <Tag>{workflow.enabled ? 'enabled' : 'disabled'}</Tag>
                    </div>
                  </div>
                </div>
                <Button disabled={busy === workflow.id} onClick={() => execute(workflow.id)}>
                  <Play className="mr-1 inline h-4 w-4" />{busy === workflow.id ? 'Running...' : 'Run now'}
                </Button>
              </div>
            ))}
          </div>
        )}
      </Card>
    </div>
  )
}
