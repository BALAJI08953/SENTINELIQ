import { useEffect, useState } from 'react'
import { api, errMsg } from '../api/client'

export function useFetch<T>(url: string | null, params?: Record<string, unknown>) {
  const [data, setData] = useState<T | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(url !== null)
  const [tick, setTick] = useState(0)
  const key = JSON.stringify(params ?? {})
  useEffect(() => {
    if (!url) return
    let cancelled = false
    setLoading(true)
    api.get<T>(url, { params: JSON.parse(key) })
      .then((r) => { if (!cancelled) { setData(r.data); setError(null) } })
      .catch((e) => { if (!cancelled) setError(errMsg(e)) })
      .finally(() => { if (!cancelled) setLoading(false) })
    return () => { cancelled = true }
  }, [url, key, tick])
  return { data, error, loading, reload: () => setTick((t) => t + 1) }
}
