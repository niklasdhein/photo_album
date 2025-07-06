import "./RegistrationPage.css";

import { useState } from "react";
import { useNavigate } from "react-router-dom";

function RegistrationPage() {
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [message, setMessage] = useState("");
    const navigation = useNavigate();

    function register() {
        fetch("http://localhost:5000/register", {
            method: "POST",
            credentials: "include",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                email: email,
                password: password,
            }),
        })
        .then((res) => {
            if (res.ok) navigation("/login/");
            return res.json();
        })
        .then((data) => setMessage(data.ans))
        .catch((e) => alert(e));
    }

    return (
        <div id="registrationPageWrapper">
            <div id="registrationCard">
                <div class="flexCenter">
                    <h1>Register</h1>
                </div>
                <p>Email</p>
                <input 
                type="email" 
                placeholder="Set an email.."
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                />
                <p>Password</p>
                <input 
                type="password" 
                placeholder="Set a password.."
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                />
                <p>{message}</p>
                <br/>
                <div class="flexCenter">
                    <button onClick={register}>Register</button>
                </div> 
            </div>
        </div>
    );
}

export default RegistrationPage;