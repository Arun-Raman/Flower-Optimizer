import { useState } from "react"

function App() {
  const [message, setMessage] = useState("")

  const handleClick = async () => {
    try {
      const response = await fetch("http://127.0.0.1:8001/test")

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
