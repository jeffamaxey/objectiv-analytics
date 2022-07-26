import { ObjectivProvider, ReactTracker } from "@objectiv/tracker-react";
import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import './index.css'

import '@objectiv/developer-tools';

const tracker = new ReactTracker({
  applicationId: 'demo-app-sessions-playground',
  endpoint: 'http://127.0.0.1:8081/'
})

ReactDOM.createRoot(document.getElementById('root') as HTMLElement).render(
  <React.StrictMode>
    <ObjectivProvider tracker={tracker}>
      <App />
    </ObjectivProvider>
  </React.StrictMode>
)
