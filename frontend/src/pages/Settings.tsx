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
      <h1 className="text-xl font-bold">Settings</h1>
      <Card>
        <Async state={st}>{() => form && (
          <div className="space-y-3 text-sm">
            <label className="block">Display name<Input className="ml-2" value={form.display_name ?? ''} onChange={(e) => setForm({ ...form, display_name: e.target.value || null })} /></label>
            <label className="block">Timezone (IANA, e.g. Asia/Kolkata)<Input className="ml-2" value={form.timezone} onChange={(e) => setForm({ ...form, timezone: e.target.value })} /></label>
            <label className="flex items-center gap-2"><input type="checkbox" checked={form.show_demo_data} onChange={(e) => setForm({ ...form, show_demo_data: e.target.checked })} />Show demo data (stored preference; filtering is not applied yet)</label>
            <Button onClick={save}>Save</Button>
          </div>)}</Async>
        {err && <div className="mt-3"><ErrorBox message={err} /></div>}{msg && <div className="mt-3 text-sm text-green-700">{msg}</div>}
      </Card>
    </>
  )
}
