import { BrowserRouter, Routes, Route, Navigate} from 'react-router-dom'
import { LoginPage } from "./pages/loginPage"
import { Dashboard } from "./pages/Dashboard"
import { ChatPage } from "./pages/chatPage"
import { Register } from "./pages/registerPage"

function App() {

  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Navigate to="/login" />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/registro" element={<Register />} />
        <Route path='/dashboard' element={<Dashboard />} />
        <Route path='/chatPage/:userId' element={<ChatPage/>}/>
      </Routes>
    </BrowserRouter>
  )
}

export default App
