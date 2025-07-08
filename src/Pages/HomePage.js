import "./HomePage.css";
import plusIcon from "../Icons/plus.png";
import trashIcon from "../Icons/trash.png";

import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

// --- custom imports ---
import AlbumButton from "../Components/AlbumButton";
import FriendButton from "../Components/FriendButton";
import AddAlbumSection from "../Components/AddAlbumSection";
import DeleteAlbumAlert from "../Components/DeleteAlbumAlert";
import LogoutButton from "../Components/LogoutButton";

function HomePage() {
    const navigation = useNavigate();

    // Used to load and store the email of logged in user
    const [email, setEmail] = useState("");              
    
    // Used to store if section for adding an album is shown
    const [showAddAlbumSection, setShowAddAlbumSection] = useState(false);
    
    // Stores loaded albums received from backend
    const [loadedAlbums, setLoadedAlbums] = useState([])                    
    const maxAmountOfLoadedAlbums = 6;

    // Stores which album the user wants to delete and wether the alert for that is shown
    const [deleteInfo, setDeleteInfo] = useState({isShown: false, album: null});


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
        .then((data) => {
            // Redirect user to login if he is not logged in
            if (!data.email) navigation("/login/");
            else setEmail(data.email);
        })
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

    // Deletes an album
    function deleteAlbum() {
        fetch("http://localhost:5000/delete_album", {
            method: "POST",
            credentials: "include",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({albumId: deleteInfo.album}),
        })
        .then((res) => {getAlbums(); if (!res.ok) return res.json();})
        .then((data) => {if (data) alert(data.ans);})
        .catch((e) => alert(e));
    }
    
    return(
        <div id="homePageWrapperWrapper">
            <DeleteAlbumAlert
                message={"Are you sure you want to delete this album?"}
                album={deleteInfo.album}
                isShown={deleteInfo.isShown}
                hideAction={() => setDeleteInfo({isShown: false, album: null})}
                confirmAction={deleteAlbum}
            />
            <div id="homePageWrapper">
                <div id="homePageTop">
                    <h1>Welcome back {email}!</h1>
                    <LogoutButton/>
                </div>
                <div id="homePageAlbumsWrapper">
                    <div id="homePageAlbumsTop">
                        <h2>Your albums</h2>
                        <div id="homePageAlbumsTopRight">
                            <p>Add new</p>
                            <button
                            id="homePageAddAlbumButton"
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
                            <div class="albumWrapper">
                                <AlbumButton 
                                key={album.id} 
                                id={album.id}
                                name={album.name}
                                />
                                <button 
                                class="albumDeleteButton"
                                onClick={() => {
                                    setDeleteInfo({isShown: true, album: album.id});
                                }}
                                ><img src={trashIcon}/></button>
                            </div>
                        ))
                        }
                    </div>
                </div>
                <div id="homePageFriendsWrapper">
                    <div id="homePageFriendsTop">
                        <h2>Your friends</h2>
                        <div id="homePageFriendsTopRight">
                            <p>Invite new</p>
                            <button
                            id="homePageAddFriendButton"
                            ><img src={plusIcon}/></button>
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
        </div>
    );
} 

export default HomePage;