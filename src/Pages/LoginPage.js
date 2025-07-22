import "./LoginPage.css";

import { useState } from "react";
import { useNavigate } from "react-router-dom";

import { login } from "../Scripts/helperFunctions";

function LoginPage() {
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [message, setMessage] = useState("")
    const navigation = useNavigate();

    return (
        <div id="loginPageWrapper">
            <div id="loginCard">
                <div class="flexCenter">
                    <h1>Login</h1>
                </div>
                <p>Email</p>
                <input 
                type="email" 
                placeholder="Enter your email.."
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                />
                <p>Password</p>
                <input 
                type="password" 
                placeholder="Enter your password.."
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                />
                <p>{message}</p>
                <br/>
                <div class="flexCenter">
                    <button onClick={() => {
                        login(email, password, setMessage, () => {navigation("/")})
                    }}>Login</button>
                </div> 
            </div>
        </div>
    );
}

export default LoginPage;