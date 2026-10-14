import { Bar, BarChart, CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import { Card, Empty, PageTitle } from '../components/ui'
import { useFetch } from '../hooks/useFetch'
import { label } from '../utils/format'

const chart = { width: '100%', height: 260 }
const tip = { background: '#111B32', border: '1px solid #263650', color: '#F8FAFC' }

export default function Analytics() {
  const timeline = useFetch<{ date: string; events: number }[]>('/analytics/timeline')
  const categories = useFetch<{ category: string; count: number }[]>('/analytics/categories')
  const companies = useFetch<{ name: string; events: number; observations: number }[]>('/analytics/companies')
  const priorities = useFetch<{ priority: string; count: number }[]>('/analytics/priorities')
  return (
    <div className="space-y-4">
      <PageTitle title="Market Analytics" subtitle="Transparent prototype analytics derived from local event and observation records." />
      <div className="grid gap-4 md:grid-cols-2">
        <Card title="Activity trend">{timeline.data?.length === 0 ? <Empty title="No activity" /> : <div style={chart}><ResponsiveContainer><LineChart data={timeline.data ?? []}><CartesianGrid stroke="#263650" /><XAxis dataKey="date" stroke="#94A3B8" /><YAxis allowDecimals={false} stroke="#94A3B8" /><Tooltip contentStyle={tip} /><Line dataKey="events" stroke="#22D3EE" strokeWidth={2} /></LineChart></ResponsiveContainer></div>}<p className="mt-2 text-xs text-slate-500">Calculated by counting events per observation date.</p></Card>
        <Card title="Event categories"><div style={chart}><ResponsiveContainer><BarChart data={(categories.data ?? []).map((x) => ({ ...x, category: label(x.category) }))}><CartesianGrid stroke="#263650" /><XAxis dataKey="category" stroke="#94A3B8" /><YAxis allowDecimals={false} stroke="#94A3B8" /><Tooltip contentStyle={tip} /><Bar dataKey="count" fill="#3B82F6" /></BarChart></ResponsiveContainer></div><p className="mt-2 text-xs text-slate-500">Counts are grouped by configured event category.</p></Card>
        <Card title="Company activity"><div style={chart}><ResponsiveContainer><BarChart data={companies.data ?? []}><CartesianGrid stroke="#263650" /><XAxis dataKey="name" stroke="#94A3B8" fontSize={10} /><YAxis allowDecimals={false} stroke="#94A3B8" /><Tooltip contentStyle={tip} /><Bar dataKey="events" fill="#22D3EE" /><Bar dataKey="observations" fill="#8B5CF6" /></BarChart></ResponsiveContainer></div><p className="mt-2 text-xs text-slate-500">Comparison uses local event and observation counts.</p></Card>
        <Card title="Risk distribution"><div style={chart}><ResponsiveContainer><BarChart data={priorities.data ?? []}><CartesianGrid stroke="#263650" /><XAxis dataKey="priority" stroke="#94A3B8" /><YAxis allowDecimals={false} stroke="#94A3B8" /><Tooltip contentStyle={tip} /><Bar dataKey="count" fill="#F59E0B" /></BarChart></ResponsiveContainer></div><p className="mt-2 text-xs text-slate-500">Priority is assigned by transparent prototype risk rules, not a validated model.</p></Card>
      </div>
    </div>
  )
}
