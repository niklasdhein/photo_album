import "./LogoutButton.css";
import logoutIcon from "./../Icons/logout.png";

import { useNavigate } from "react-router-dom";

function LogoutButton({ logoutCallback }) {
    const navigation = useNavigate();

    function logout() {
        fetch("http://localhost:5000/logout", {
            method: "POST",
            credentials: "include",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({}),
        })
        .then((res) => res.json())
        .then((data) => {
            if (logoutCallback) logoutCallback();
            navigation("/login/");
        })
        .catch((e) => alert(e));
    }
    
    return (
        <div class="logoutButtonWrapper">
            <button onClick={logout}><img src={logoutIcon}/></button>
        </div>
    );
}

export default LogoutButton;