// import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import App from './App.tsx'
import { initPerformanceLogSession } from './performance'
import '../../shared/dom-mutation-observer.js'
import '../../shared/performance-measurement.js'

import "./assets/fontawesome/css/all.css"
import "./assets/style/style.scss"

initPerformanceLogSession()

createRoot(document.getElementById('root')!).render(
  // <StrictMode>
    <App />
  // </StrictMode>,
)
