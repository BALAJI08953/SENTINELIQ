import { useEffect, useMemo, useRef, useState } from 'react'
import { Copy, Loader2, Maximize2, MessageCircle, Minimize2, Plus, Send, X } from 'lucide-react'
import { Link, useLocation, useParams } from 'react-router-dom'
import { api, errMsg } from '../api/client'
import type { SentrixResponse } from '../types'

type ChatMessage = {
  id: string
  role: 'user' | 'assistant'
  text: string
  at: string
  response?: SentrixResponse
}

const suggestions = [
  'Summarize the latest developments on this page.',
  'Which risks need attention first?',
  'What evidence supports this conclusion?',
]

function routeContext(pathname: string, params: Readonly<Record<string, string | undefined>>) {
  const body: { company_id?: number; event_id?: number } = {}
  if (pathname.startsWith('/companies/') && params.id) body.company_id = Number(params.id)
  if (pathname.startsWith('/events/') && params.id) body.event_id = Number(params.id)
  return body
}

function labelForPath(pathname: string) {
  if (pathname === '/') return 'Overview'
  return pathname.split('/').filter(Boolean).map((part) => part.replace(/-/g, ' ')).join(' / ') || 'Current page'
}

export default function FloatingSentrix() {
  const location = useLocation()
  const params = useParams()
  const inputRef = useRef<HTMLInputElement>(null)
  const [open, setOpen] = useState(false)
  const [minimized, setMinimized] = useState(false)
  const [message, setMessage] = useState('')
  const [history, setHistory] = useState<ChatMessage[]>([])
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [copiedId, setCopiedId] = useState<string | null>(null)
  const pageLabel = useMemo(() => labelForPath(location.pathname), [location.pathname])
  const context = useMemo(() => routeContext(location.pathname, params), [location.pathname, params])

  useEffect(() => {
    if (open && !minimized) inputRef.current?.focus()
  }, [open, minimized])

  async function send(text = message) {
    const cleaned = text.trim()
    if (!cleaned || busy) return
    const at = new Date().toISOString()
    setHistory((items) => [...items, { id: crypto.randomUUID(), role: 'user', text: cleaned, at }])
    setMessage('')
    setError(null)
    setBusy(true)
    try {
      const response = await api.post<SentrixResponse>('/sentrix/chat', {
        message: cleaned,
        ...context,
      })
      setHistory((items) => [
        ...items,
        { id: crypto.randomUUID(), role: 'assistant', text: response.data.answer, at: new Date().toISOString(), response: response.data },
      ])
    } catch (e) {
      setError(errMsg(e))
    } finally {
      setBusy(false)
    }
  }

  async function copy(item: ChatMessage) {
    try {
      await navigator.clipboard.writeText(item.text)
      setCopiedId(item.id)
      window.setTimeout(() => setCopiedId(null), 1400)
    } catch {
      setError('Could not copy the SENTRIX answer from this browser context.')
    }
  }

  function startNew() {
    setHistory([])
    setError(null)
    setMessage('')
    setMinimized(false)
    setOpen(true)
  }

  if (!open) {
    return (
      <button
        type="button"
        aria-label="Open SENTRIX assistant"
        className="fixed bottom-4 right-4 z-40 inline-flex h-12 w-12 items-center justify-center rounded-full border border-cyan-200/40 bg-cyan-500 text-white shadow-2xl shadow-cyan-950/40 transition hover:bg-cyan-400 focus:outline-none focus:ring-2 focus:ring-cyan-200 md:bottom-6 md:right-6"
        onClick={() => setOpen(true)}
      >
        <MessageCircle className="h-5 w-5" />
      </button>
    )
  }

  return (
    <aside
      aria-label="SENTRIX assistant"
      className="fixed inset-x-3 bottom-3 z-40 md:inset-x-auto md:bottom-6 md:right-6 md:w-[24rem]"
    >
      <div className="overflow-hidden rounded-lg border border-cyan-200/25 bg-[#0B1020]/95 shadow-2xl shadow-black/40 backdrop-blur-xl">
        <header className="flex items-center gap-2 border-b border-[#263650] bg-[#111B32] px-3 py-2">
          <MessageCircle className="h-4 w-4 text-cyan-200" />
          <div className="min-w-0 flex-1">
            <div className="text-sm font-semibold text-slate-50">SENTRIX</div>
            <div className="truncate text-xs text-slate-400">{pageLabel} context</div>
          </div>
          <Link className="rounded p-1 text-slate-300 hover:bg-white/10 hover:text-white" aria-label="Open full SENTRIX page" to="/sentrix">
            <Maximize2 className="h-4 w-4" />
          </Link>
          <button type="button" className="rounded p-1 text-slate-300 hover:bg-white/10 hover:text-white" aria-label="Start new SENTRIX conversation" onClick={startNew}>
            <Plus className="h-4 w-4" />
          </button>
          <button type="button" className="rounded p-1 text-slate-300 hover:bg-white/10 hover:text-white" aria-label={minimized ? 'Restore SENTRIX' : 'Minimize SENTRIX'} onClick={() => setMinimized((value) => !value)}>
            <Minimize2 className="h-4 w-4" />
          </button>
          <button type="button" className="rounded p-1 text-slate-300 hover:bg-white/10 hover:text-white" aria-label="Close SENTRIX" onClick={() => setOpen(false)}>
            <X className="h-4 w-4" />
          </button>
        </header>
        {!minimized && (
          <>
            <div className="max-h-[54vh] min-h-64 space-y-3 overflow-y-auto px-3 py-3 md:max-h-[30rem]">
              {!history.length && (
                <div className="rounded-md border border-[#263650] bg-[#111B32]/70 p-3 text-sm text-slate-300">
                  Ask about stored companies, events, evidence, risks, reports, workflows, or ML experiments. SENTRIX answers from persisted records and cites sources when available.
                </div>
              )}
              {history.map((item) => (
                <article key={item.id} className={`rounded-md border p-3 text-sm ${item.role === 'user' ? 'ml-8 border-cyan-300/25 bg-cyan-300/10 text-cyan-50' : 'mr-8 border-[#263650] bg-[#111B32]/75 text-slate-200'}`}>
                  <div className="mb-1 flex items-center justify-between gap-2 text-xs text-slate-500">
                    <span>{item.role === 'user' ? 'You' : 'SENTRIX'} · {new Date(item.at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
                    {item.role === 'assistant' && (
                      <button type="button" className="rounded p-1 text-slate-400 hover:bg-white/10 hover:text-cyan-100" aria-label="Copy SENTRIX answer" onClick={() => copy(item)}>
                        <Copy className="h-3.5 w-3.5" />
                      </button>
                    )}
                  </div>
                  <p className="whitespace-pre-wrap leading-6">{item.text}</p>
                  {copiedId === item.id && <div className="mt-2 text-xs text-emerald-300">Copied.</div>}
                  {item.response?.citations.length ? (
                    <div className="mt-3 border-t border-[#263650] pt-2 text-xs text-slate-400">
                      <div className="font-medium text-slate-300">Sources</div>
                      <div className="mt-1 space-y-1">
                        {item.response.citations.slice(0, 3).map((citation) => (
                          <div key={citation.id}>
                            <span className="text-cyan-200">[{citation.id}]</span>{' '}
                            {citation.url ? <a className="text-cyan-300 underline" href={citation.url} target="_blank" rel="noreferrer">{citation.title}</a> : citation.title}
                          </div>
                        ))}
                      </div>
                    </div>
                  ) : null}
                </article>
              ))}
              {busy && <div className="flex items-center gap-2 text-sm text-slate-400"><Loader2 className="h-4 w-4 animate-spin" />SENTRIX is checking records...</div>}
              {error && <div role="alert" className="rounded-md border border-red-400/30 bg-red-950/50 p-2 text-sm text-red-100">{error}</div>}
            </div>
            {!history.length && (
              <div className="flex gap-2 overflow-x-auto border-t border-[#263650] px-3 py-2">
                {suggestions.map((suggestion) => (
                  <button key={suggestion} type="button" className="shrink-0 rounded-md border border-[#263650] px-2 py-1 text-xs text-slate-300 hover:border-cyan-300/40 hover:text-cyan-100" onClick={() => send(suggestion)}>
                    {suggestion}
                  </button>
                ))}
              </div>
            )}
            <form className="flex gap-2 border-t border-[#263650] p-3" onSubmit={(event) => { event.preventDefault(); send() }}>
              <input
                ref={inputRef}
                className="min-w-0 flex-1 rounded-md border border-[#263650] bg-[#080D1A] px-2 py-2 text-sm text-slate-50 outline-none placeholder:text-slate-500 focus:border-cyan-300 focus:ring-2 focus:ring-cyan-300/20"
                placeholder="Ask SENTRIX..."
                value={message}
                onChange={(event) => setMessage(event.target.value)}
              />
              <button type="submit" disabled={busy || !message.trim()} aria-label="Send message to SENTRIX" className="inline-flex h-9 w-9 items-center justify-center rounded-md border border-cyan-300/30 bg-cyan-500 text-white hover:bg-cyan-400 disabled:opacity-50">
                <Send className="h-4 w-4" />
              </button>
            </form>
          </>
        )}
      </div>
    </aside>
  )
}
