import axios from 'axios'

const apiBase = import.meta.env.VITE_API_BASE_URL ?? '/api/v1'
export const api = axios.create({ baseURL: apiBase })

export const backendApi = api

export function errMsg(e: unknown): string {
  if (axios.isAxiosError(e)) {
    if (!e.response) return 'Backend is unavailable. Start the SentinelIQ API and try again.'
    const status = e.response.status
    if (status >= 500) return 'Backend failed while processing this request. Check the server logs and try again.'
    if (status === 404) return 'The requested backend resource was not found.'
    const detail = e.response.data?.detail
    if (typeof detail === 'string') return `Request was not accepted: ${detail}`
    if (Array.isArray(detail) && detail[0]?.msg) return `Request was not accepted: ${detail[0].msg}`
    return `Request was not accepted by the backend. Status ${status}.`
  }
  return e instanceof Error ? e.message : 'Unexpected error.'
}
