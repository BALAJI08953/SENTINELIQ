import { useState } from 'react'
import { Link } from 'react-router-dom'
import { api, errMsg } from '../api/client'
import { useFetch } from '../hooks/useFetch'
import { Async, Button, Card, DemoTag, Empty, ErrorBox, Input, Pager } from '../components/ui'
import type { Company, Page } from '../types'

export default function Companies() {
  const [q, setQ] = useState('')
  const [offset, setOffset] = useState(0)
  const [name, setName] = useState('')
  const [industry, setIndustry] = useState('')
  const [website, setWebsite] = useState('')
  const [err, setErr] = useState<string | null>(null)
  const list = useFetch<Page<Company>>('/companies', { q: q || undefined, offset, limit: 10 })

  async function add() {
    setErr(null)
    try {
      await api.post('/companies', { name, industry: industry || null, website: website || null })
      setName(''); setIndustry(''); setWebsite(''); list.reload()
    } catch (e) { setErr(errMsg(e)) }
  }
  async function remove(c: Company) {
    if (!window.confirm(`Delete ${c.name} and all its sources, observations and events?`)) return
    try { await api.delete(`/companies/${c.id}`); list.reload() } catch (e) { setErr(errMsg(e)) }
  }
  return (
    <>
      <h1 className="text-xl font-bold">Companies</h1>
      <Card title="Add company">
        <div className="flex flex-wrap gap-2">
          <Input placeholder="Name *" value={name} onChange={(e) => setName(e.target.value)} />
          <Input placeholder="Industry" value={industry} onChange={(e) => setIndustry(e.target.value)} />
          <Input placeholder="https://website" value={website} onChange={(e) => setWebsite(e.target.value)} />
          <Button disabled={!name.trim()} onClick={add}>Add</Button>
        </div>
        {err && <div className="mt-2"><ErrorBox message={err} /></div>}
      </Card>
      <Card title="Monitored companies" right={<Input placeholder="Search…" value={q} onChange={(e) => { setQ(e.target.value); setOffset(0) }} />}>
        <Async state={list}>{(p) => p.items.length === 0 ? <Empty title="No companies found" hint="Add one above or run the seed script." /> : (
          <>
            <ul className="divide-y">{p.items.map((c) => (
              <li key={c.id} className="flex flex-wrap items-center gap-2 py-2">
                <Link className="font-medium text-blue-700 hover:underline" to={`/companies/${c.id}`}>{c.name}</Link>
                <span className="text-sm text-slate-500">{c.industry ?? 'industry unknown'}</span><DemoTag demo={c.is_demo} />
                <button className="ml-auto text-sm text-red-600 hover:underline" onClick={() => remove(c)}>Delete</button>
              </li>))}</ul>
            <Pager total={p.total} offset={p.offset} limit={p.limit} onChange={setOffset} />
          </>)}</Async>
      </Card>
    </>
  )
}
