import { createRoot } from 'react-dom/client'
import { paths } from './api/client'

function App() {
  return (
    <div>
      <h1>Frontend spricht</h1>
      <p>Hier könnten API-Daten stehen...</p>
    </div>
  )
}

const root = createRoot(document.getElementById('root')!)
root.render(<App />)
