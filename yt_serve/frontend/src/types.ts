export interface Playlist {
  id: number
  url: string
  title: string
  local_count: number
  playlist_count: number
  unavailable_count: number
  last_download: string | null
  last_extract: string | null
  excluded_ids: string[]
}

export interface Job {
  id: number
  playlist_id: number
  job_type: 'download' | 'extract' | 'both'
  status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled'
  progress: number
  total_items: number
  completed_items: number
  failed_items: number
  created_at: string
  started_at: string | null
  completed_at: string | null
  error: string | null
}

export interface LogEntry {
  message: string
}
