import { useState } from 'react'

export default function SearchBar({ onSearch, loading }) {
  const [query, setQuery] = useState('')
  const [limit, setLimit] = useState(10)

  function handleSubmit(e) {
    e.preventDefault()
    if (query.trim()) onSearch(query.trim(), limit)
  }

  return (
    <form onSubmit={handleSubmit} style={{ display: 'flex', gap: 8, alignItems: 'center', flexWrap: 'wrap' }}>
      <input
        type="text"
        value={query}
        onChange={e => setQuery(e.target.value)}
        placeholder="Search products in natural language…"
        aria-label="Search query"
        style={{ flex: 1, padding: '8px 12px', fontSize: 16, borderRadius: 4, border: '1px solid #ccc', minWidth: 200 }}
      />
      <label style={{ display: 'flex', alignItems: 'center', gap: 4, fontSize: 14 }}>
        Max results:
        <input
          type="number"
          value={limit}
          min={1}
          max={15}
          onChange={e => setLimit(Number(e.target.value))}
          aria-label="Result limit"
          style={{ width: 52, padding: '8px 4px', borderRadius: 4, border: '1px solid #ccc', textAlign: 'center' }}
        />
      </label>
      <button type="submit" disabled={loading || !query.trim()} style={{ padding: '8px 20px', borderRadius: 4, background: '#0070f3', color: '#fff', border: 'none', cursor: 'pointer', fontSize: 15 }}>
        {loading ? 'Searching…' : 'Search'}
      </button>
    </form>
  )
}
