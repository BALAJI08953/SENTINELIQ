import { useEffect, useState } from 'react'
import { api, errMsg } from '../api/client'
import { useFetch } from '../hooks/useFetch'
import { Async, Button, Card, ErrorBox, Input } from '../components/ui'
import type { Settings as S } from '../types'

export default function Settings() {
  const st = useFetch<S>('/settings')
  const [form, setForm] = useState<S | null>(null)
  const [msg, setMsg] = useState<string | null>(null)
  const [err, setErr] = useState<string | null>(null)
  useEffect(() => { if (st.data) setForm(st.data) }, [st.data])
  async function save() {
    if (!form) return
    setErr(null); setMsg(null)
    try { await api.put('/settings', form); setMsg('Settings saved.') } catch (e) { setErr(errMsg(e)) }
  }
  return (
    <>
      <h1 className="text-xl font-bold text-slate-50">Settings</h1>
      <p className="text-sm text-slate-400">Connection and data settings for the SentinelIQ workspace.</p>
      <div className="grid gap-3 md:grid-cols-2">
        <Card title="Backend connection">
          <div className="flex items-center gap-2 text-sm text-amber-200"><span className="h-2.5 w-2.5 rounded-full bg-amber-300" />Live API is checked through the Vite proxy at <code className="text-cyan-200">/api/v1</code>.</div>
          <p className="mt-2 text-xs text-slate-500">When the backend is unavailable, the workspace shows an operational error and retry action.</p>
        </Card>
        <Card title="Data mode">
          <div className="flex items-center gap-2 text-sm text-violet-200"><span className="h-2.5 w-2.5 rounded-full bg-violet-300" />Configured sources determine which records appear.</div>
          <p className="mt-2 text-xs text-slate-500">Only persisted records returned by the backend are displayed.</p>
        </Card>
      </div>
      <Card>
        <Async state={st}>{() => form && (
          <div className="space-y-3 text-sm">
            <label className="block">Display name<Input className="ml-2" value={form.display_name ?? ''} onChange={(e) => setForm({ ...form, display_name: e.target.value || null })} /></label>
            <label className="block">Timezone (IANA, e.g. Asia/Kolkata)<Input className="ml-2" value={form.timezone} onChange={(e) => setForm({ ...form, timezone: e.target.value })} /></label>
            <label className="flex items-center gap-2"><input type="checkbox" checked={form.show_demo_data} onChange={(e) => setForm({ ...form, show_demo_data: e.target.checked })} />Include records flagged for review</label>
            <Button onClick={save}>Save</Button>
          </div>)}</Async>
        {err && <div className="mt-3"><ErrorBox message={err} /></div>}{msg && <div className="mt-3 text-sm text-green-700">{msg}</div>}
      </Card>
    </>
  )
}
