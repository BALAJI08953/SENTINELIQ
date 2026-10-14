import { NavLink, Outlet } from 'react-router-dom'
import { BarChart3, Bell, Beaker, Building2, FileSearch, FileText, MessageCircle, Newspaper, Rss, Settings, ShieldAlert, Star, Workflow } from 'lucide-react'
import FloatingSentrix from './FloatingSentrix'

const NAV = [
  ['/', 'Overview', BarChart3], ['/feed', 'Intelligence Feed', Newspaper], ['/companies', 'Companies', Building2],
  ['/watchlists', 'Watchlists', Star], ['/events', 'Events & Evidence', FileSearch], ['/analytics', 'Analytics', BarChart3],
  ['/risk', 'Risk Assessments', ShieldAlert], ['/reports', 'Reports', FileText], ['/workflows', 'Alerts & Workflows', Workflow],
  ['/ml-lab', 'ML Lab', Beaker], ['/sources', 'Sources', Rss], ['/settings', 'Settings', Settings],
  ['/sentrix', 'SENTRIX Assistant', MessageCircle],
] as const

export default function Layout() {
  return (
    <div className="min-h-screen md:flex">
      <nav className="border-b border-[#263650] bg-[#080D1A]/95 p-3 text-slate-200 shadow-2xl shadow-black/20 backdrop-blur-xl md:sticky md:top-0 md:min-h-screen md:w-60 md:border-b-0 md:border-r">
        <div className="mb-4 rounded-lg border border-cyan-300/20 bg-[#111B32] px-3 py-3">
          <div className="text-lg font-bold text-white">SentinelIQ</div>
          <div className="mt-1 text-xs text-cyan-200/75">Competitive intelligence workspace</div>
          <div className="mt-3 inline-flex items-center gap-1 rounded-full border border-violet-400/30 px-2 py-0.5 text-[11px] text-violet-100"><Bell className="h-3 w-3" />Prototype data</div>
        </div>
        <ul className="flex flex-wrap gap-1 md:block md:space-y-1">
          {NAV.map(([to, name, Icon]) => (
            <li key={to}><NavLink to={to} end={to === '/'} className={({ isActive }) => `flex items-center gap-2 rounded-md px-2.5 py-2 text-sm transition ${isActive ? 'border border-cyan-300/30 bg-cyan-300/10 text-cyan-100 shadow-sm' : 'text-slate-300 hover:bg-white/[0.08] hover:text-white'}`}><Icon className="h-4 w-4" />{name}</NavLink></li>
          ))}
        </ul>
      </nav>
      <main className="mx-auto w-full max-w-6xl flex-1 space-y-4 p-4 pb-24 md:p-6 md:pb-24"><Outlet /></main>
      <FloatingSentrix />
    </div>
  )
}
