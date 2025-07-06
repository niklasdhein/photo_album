import "./HomeButton.css";
import homeIcon from "./../Icons/home.png";

import { useNavigate } from "react-router-dom";

function HomeButton() {
    const navigation = useNavigate();
    
    return (
        <div class="homeButtonWrapper">
            <button onClick={() => navigation("/home/")}><img src={homeIcon}/></button>
        </div>
    );
}

export default HomeButton;