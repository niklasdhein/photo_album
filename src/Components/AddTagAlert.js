import "./AddTagAlert.css";

import { useState, useEffect } from "react";

import xIcon from "../Icons/x.png";

function AddTagAlert({ isShown, imageName, hideAction }) {
    const [tagInput, setTagInput] = useState("");   // Stores tag input field's value
    const [tags, setTags] = useState([]);            // All tags from the user
    
    // If alert is shown load tags
    useEffect(() => {
        if (!isShown) return;
        loadTags();
    }, [isShown]);

    // Sends a new tag to add for that image the backend
    function addTag() {
        fetch("http://localhost:5000/add_tag", {
            method: "POST",
            credentials: "include",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({
                imageName: imageName,
                tag: tagInput,
            })
        })
        .then((res) => {if (!res.ok) return res.json();})
        .then((data) => {
            setTagInput("");
            loadTags();
            if (data) alert(data.ans);
            else hideAction();
        })
        .catch((e) => alert(e));
    }

    function addExistingTag(tagId) {
        fetch("http://localhost:5000/add_existing_tag", {
            method: "POST",
            credentials: "include",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({
                imageName: imageName,
                tagId: tagId,
            })
        })
        .then((res) => {if (!res.ok) return res.json();})
        .then((data) => {
            setTagInput("");
            loadTags();
            if (data) alert(data.ans);
            else hideAction();
        })
        .catch((e) => alert(e));
    }

    // Sends delete request to backend
    function deleteTag(tagId) {
        fetch("http://localhost:5000/delete_tag", {
            method: "POST",
            credentials: "include",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({
                tagId: tagId,
            }),
        })
        .then((res) => {
            if (!res.ok) return res.json();
        })
        .then((data) => {
            loadTags();
            if (data) alert(data.ans);
        })
        .catch((e) => alert(e));
    }   

    // Loads tags from user from backend
    function loadTags() {
        fetch("http://localhost:5000/get_tags?imageName="+imageName, {
            method: "GET",
            credentials: "include",
        })
        .then((res) => res.json())
        .then((data) => {
            if (data.ans) alert(data.ans);
            else setTags(data);
        })
        .catch((e) => alert(e));
    }

    return (
        (isShown)
        ?
        <div id="addTagAlertWrapper">
            <div id="addTagAlertWidget">
                <div id="addTagAlertHead">
                    <h2>Use a new tag</h2>
                    <button onClick={() => {
                        hideAction();
                        setTags([]);            // Just clean
                        setTagInput("");        // up a little
                    }}>Cancel</button>
                </div>
                <div id="addTagAlertInputWrapper">
                    <input 
                    type="text" 
                    placeholder="Give your tag a name"
                    value={tagInput}
                    onChange={(e) => setTagInput(e.target.value)}
                    />
                    <button
                    onClick={addTag}
                    >Create</button>
                </div>
                <h2>Select an existing tag</h2>
                <div id="addTagAlertExistingWrapper">
                    {
                        (tags.length > 0)
                        ?
                        tags.map((t) => (
                            <div class="addTagAlertTags" key={t.id+t.name}>
                                <p
                                onClick={() => addExistingTag(t.id)}
                                >{t.name}</p>
                                <img 
                                src={xIcon}
                                onClick={() => deleteTag(t.id)}
                                />
                            </div>
                        ))
                        :
                        <p id="addTagAlertPlaceholderP">No tags created yet</p>
                    }
                </div>
            </div>
        </div>
        : 
        null 
    );
}

export default AddTagAlert;