import "./Navbar.css"

import { useState, useEffect } from "react";

// --- custom components ---
import HomeButton from "./HomeButton";

function Navbar() {
    const [email, setEmail] = useState(null);
    
    // Load the email of currently logged in user
    useEffect(() => {
        fetch("http://localhost:5000/get_login_status", {
            method: "GET",
            credentials: "include",
        })
        .then((res) => res.json())
        .then((data) => setEmail(data.email))
        .catch((e) => alert(e));
    }, []);

    return (
        <div id="navbarWrapper">
            <div id="navbar">
                <div id="navbarLeftRegion">
                    <p>Discover</p>
                </div>
                <div id="navbarRightRegion">
                    <p>Logged in as {email}</p>
                    <HomeButton/>
                </div>
            </div>
        </div>
    );
}

export default Navbar;