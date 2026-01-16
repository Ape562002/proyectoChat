import { useState, useEffect } from "react"
import DropdownMenu from "../components/Base"
import { useNavigate } from "react-router-dom"

export function Dashboard(){
    const [users,setUsers] = useState([])
    const navigate = useNavigate();
    
    useEffect(() => {
        fetch("http://127.0.0.1:8000/user/",{
            headers: {
                Authorization: `token ${localStorage.getItem("token")}`
            }
        })
        .then(res => res.json())
        .then(data => setUsers(data.results));
    },[])

    return(
        <div>
            <h1>Que Onda</h1>

            {users.map(user => (
                <button key={user.id}
                onClick={() => navigate(`/chatPage/${user.id}`)}
                >
                    {user.username}
                </button>
            ))}
            <DropdownMenu/>
        </div>
    )
}