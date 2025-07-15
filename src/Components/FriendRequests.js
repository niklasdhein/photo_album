import "./FriendRequests.css";
import xIcon from "../Icons/x.png";
import checkIcon from "../Icons/check.png";

import { useEffect, useState } from "react";

function FriendRequests({ isShown, reloadFriendsOnRequestAccept }) {
    const [requests, setRequests] = useState({toUser: [], byUser: []});
    const [showReceived, setShowReceived] = useState(true);
    
    // Sends a post request to the backend trying to delete the request sent to the user
    function deleteRequestToUser(fromUserId) {
        fetch("http://localhost:5000/delete_request_to_user", {
            method: "POST",
            credentials: "include",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({fromUserId: fromUserId}),
        })
        .then((res) => {
            if (res.ok) getFriendRequests();
            else return res.json();
        })
        .then((data) => {if (data.ans) alert(data.ans);})
        .catch((e) => alert(e));
    }

    // Sends a post request to the backend trying to delete the request sent by the user 
    function deleteRequestByUser(toUserId) {
        fetch("http://localhost:5000/delete_request_by_user", {
            method: "POST",
            credentials: "include",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({toUserId: toUserId}),
        })
        .then((res) => {
            if (res.ok) getFriendRequests();
            else return res.json();
        })
        .then((data) => {if (data.ans) alert(data.ans);})
        .catch((e) => alert(e));
    }

    // Fetches all requests a user has (received and sent) from the backend
    function getFriendRequests() {
        // Get all requests sent to and by the user
        fetch("http://localhost:5000/get_friend_requests", {
            method: "GET",
            credentials: "include",
        })
        .then((res) => res.json())
        .then((data) => {
            if (data.ans) alert(data.ans);
            else setRequests(data);
        })
        .catch((e) => alert(e));
    }

    // Sends a post request to the backend trying to accept a friendrequest 
    // and creating a friendship
    function acceptRequest(fromUserId) {
        fetch("http://localhost:5000/accept_request", {
            method: "POST",
            credentials: "include",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({fromUserId: fromUserId}),
        })
        .then((res) => {
            if (res.ok) {
                getFriendRequests();
                if (reloadFriendsOnRequestAccept) reloadFriendsOnRequestAccept();
            }
            else return res.json();
        })
        .then((data) => {if (data.ans) alert(data.ans);})
        .catch((e) => alert(e));
    } 

    // Called when the page loads
    useEffect(() => {
        getFriendRequests();
    }, []);

    // Called when the state wether the component is shown or not changes
    useEffect(() => {
        getFriendRequests();
    }, [isShown]);
    
    return (
        (isShown)
        ?
        <div id="friendRequestsWrapper">
            <div id="friendRequestsWrapperControlBar">
                <button
                className={(showReceived) ? "friendRequestsWrapperControlBarSelected" : ""} 
                onClick={() => setShowReceived(true)}
                >Received</button>
                <button 
                className={(!showReceived) ? "friendRequestsWrapperControlBarSelected" : ""}
                onClick={() => setShowReceived(false)}
                >Sent</button>
            </div>
            <div id="friendRequestsDisplayer">
                {
                (showReceived)
                ?
                    (requests.toUser.length > 0)
                    ?
                    requests.toUser.map((r) => (
                    <div 
                    className="friendRequest"
                    key={"friendRequest_"+r.id}
                    >
                        <p><strong>{r.email}</strong> wants to be your friend</p>
                        <div className="receivedRequestOptions">
                            <button 
                            className="decline"
                            onClick={() => deleteRequestToUser(r.id)}
                            ><img src={xIcon}/></button>
                            <button 
                            className="accept"
                            onClick={() => acceptRequest(r.id)}
                            ><img src={checkIcon}/></button>
                        </div>
                    </div>  
                    ))
                    :
                    <p>No friendrequests received yet..</p>
                :
                    (requests.byUser.length > 0)
                    ?
                    requests.byUser.map((r) => (
                    <div
                    className="friendRequest"
                    key={"friendRequest_"+r.id}
                    >
                        <p>Sent friendrequest to <strong>{r.email}</strong></p>
                        <div className="receivedRequestOptions">
                            <button 
                            className="decline"
                            onClick={() => deleteRequestByUser(r.id)}
                            ><img src={xIcon}/></button>
                        </div>
                    </div>
                    ))
                    :
                    <p>No pending requests currently</p>
                }
            </div>
        </div>
        : null
    );
}

export default FriendRequests;