import { Route, Routes } from 'react-router-dom'
import Layout from './components/Layout'
import { Empty } from './components/ui'
import Companies from './pages/Companies'
import CompanyProfile from './pages/CompanyProfile'
import EventDetail from './pages/EventDetail'
import Feed from './pages/Feed'
import Overview from './pages/Overview'
import Planned from './pages/Planned'
import Risk from './pages/Risk'
import Settings from './pages/Settings'

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route index element={<Overview />} />
        <Route path="companies" element={<Companies />} />
        <Route path="companies/:id" element={<CompanyProfile />} />
        <Route path="feed" element={<Feed />} />
        <Route path="events/:id" element={<EventDetail />} />
        <Route path="risk" element={<Risk />} />
        <Route path="reports" element={<Planned title="Reports" hint="Report generation and export are planned for stage 6; the backend has no report endpoints yet." />} />
        <Route path="workflows" element={<Planned title="Workflows" hint="Scheduling and delivery workflows are planned for stage 6; the backend has no workflow endpoints yet." />} />
        <Route path="settings" element={<Settings />} />
        <Route path="*" element={<Empty title="Page not found" />} />
      </Route>
    </Routes>
  )
}
