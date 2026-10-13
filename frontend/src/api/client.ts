import axios from 'axios'

export const api = axios.create({ baseURL: '/api/v1' })

export function errMsg(e: unknown): string {
  if (axios.isAxiosError(e)) {
    const d = e.response?.data
    return d?.error?.message ?? d?.detail?.[0]?.msg ?? e.message
  }
  return e instanceof Error ? e.message : String(e)
}
