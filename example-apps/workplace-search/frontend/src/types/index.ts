export interface Facet {
  name: string
  entries: {
    count: number
    value: string
  }[]
}

export interface SearchResponse {
  results: Result[]
  facets: Facet[]
  streaming_id: string
  conversation_id: string
}

export interface Result {
  id: string
  category: [string]
  content: [string]
  summary: [string]
  name: [string]
  url: [string]
}

export type SourceType = {
  name: string
  summary: string[]
  url?: string
}
