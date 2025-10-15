import { useState } from "react"

function App() {
  const [message, setMessage] = useState("")    // A React hook used for dynamic state

  const handleClick = async () => {
    try {
      const response = await fetch("http://127.0.0.1:8001/test")    // Calls the backend API endpoint

      const message = await response.text();
      setMessage(message)
    } catch (error) {
      console.log(error)
    }
  }

  return (
    <>
      <button className="btn btn-primary" onClick={handleClick}>Click me</button>
      <p>{message}</p>
    </>
  )
}

export default App
