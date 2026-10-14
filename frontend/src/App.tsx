import { Route, Routes } from 'react-router-dom'
import Layout from './components/Layout'
import { Empty } from './components/ui'
import Companies from './pages/Companies'
import CompanyProfile from './pages/CompanyProfile'
import EventDetail from './pages/EventDetail'
import EventsEvidence from './pages/EventsEvidence'
import Feed from './pages/Feed'
import Analytics from './pages/Analytics'
import MLLab from './pages/MLLab'
import Overview from './pages/Overview'
import Reports from './pages/Reports'
import Risk from './pages/Risk'
import Settings from './pages/Settings'
import Sources from './pages/Sources'
import Watchlists from './pages/Watchlists'
import Workflows from './pages/Workflows'
import Sentrix from './pages/Sentrix'

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route index element={<Overview />} />
        <Route path="companies" element={<Companies />} />
        <Route path="companies/:id" element={<CompanyProfile />} />
        <Route path="watchlists" element={<Watchlists />} />
        <Route path="feed" element={<Feed />} />
        <Route path="events" element={<EventsEvidence />} />
        <Route path="events/:id" element={<EventDetail />} />
        <Route path="risk" element={<Risk />} />
        <Route path="analytics" element={<Analytics />} />
        <Route path="reports" element={<Reports />} />
        <Route path="workflows" element={<Workflows />} />
        <Route path="ml-lab" element={<MLLab />} />
        <Route path="sources" element={<Sources />} />
        <Route path="settings" element={<Settings />} />
        <Route path="sentrix" element={<Sentrix />} />
        <Route path="*" element={<Empty title="Page not found" />} />
      </Route>
    </Routes>
  )
}
