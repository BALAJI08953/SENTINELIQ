import { useState } from 'react'
import { Copy, MessageCircle, Send } from 'lucide-react'
import { api, errMsg } from '../api/client'
import { Button, Card, ErrorBox, Input, Loading, PageTitle, SuccessBox } from '../components/ui'
import { useFetch } from '../hooks/useFetch'
import type { Company, Page, SentrixResponse } from '../types'

type Message = { role: 'user' | 'assistant'; text: string; response?: SentrixResponse }

const suggestions = [
  'Summarize the latest developments for the selected company.',
  'Which events have the highest risk scores, and why?',
  'What information is missing before we can assess this company confidently?',
  'Explain my latest ML experiment in simple terms.',
]

export default function Sentrix() {
  const companies = useFetch<Page<Company>>('/companies', { limit: 200 })
  const [companyId, setCompanyId] = useState('')
  const [message, setMessage] = useState('')
  const [history, setHistory] = useState<Message[]>([])
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [copied, setCopied] = useState(false)

  async function send(text = message) {
    if (!text.trim()) return
    setBusy(true)
    setError(null)
    setMessage('')
    setHistory((items) => [...items, { role: 'user', text }])
    try {
      const response = await api.post<SentrixResponse>('/sentrix/chat', {
        message: text,
        company_id: companyId ? Number(companyId) : null,
      })
      setHistory((items) => [...items, { role: 'assistant', text: response.data.answer, response: response.data }])
    } catch (e) {
      setError(errMsg(e))
    } finally {
      setBusy(false)
    }
  }

  const latest = [...history].reverse().find((item) => item.role === 'assistant')

  return (
    <div className="space-y-4">
      <PageTitle title="SENTRIX Assistant" subtitle="Grounded conversational intelligence over SentinelIQ records, evidence, reports, and ML experiments." />
      {error && <ErrorBox message={error} />}
      <Card title="Conversation context">
        <div className="flex flex-wrap items-center gap-2">
          <label className="text-sm text-slate-300">
            Company
            <select className="ml-2 px-2 py-1.5 text-sm" value={companyId} onChange={(e) => setCompanyId(e.target.value)}>
              <option value="">All stored records</option>
              {companies.data?.items.map((company) => <option key={company.id} value={company.id}>{company.name}</option>)}
            </select>
          </label>
          <span className="text-xs text-slate-500">SENTRIX receives this context explicitly; it does not guess the selected record.</span>
        </div>
      </Card>
      <Card title="Ask SENTRIX" right={<span className="text-xs text-cyan-200"><MessageCircle className="mr-1 inline h-4 w-4" />{latest?.response?.provider ?? 'ready'}</span>}>
        <div className="min-h-64 space-y-3">
          {!history.length && <div className="rounded-md border border-[#263650] bg-[#0B1020]/50 p-4 text-sm text-slate-400">Ask about stored companies, events, evidence, risks, or actual ML experiments. Answers disclose missing evidence and provider limitations.</div>}
          {history.map((item, index) => (
            <div key={`${item.role}-${index}`} className={`rounded-md border p-3 text-sm ${item.role === 'user' ? 'ml-8 border-cyan-300/20 bg-cyan-300/10 text-cyan-50' : 'mr-8 border-[#263650] bg-[#0B1020]/60 text-slate-200'}`}>
              <div className="mb-1 text-xs uppercase text-slate-500">{item.role === 'user' ? 'You' : 'SENTRIX'}</div>
              <p className="whitespace-pre-wrap leading-6">{item.text}</p>
              {item.response?.citations.length ? <div className="mt-3 border-t border-[#263650] pt-2 text-xs text-slate-400">
                Sources:
                <div className="mt-1 space-y-1">{item.response.citations.map((citation) => (
                  <div key={citation.id}><span className="text-cyan-200">[{citation.id}]</span>{' '}
                    {citation.url ? <a className="text-cyan-300 underline" href={citation.url} target="_blank" rel="noreferrer">{citation.title}</a> : citation.title}
                    {' '}({citation.verification_status}, collected {new Date(citation.collected_at).toLocaleDateString()})
                  </div>
                ))}</div>
              </div> : null}
            </div>
          ))}
          {busy && <Loading />}
        </div>
        <div className="mt-3 flex gap-2">
          <Input className="flex-1" placeholder="Ask about your intelligence records..." value={message} onChange={(e) => setMessage(e.target.value)} onKeyDown={(e) => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); send() } }} />
          <Button disabled={busy || !message.trim()} onClick={() => send()}><Send className="mr-1 inline h-4 w-4" />Send</Button>
          <Button disabled={!latest} onClick={async () => { if (latest) { await navigator.clipboard.writeText(latest.text); setCopied(true); setTimeout(() => setCopied(false), 1500) } }}><Copy className="mr-1 inline h-4 w-4" />Copy</Button>
        </div>
        {copied && <SuccessBox message="Latest SENTRIX answer copied." />}
      </Card>
      <Card title="Suggested questions">
        <div className="flex flex-wrap gap-2">{suggestions.map((suggestion) => <button key={suggestion} className="rounded-md border border-[#263650] px-3 py-2 text-left text-sm text-slate-300 hover:border-cyan-300/40 hover:text-cyan-100" onClick={() => send(suggestion)}>{suggestion}</button>)}</div>
      </Card>
    </div>
  )
}
