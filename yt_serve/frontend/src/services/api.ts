import axios from 'axios'
import type { Playlist, Job, LogEntry } from './types'

const api = axios.create({
  baseURL: '/api',
})

export const playlistsApi = {
  list: () => api.get<Playlist[]>('/playlists'),
  get: (id: number) => api.get<Playlist>(`/playlists/${id}`),
  create: (url: string) => api.post<Playlist>('/playlists', { url }),
  update: (id: number, data: Partial<Playlist>) => api.put<Playlist>(`/playlists/${id}`, data),
  delete: (id: number) => api.delete(`/playlists/${id}`),
  refresh: (id: number) => api.post<Playlist>(`/playlists/${id}/refresh`),
}

export const jobsApi = {
  list: (playlistId?: number) => 
    api.get<Job[]>('/downloads/jobs', { params: { playlist_id: playlistId } }),
  get: (id: number) => api.get<Job>(`/downloads/jobs/${id}`),
  create: (playlistId: number, jobType: 'download' | 'extract' | 'both') =>
    api.post<Job>('/downloads/jobs', { playlist_id: playlistId, job_type: jobType }),
  cancel: (id: number) => api.post(`/downloads/jobs/${id}/cancel`),
  logs: (id: number, lines?: number) =>
    api.get<LogEntry[]>(`/downloads/jobs/${id}/logs`, { params: { lines } }),
}

export interface Config {
  base_download_path: string
  audio_extract_mode: string
  max_extraction_workers: number
  max_concurrent_downloads: number
  batch_size: number
  cookies_file: string | null
  use_browser_cookies: boolean
  browser_name: string
  needs_setup: boolean
}

export const configApi = {
  get: () => api.get<Config>('/config'),
  update: (config: Partial<Config>) => api.put<Config>('/config', config),
}

export default api
