import { NavLink, Outlet } from 'react-router-dom'
import { BarChart3, Building2, FileText, Newspaper, Settings, ShieldAlert, Workflow } from 'lucide-react'

const NAV = [
  ['/', 'Overview', BarChart3], ['/companies', 'Companies', Building2], ['/feed', 'Intelligence feed', Newspaper],
  ['/risk', 'Risk assessments', ShieldAlert], ['/reports', 'Reports', FileText], ['/workflows', 'Workflows', Workflow],
  ['/settings', 'Settings', Settings],
] as const

export default function Layout() {
  return (
    <div className="min-h-screen md:flex">
      <nav className="border-b border-slate-200 bg-slate-900 p-3 text-slate-200 md:min-h-screen md:w-56 md:border-b-0">
        <div className="mb-3 px-2 text-lg font-bold text-white">SentinelIQ</div>
        <ul className="flex flex-wrap gap-1 md:block md:space-y-1">
          {NAV.map(([to, name, Icon]) => (
            <li key={to}><NavLink to={to} end={to === '/'} className={({ isActive }) => `flex items-center gap-2 rounded px-2 py-1.5 text-sm ${isActive ? 'bg-slate-700 text-white' : 'hover:bg-slate-800'}`}><Icon className="h-4 w-4" />{name}</NavLink></li>
          ))}
        </ul>
      </nav>
      <main className="mx-auto w-full max-w-6xl flex-1 space-y-4 p-4"><Outlet /></main>
    </div>
  )
}
