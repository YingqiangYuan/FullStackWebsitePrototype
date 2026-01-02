import React, { useEffect, useState } from 'react'
import Plot from 'react-plotly.js'

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8080/api'

export default function Dashboard({ token }) {
  const [companies, setCompanies] = useState([])
  const [top5, setTop5] = useState([])
  const [low5, setLow5] = useState([])

  useEffect(() => {
    const headers = { Authorization: `Bearer ${token}` }
    fetch(`${API_BASE}/companies`, { headers })
      .then(r => r.json()).then(setCompanies)
    fetch(`${API_BASE}/treemap/top5`, { headers })
      .then(r => r.json()).then(setTop5)
    fetch(`${API_BASE}/treemap/low5`, { headers })
      .then(r => r.json()).then(setLow5)
  }, [token])

  function toTreemap(data) {
    // Sector as parent, ticker as label; values use absolute score magnitude for size
    const parents = data.map(d => d.sector)
    const labels = data.map(d => d.ticker)
    const values = data.map(d => Math.abs(d.score) + 0.01)
    return (
      <Plot
        data={[{type:'treemap', labels, parents, values, text: data.map(d => d.score.toFixed(3)), textinfo:'label+text'}]}
        layout={{ height: 500, margin: { t: 40, l: 0, r: 0, b: 0 } }}
      />
    )
  }

  return (
    <div style={{ padding: 16, fontFamily: 'sans-serif' }}>
      <h2>MarketView Dashboard</h2>
      <p>Companies loaded: {companies.length}</p>
      <h3>Top 5 by Sector</h3>
      {toTreemap(top5)}
      <h3>Bottom 5 by Sector</h3>
      {toTreemap(low5)}
    </div>
  )
}
