import "./AddFriendSection.css";

import { useState } from "react";

function AddFriendSection({ showAddFriendSection, reloadFriends }) {
    const [friendName, setFriendName] = useState("");
    
    return (
        <div id="addFriendSectionWrapper">
            <input
            type="text" 
            placeholder="Enter friend name here.."
            value={friendName}
            onChange={(e) => setFriendName(e.target.value)}
            />
            <button onClick={() => {
                showAddFriendSection(false);
                fetch("http://localhost:5000/add_friend_request", {
                    method: "POST",
                    credentials: "include",
                    headers: {"Content-Type": "application/json"},
                    body: JSON.stringify({friendName: friendName}),
                })
                .then((res) => {if (!res.ok) return res.json()})
                .then((data) => {
                    if (data) alert(data.ans);

                    // Hides the add friend section
                    if (showAddFriendSection) showAddFriendSection();
                    setFriendName("");
                    reloadFriends();
                })
                .catch((e) => alert(e));
            }}>Create</button>
        </div>
    );
}

export default AddFriendSection;