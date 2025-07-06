import "./HomePage.css";
import plusIcon from "../Icons/plus.png";

import { useEffect, useState } from "react";

// --- custom imports ---
import AlbumButton from "../Components/AlbumButton";
import FriendButton from "../Components/FriendButton";
import AddAlbumSection from "../Components/AddAlbumSection";
import AlertBox from "../Components/AlertBox";

function HomePage() {
    // Used to load and store the email of logged in user
    const [email, setEmail] = useState("");              
    
    // Used to store if section for adding an album is shown
    const [showAddAlbumSection, setShowAddAlbumSection] = useState(false);
    
    // Stores loaded albums received from backend
    const [loadedAlbums, setLoadedAlbums] = useState([])                    
    const maxAmountOfLoadedAlbums = 6;

    //Wether alert box is shown or not
    const [showAlbumAlert, setShowAlbumAlert] = useState(true);


    // Called on page load
    useEffect(() => {
        loadEmail();
        getAlbums();
    }, []);


    // Load email of logged in user
    function loadEmail() {
        fetch("http://localhost:5000/get_login_status", {
            method: "GET",
            credentials: "include",
        })
        .then((res) => res.json())
        .then((data) => setEmail(data.email))
        .catch((e) => alert(e));
    }


    // Load albums of logged in user
    function getAlbums() {
        fetch("http://localhost:5000/get_albums?amount="+maxAmountOfLoadedAlbums, {
            method: "GET",
            credentials: "include",
        })
        .then((res) => res.json())
        .then((data) => setLoadedAlbums(data))
        .catch((e) => alert(e));
    } 
    
    return(
        <div id="homePageWrapper">
            {
            (showAlbumAlert)
            ? <AlertBox message="test" onConfirm={() => setShowAlbumAlert(false)}/>
            : null
            }
            <div id="homePageTop">
                <h1>Welcome back {email}!</h1>
            </div>
            <div id="homePageAlbumsWrapper">
                <div id="homePageAlbumsTop">
                    <h2>Your albums</h2>
                    <div id="homePageAlbumsTopRight">
                        <p>Add new</p>
                        <button
                        onClick={() => {setShowAddAlbumSection(!showAddAlbumSection)}
                        }>
                            <img src={plusIcon}/>
                        </button>
                    </div>
                </div>
                {
                (showAddAlbumSection)
                ?
                <AddAlbumSection 
                showAlbumSectionCallback={setShowAddAlbumSection}
                reloadAlbumsCallback={getAlbums}
                />
                :
                null
                }
                <div id="homePageAlbums">
                    {
                    loadedAlbums.map((album) => (
                            <AlbumButton 
                            key={album.id} 
                            id={album.id}
                            name={album.name}
                            />))
                    }
                </div>
            </div>
            <div id="homePageFriendsWrapper">
                <div id="homePageFriendsTop">
                    <h2>Your friends</h2>
                    <div id="homePageFriendsTopRight">
                        <p>Invite new</p>
                        <button><img src={plusIcon}/></button>
                    </div>
                </div>
                <div id="homePageFriends">
                    <FriendButton name="TEST"/>
                    <FriendButton name="TEST"/>
                    <FriendButton name="TEST"/>
                    <FriendButton name="TEST"/>
                </div>
            </div>
        </div>
    );
} 

export default HomePage;