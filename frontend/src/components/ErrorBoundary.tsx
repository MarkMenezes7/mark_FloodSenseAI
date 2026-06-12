import { Component, type ReactNode } from 'react'

interface Props { children: ReactNode }
interface State { hasError: boolean; errorMessage: string }

export default class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props)
    this.state = { hasError: false, errorMessage: '' }
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, errorMessage: error.message }
  }

  componentDidCatch(error: Error, info: { componentStack: string }) {
    console.error('[FloodSenseAI] Uncaught error:', error, info.componentStack)
  }

  render() {
    if (this.state.hasError) {
      return (
        <div style={{
          minHeight: '100vh', display: 'flex', flexDirection: 'column',
          alignItems: 'center', justifyContent: 'center',
          background: 'linear-gradient(135deg, #0f1119 0%, #1a1d2e 100%)',
          color: '#fff', fontFamily: 'Inter, sans-serif', padding: '2rem', textAlign: 'center'
        }}>
          <div style={{ fontSize: '4rem', marginBottom: '1rem' }}>⚠️</div>
          <h1 style={{ fontSize: '1.8rem', fontWeight: 700, marginBottom: '0.5rem' }}>
            Something went wrong
          </h1>
          <p style={{ color: '#94a3b8', maxWidth: 420, marginBottom: '0.5rem' }}>
            The app encountered an unexpected error. This usually happens when the backend server is temporarily unreachable.
          </p>
          <p style={{
            background: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.3)',
            borderRadius: 8, padding: '8px 16px', fontSize: '0.8rem',
            color: '#fca5a5', marginBottom: '2rem', maxWidth: 480, wordBreak: 'break-word'
          }}>
            {this.state.errorMessage || 'Unknown error'}
          </p>
          <button
            onClick={() => { this.setState({ hasError: false, errorMessage: '' }); window.location.reload() }}
            style={{
              background: 'linear-gradient(135deg, #3b82f6, #6366f1)', color: '#fff',
              border: 'none', borderRadius: 10, padding: '12px 28px',
              fontSize: '1rem', fontWeight: 600, cursor: 'pointer'
            }}
          >
            🔄 Reload App
          </button>
        </div>
      )
    }
    return this.props.children
  }
}
