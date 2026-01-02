import React, { useState, useMemo } from 'react'
import LoginForm from './components/LoginForm'
import Dashboard from './pages/Dashboard'

export default function App() {
  const [token, setToken] = useState(null)
  if (!token) return <LoginForm onLogin={setToken} />
  return <Dashboard token={token} />
}
