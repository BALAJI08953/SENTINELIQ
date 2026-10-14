import { useState } from 'react'
import { Beaker, Play, Search } from 'lucide-react'
import { backendApi, errMsg } from '../api/client'
import { Button, Card, ErrorBox, Input, Loading, PageTitle, SuccessBox, Tag } from '../components/ui'

type Validation = { is_valid: boolean; path: string; row_count: number; valid_row_count: number; invalid_row_count: number; duplicate_row_count: number; labels: string[]; label_counts: Record<string, number>; validation_errors: string[] }
type Experiment = { id: string; task: string; status: string; dataset: Validation; metrics: { accuracy: number; macro_f1: number; n_test: number; baseline: { accuracy: number; macro_f1: number }; confusion_matrix: number[][]; labels: string[] }; created_at: string }

export default function MLLab() {
  const [path, setPath] = useState('sample_data/training_examples.csv')
  const [validation, setValidation] = useState<Validation | null>(null)
  const [experiments, setExperiments] = useState<Experiment[]>([])
  const [selected, setSelected] = useState<Experiment | null>(null)
  const [text, setText] = useState('')
  const [prediction, setPrediction] = useState<{ label: string; confidence: number; model_version: string } | null>(null)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [message, setMessage] = useState<string | null>(null)

  const run = async (action: () => Promise<void>) => {
    setError(null)
    setMessage(null)
    setBusy(true)
    try { await action() } catch (e) { setError(errMsg(e)) } finally { setBusy(false) }
  }

  const validate = () => run(async () => {
    const response = await backendApi.post<Validation>('/ml/datasets/validate', { path })
    setValidation(response.data)
    setMessage(response.data.is_valid ? 'Dataset validation passed.' : 'Dataset validation found issues.')
  })

  const loadHistory = () => run(async () => {
    const response = await backendApi.get<{ items: Experiment[] }>('/ml/experiments')
    setExperiments(response.data.items)
    setMessage('Experiment history loaded.')
  })

  const train = () => run(async () => {
    const response = await backendApi.post<Experiment>('/ml/experiments/train', { path, task: 'competitive_event_classification' })
    setExperiments((items) => [response.data, ...items.filter((item) => item.id !== response.data.id)])
    setSelected(response.data)
    setMessage(`Training completed: ${response.data.id}`)
  })

  const predict = () => selected && run(async () => {
    const response = await backendApi.post(`/ml/experiments/${selected.id}/predict`, { text })
    setPrediction(response.data)
  })

  return (
    <div className="space-y-4">
      <PageTitle title="ML Lab" subtitle="Run the real local event-classification pipeline. Metrics appear only after backend training completes." />
      {error && <ErrorBox message={error} />}{message && <SuccessBox message={message} />}
      <Card title="Dataset validation and training">
        <div className="flex flex-wrap gap-2"><Input className="min-w-80 flex-1" value={path} onChange={(e) => setPath(e.target.value)} placeholder="Path to local CSV inside the project" /><Button disabled={busy} onClick={validate}><Search className="mr-1 inline h-4 w-4" />Validate</Button><Button disabled={busy || !validation?.is_valid} onClick={train}><Play className="mr-1 inline h-4 w-4" />Train event classifier</Button></div>
        <p className="mt-2 text-xs text-slate-500">Required columns: <code>text,label</code>. The current backend task supports competitive event labels only.</p>
        {validation && <div className="mt-4 grid gap-2 text-sm md:grid-cols-4"><div><span className="text-slate-500">Rows</span><div className="text-slate-100">{validation.row_count}</div></div><div><span className="text-slate-500">Valid rows</span><div className="text-slate-100">{validation.valid_row_count}</div></div><div><span className="text-slate-500">Duplicates</span><div className="text-slate-100">{validation.duplicate_row_count}</div></div><div><span className="text-slate-500">Labels</span><div className="text-slate-100">{validation.labels.join(', ') || '-'}</div></div></div>}
        {validation?.validation_errors.length ? <ul className="mt-3 list-disc pl-5 text-sm text-amber-200">{validation.validation_errors.map((item) => <li key={item}>{item}</li>)}</ul> : null}
      </Card>
      <Card title="Experiment history" right={<Button disabled={busy} onClick={loadHistory}>Refresh</Button>}>
        {busy && !experiments.length && <Loading />}
        {!experiments.length && !busy && <p className="text-sm text-slate-400">No experiments loaded. Validate and train a local dataset or refresh history.</p>}
        <div className="divide-y divide-[#263650]">{experiments.map((experiment) => <button key={experiment.id} className="flex w-full items-center gap-2 py-3 text-left hover:bg-white/[0.03]" onClick={() => setSelected(experiment)}><Beaker className="h-4 w-4 text-cyan-300" /><span className="text-slate-100">{experiment.id}</span><Tag>{experiment.task}</Tag><Tag>{experiment.status}</Tag><span className="ml-auto text-xs text-slate-500">{new Date(experiment.created_at).toLocaleString()}</span></button>)}</div>
      </Card>
      {selected && <Card title={`Experiment ${selected.id}`}>
        <div className="grid gap-3 md:grid-cols-4"><Metric name="Accuracy" value={selected.metrics.accuracy} /><Metric name="Macro F1" value={selected.metrics.macro_f1} /><Metric name="Baseline accuracy" value={selected.metrics.baseline.accuracy} /><Metric name="Held-out rows" value={selected.metrics.n_test} /></div>
        <div className="mt-4 flex flex-wrap gap-2"><Input className="min-w-80 flex-1" placeholder="Enter text for inference" value={text} onChange={(e) => setText(e.target.value)} /><Button disabled={!text.trim() || busy} onClick={predict}>Run inference</Button></div>
        {prediction && <div className="mt-3 text-sm text-cyan-100">Prediction: <b>{prediction.label}</b> - confidence {Math.round(prediction.confidence * 100)}% - model {prediction.model_version}</div>}
        <p className="mt-3 text-xs text-slate-500">Evaluation is computed on the held-out split returned by the backend. It is not a business-risk prediction.</p>
      </Card>}
    </div>
  )
}

function Metric({ name, value }: { name: string; value: number }) {
  const display = name === 'Held-out rows' ? String(value) : `${Math.round(value * 100)}%`
  return <div className="rounded-lg border border-[#263650] bg-[#0B1020]/60 p-3"><div className="text-xs uppercase text-slate-500">{name}</div><div className="mt-1 text-xl font-semibold text-slate-100">{display}</div></div>
}
