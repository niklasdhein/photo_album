import "./HomePage.css";
import plusIcon from "../Icons/plus.png";
import trashIcon from "../Icons/trash.png";
import friendsIcon from "../Icons/friends.png";

import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

// --- custom imports ---
import AlbumButton from "../Components/AlbumButton";
import FriendButton from "../Components/FriendButton";
import AddAlbumSection from "../Components/AddAlbumSection";
import DeleteAlbumAlert from "../Components/DeleteAlbumAlert";
import LogoutButton from "../Components/LogoutButton";
import AddFriendSection from "../Components/AddFriendSection";
import FriendRequests from "../Components/FriendRequests";

function HomePage() {
    const navigation = useNavigate();

    // Used to load and store the email of logged in user
    const [email, setEmail] = useState("");              
    
    // Used to store if section for adding an album is shown
    const [showAddAlbumSection, setShowAddAlbumSection] = useState(false);
    
    // Stores loaded albums received from backend
    const [loadedAlbums, setLoadedAlbums] = useState([])                    

    // Stores which album the user wants to delete and wether the alert for that is shown
    const [deleteInfo, setDeleteInfo] = useState({isShown: false, album: null});

    // Wether add friend section is shown (same as showAddAlbumSection)
    const [showAddFriendSection, setShowAddFriendSection] = useState(false);

    // Stores id and name of each friend the user has
    const [loadedFriends, setLoadedFriends] = useState([]);

    // Wether the users friend requests are shown or not
    const [showFriendRequests, setShowFriendRequests] = useState(false);


    // Called on page load
    useEffect(() => {
        loadEmail();
        getAlbums();
        loadFriends();
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
        fetch("http://localhost:5000/get_albums", {
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

    // Loads id and name for each friend the user has
    function loadFriends() {
        fetch("http://localhost:5000/get_friends", {
            method: "GET",
            credentials: "include"
        })
        .then((res) => res.json())
        .then((data) => {
            if (data.ans) alert(data.ans);
            else setLoadedFriends(data);
        })
        .catch((e) => alert((e)));
    }

    // Sends a post request to backend to remove this friend
    function removeFriend(friendId) {
        fetch("http://localhost:5000/remove_friend", {
            method: "POST",
            credentials: "include",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({friendId: friendId}),
        })
        .then((res) => {
            loadFriends();
            if (!res.ok) return res.json()
        })
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
                    <div id="homePageTopRight">
                        <button
                        onClick={() => setShowFriendRequests(!showFriendRequests)}
                        ><img src={friendsIcon}/></button>
                        <FriendRequests 
                        isShown={showFriendRequests}
                        reloadFriendsOnRequestAccept={loadFriends}
                        />
                        <LogoutButton/>
                    </div>
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
                        (loadedAlbums.length > 0)
                        ?
                        loadedAlbums.map((album) => (
                            <div className="albumWrapper" key={album.id}>
                                <AlbumButton  
                                id={album.id}
                                name={album.name}
                                />
                                <button 
                                className="albumDeleteButton"
                                onClick={() => {
                                    setDeleteInfo({isShown: true, album: album.id});
                                }}
                                ><img src={trashIcon}/></button>
                            </div>
                        ))
                        : <p>Create your first album!</p>
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
                            onClick={() => setShowAddFriendSection(!showAddFriendSection)}
                            ><img src={plusIcon}/></button>
                        </div>
                    </div>
                    {
                    (showAddFriendSection)
                    ? 
                    <AddFriendSection 
                    showAddFriendSection={setShowAddFriendSection}
                    reloadFriends={loadFriends}
                    />
                    : null
                    }
                    <div id="homePageFriends">
                        {
                        (loadedFriends.length > 0)
                        ?
                        loadedFriends.map((f) => (
                        <div className="friendWrapper" key={"friendButton_"+f.id}>
                            <FriendButton
                            friendName={f.email}
                            />
                            <button 
                                className="friendDeleteButton"
                                onClick={() => removeFriend(f.id)}
                            ><img src={trashIcon}/></button>
                        </div>
                        ))
                        : 
                        <p>You have no friends..</p>
                        }
                    </div>
                </div>
            </div>
        </div>
    );
} 

export default HomePage;