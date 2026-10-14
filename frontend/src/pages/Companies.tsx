import { useState } from 'react'
import { Link } from 'react-router-dom'
import { api, errMsg } from '../api/client'
import { useFetch } from '../hooks/useFetch'
import { Async, Button, Card, DemoTag, Empty, ErrorBox, Input, PageTitle, Pager, linkClass } from '../components/ui'
import type { Company, Page } from '../types'

export default function Companies() {
  const [q, setQ] = useState('')
  const [offset, setOffset] = useState(0)
  const [name, setName] = useState('')
  const [industry, setIndustry] = useState('')
  const [website, setWebsite] = useState('')
  const [err, setErr] = useState<string | null>(null)
  const [msg, setMsg] = useState<string | null>(null)
  const list = useFetch<Page<Company>>('/companies', { q: q || undefined, offset, limit: 10 })

  async function add() {
    setErr(null)
    setMsg(null)
    if (name.trim().length < 2) {
      setErr('Enter a company name with at least 2 characters.')
      return
    }
    if (website && !/^https?:\/\/.+/i.test(website)) {
      setErr('Website must start with http:// or https://.')
      return
    }
    try {
      await api.post('/companies', { name, industry: industry || null, website: website || null })
      setName('')
      setIndustry('')
      setWebsite('')
      list.reload()
    } catch (e) {
      setErr(errMsg(e))
    }
  }

  async function remove(c: Company) {
    if (!window.confirm(`Delete ${c.name} and all its sources, observations and events?`)) return
    try {
      await api.delete(`/companies/${c.id}`)
      list.reload()
    } catch (e) {
      setErr(errMsg(e))
    }
  }

  return (
    <>
      <PageTitle title="Companies" subtitle="Track competitors, customers, and market actors with evidence-linked sources." />
      <Card title="Add company">
        <div className="flex flex-wrap gap-2">
          <Input placeholder="Name *" value={name} onChange={(e) => setName(e.target.value)} />
          <Input placeholder="Industry" value={industry} onChange={(e) => setIndustry(e.target.value)} />
          <Input placeholder="https://website" value={website} onChange={(e) => setWebsite(e.target.value)} />
          <Button disabled={!name.trim()} onClick={add}>Add</Button>
        </div>
        {err && <div className="mt-2"><ErrorBox message={err} /></div>}{msg && <div className="mt-2 text-sm text-cyan-200">{msg}</div>}
      </Card>
      <Card title="Monitored companies" right={<Input placeholder="Search..." value={q} onChange={(e) => { setQ(e.target.value); setOffset(0) }} />}>
        <Async state={list}>{(p) => p.items.length === 0 ? <Empty title="No companies found" hint="Add one above or run the seed script." /> : (
          <>
            <ul className="divide-y divide-[#263650]">{p.items.map((c) => (
              <li key={c.id} className="flex flex-wrap items-center gap-2 py-2">
                <Link className={linkClass} to={`/companies/${c.id}`}>{c.name}</Link>
                <span className="text-sm text-slate-400">{c.industry ?? 'industry unknown'}</span><DemoTag demo={c.is_demo} />
                <span className="ml-auto text-xs text-slate-500">monitoring status: configured</span>
                <button className="text-sm text-rose-300 hover:underline" onClick={() => remove(c)}>Delete</button>
              </li>
            ))}</ul>
            <Pager total={p.total} offset={p.offset} limit={p.limit} onChange={setOffset} />
          </>
        )}</Async>
      </Card>
    </>
  )
}
