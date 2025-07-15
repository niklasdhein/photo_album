import { useState } from "react";

function FriendButton({ friendName }) {
    return (
        <div class="friendButtonWrapper">   
            <button>{friendName}</button>
        </div>
    );
}

export default FriendButton;