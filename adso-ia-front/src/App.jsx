import React from 'react'
import './App.css'
import Chatbot from './components/Chatbot'
import Logo from './components/Logo'

function App() {
    return (
        <div className="flex justify-center items-center min-h-screen bg-zinc-900 justify-evenly">
            <Logo />
            <Chatbot />
        </div>
    )
}

export default App
