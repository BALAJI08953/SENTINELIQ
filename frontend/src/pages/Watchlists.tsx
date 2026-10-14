import { useMemo, useState } from 'react'
import { Plus, Trash2 } from 'lucide-react'
import { Button, Card, Empty, Input, PageTitle, Tag } from '../components/ui'
import { useFetch } from '../hooks/useFetch'
import type { Company, Page } from '../types'

type Watchlist = { id: string; name: string; companies: number[]; topics: string[] }
const KEY = 'sentineliq.watchlists'
const initial: Watchlist[] = [{ id: 'enterprise-threats', name: 'Enterprise threats', companies: [1, 3, 5], topics: ['product_launch', 'supply_chain', 'cybersecurity'] }]

const read = () => JSON.parse(localStorage.getItem(KEY) ?? JSON.stringify(initial)) as Watchlist[]
const write = (items: Watchlist[]) => localStorage.setItem(KEY, JSON.stringify(items))

export default function Watchlists() {
  const companies = useFetch<Page<Company>>('/companies', { limit: 200 })
  const [items, setItems] = useState<Watchlist[]>(read)
  const [name, setName] = useState('')
  const names = useMemo(() => new Map(companies.data?.items.map((c) => [c.id, c.name])), [companies.data])

  const persist = (next: Watchlist[]) => { setItems(next); write(next) }
  const add = () => {
    if (!name.trim()) return
    persist([{ id: String(Date.now()), name: name.trim(), companies: [], topics: [] }, ...items])
    setName('')
  }
  const toggleCompany = (list: Watchlist, id: number) => {
    const companies = list.companies.includes(id) ? list.companies.filter((x) => x !== id) : [...list.companies, id]
    persist(items.map((item) => item.id === list.id ? { ...item, companies } : item))
  }

  return (
    <div className="space-y-4">
      <PageTitle title="Watchlists" subtitle="Create saved groups of companies and topics for focused monitoring." />
      <Card title="Create watchlist">
        <div className="flex gap-2"><Input className="flex-1" placeholder="Watchlist name" value={name} onChange={(e) => setName(e.target.value)} /><Button onClick={add}><Plus className="mr-1 inline h-4 w-4" />Create</Button></div>
      </Card>
      {items.length === 0 ? <Card><Empty title="No watchlists" hint="Create a watchlist to group tracked companies." /></Card> : items.map((list) => (
        <Card key={list.id} title={list.name} right={<button className="text-rose-300" onClick={() => persist(items.filter((x) => x.id !== list.id))}><Trash2 className="h-4 w-4" /></button>}>
          <div className="flex flex-wrap gap-2">{companies.data?.items.map((company) => <button key={company.id} className={`rounded-md border px-2 py-1 text-sm ${list.companies.includes(company.id) ? 'border-cyan-300/40 bg-cyan-300/10 text-cyan-100' : 'border-[#263650] text-slate-400'}`} onClick={() => toggleCompany(list, company.id)}>{company.name}</button>)}</div>
          <div className="mt-3 flex flex-wrap gap-1 text-xs">{list.companies.length === 0 ? <span className="text-slate-500">No companies selected</span> : list.companies.map((id) => <Tag key={id}>{names.get(id) ?? `Company ${id}`}</Tag>)}</div>
        </Card>
      ))}
    </div>
  )
}
