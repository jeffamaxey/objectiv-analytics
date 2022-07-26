import { useSuccessEventTracker } from "@objectiv/tracker-react";
import './App.css'
import { useCookies } from "react-cookie";
import reactLogo from './assets/react.svg'

function App() {
  const objectivCookieName = 'obj_user_id';
  const [cookies,,removeCookie] = useCookies([objectivCookieName]);
  const trackSuccessEvent = useSuccessEventTracker();

  const deleteObjectivCookie = () => {
    removeCookie(objectivCookieName);
  }

  const sendLotsOfEventsAtOnce = () => {
    // Default Queue size is 10, this will create 4 batches with 10,10,10 and 1 events respectively.
    for(let i=0; i<31; i++) {
      trackSuccessEvent({
        message: i.toString()
      })
    }
  }

  return (
    <div className="App">
      <div>
        <a href="https://vitejs.dev" target="_blank">
          <img src="/vite.svg" className="logo" alt="Vite logo" />
        </a>
        <a href="https://reactjs.org" target="_blank">
          <img src={reactLogo} className="logo react" alt="React logo" />
        </a>
      </div>
      <h1>Vite + React</h1>
      <div className="card">
        <h3>
          <strong>Last known objectiv cookie</strong>: {cookies.obj_user_id ?? 'not set'}
        </h3>

        <p>
          <button onClick={() => deleteObjectivCookie()}>
            Delete Objectiv cookie
          </button>
        </p>

        <p>
          <button onClick={() => sendLotsOfEventsAtOnce()}>
            Send lots of Events at once
          </button>
        </p>
      </div>
      <p className="read-the-docs">
        Click on the Vite and React logos to learn more
      </p>
    </div>
  )
}

export default App
