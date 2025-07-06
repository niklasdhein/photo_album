import "./AddAlbumSection.css";
import { useState } from "react";

// Section shown when the user wants to add an album
function AddAlbumSection({ showAlbumSectionCallback, reloadAlbumsCallback }) {
    const [albumName, setAlbumName] = useState("");

    return (
        <div id="addAlbumSectionWrapper">
            <input
            type="text" 
            placeholder="Enter album name here.."
            value={albumName}
            onChange={(e) => setAlbumName(e.target.value)}
            />
            <button onClick={() => {
                showAlbumSectionCallback(false);
                fetch("http://localhost:5000/add_album", {
                    method: "POST",
                    credentials: "include",
                    headers: {"Content-Type": "application/json"},
                    body: JSON.stringify({name: albumName}),
                })
                .then((res) => res.json())
                .then(() => {
                    // Calls a function to reload albums if passed
                    if (reloadAlbumsCallback) reloadAlbumsCallback();
                    setAlbumName("");
                })
                .catch((e) => alert(e));
            }}>Create</button>
        </div>
    );
}

export default AddAlbumSection;