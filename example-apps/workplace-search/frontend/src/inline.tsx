import React from 'react'
import ReactDOM from 'react-dom/client'
import './index.css'
import InlineApp from './InlineApp'
import { GlobalStateProvider } from './store/provider'

const root = ReactDOM.createRoot(document.getElementById('root') as HTMLElement)
root.render(
  <GlobalStateProvider>
    <InlineApp />
  </GlobalStateProvider>
)
