import "./App.css";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";

// --- custom pages --- 
import MainPage from "./Pages/MainPage";
import LoginPage from "./Pages/LoginPage";
import RegistrationPage from "./Pages/RegistrationPage";
import HomePage from "./Pages/HomePage";
import AlbumPage from "./Pages/AlbumPage";

function App() {
    return(
        <div id="appWrapper">
            <Router>
                <Routes>
                    <Route path="/" element={
                        <MainPage/>
                    }/>

                    <Route path="/login/" element={
                        <LoginPage/>
                    }/>

                    <Route path="/register/" element={
                        <RegistrationPage/>
                    }/>

                    <Route path="/home/" element={
                        <HomePage/>
                    }/>

                    <Route path="/album/" element={
                        <AlbumPage/>
                    }/>
                </Routes>
            </Router>
        </div>
    );
}

export default App;