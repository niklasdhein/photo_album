import { useState } from "react";

function FriendButton({ name }) {
    const [friendName, setFriendName] = useState(name);

    return (
        <div class="friendButtonWrapper">   
            <button>{friendName}</button>
        </div>
    );
}

export default FriendButton;