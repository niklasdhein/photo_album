import "./AlbumPage.css";
import trashIcon from "./../Icons/trash.png";
import tagIcon from "../Icons/tag.png";
import xIcon from "../Icons/x.png";

import { useSearchParams } from "react-router-dom";
import { useState, useEffect } from "react";

import HomeButton from "./../Components/HomeButton";
import DeleteImagesAlertBox from "../Components/DeleteImagesAlertBox";
import AddTagAlert from "../Components/AddTagAlert";

function AlbumPage() {
    // URL params stored for access here
    const [searchParams] = useSearchParams();

    // Album id and name stored for later use
    const albumId = searchParams.get("id");
    const albumName = searchParams.get("name");

    // Stores file names of images the user wants to upload
    const [imageFileNames, setImageFileNames] = useState([]);
    const [isUploading, setIsUploading] = useState(false);

    // Information about the alert shown when user wants to delete images
    const [deleteImagesAlert, setDeleteImagesAlert] = useState({
        isShown: false,
        imagesToDelete: [],
    });
    const [imagesSelected, setImagesSelected] = useState(0);

    // Information about the tag menu rendered in an alert-like style
    const [tagAlert, setTagAlert] = useState({
        isShown: false,
        imageName: null,
    });

    // Stores loaded tags of an image
    const [imageTags, setImageTags] = useState([]);

    // Stores all the loaded tags an album includes
    const [albumTags, setAlbumTags] = useState([]);

    // Called on page (re)load
    useEffect(() => {
        getImages();
        getAlbumTags();
    }, []);

    // Sends an post request to the backend to delete the passed image
    function deleteImages(imageNames) {
        fetch("http://localhost:5000/delete_images", {
            method: "POST",
            credentials: "include",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({imageNames: imageNames}),
        })
        .then((res) => {
            if (res.ok) {
                // Reset the images to delete after successful deletion
                setImagesSelected(0);
                getImages();
                return null;
            }
            else {
                return res.json();
            }
        })
        .then((data) => {
            if (data) alert(data.ans);
        })
        .catch((e) => alert(e));
    }
            
    // Gets all image file names of current album from backend
    function getImages() {
        fetch("http://localhost:5000/get_images?albumId="+albumId, {
            method: "GET",
            credentials: "include",
        })
        .then((res) => res.json())
        .then((data) => setImageFileNames(data.ans))
        .catch((e) => alert(e));
    }

    // Posts selected images by the user to the backend
    function postImages(files) {
        if (!files || isUploading) return;
        
        setIsUploading(true);
        const formData = new FormData();
        
        // Append all images
        for (let i = 0; i < files.length; i++) {
            formData.append("images", files[i]);
        }

        // Append the albums id 
        formData.append("albumId", albumId);
        
        // Post data to backend
        fetch("http://localhost:5000/post_images", {
            method: "POST",
            credentials: "include",
            body: formData,
        })
        .then((res) => {
            // Reload shown images after successful upload
            if (res.ok) {
                setIsUploading(false);
                getImages();
            }
        })
        .catch((e) => alert(e));
    }

    // Gets tags from backend (used when user hovers over tag icon)
    function getTags(imageName) {
        fetch("http://localhost:5000/get_tags_of_image?imageName="+imageName, {
            method: "GET",
            credentials: "include",
        })
        .then((res) => res.json())
        .then((data) => {
            if (data.ans) alert(data.ans);
            else setImageTags(data);
        })
        .catch((e) => alert(e));
    }

    // Sends request to backend to delete that tag from this image
    function deleteTagFromImage(tagId, imageName) {
        fetch("http://localhost:5000/delete_tag_from_image", {
            method: "POST",
            credentials: "include",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({
                tagId: tagId,
                imageName: imageName,
            })
        })
        .then((res) => {if (!res.ok) return res.json(); else {getTags(imageName); getAlbumTags();}})
        .then((data) => {if (data) alert(data.ans);})
        .catch((e) => alert(e));
    }

    // Gets all tags used in that album
    function getAlbumTags() {
        fetch("http://localhost:5000/get_tags_of_album?albumId="+albumId, {
            method: "GET",
            credentials: "include",
        })   
        .then((res) => res.json())
        .then((data) => {
            if (data.ans) alert(data.ans);
            else setAlbumTags(data);
        })
        .catch((e) => alert(e));
    }

    return (    
        <div id="albumPageWrapper">
            <DeleteImagesAlertBox 
                message="Are you sure you want to delete this?" 
                hideAction={() => {
                    setDeleteImagesAlert({isShown: false, imagesToDelete: []});
                    setImagesSelected(0);
                }}
                confirmAction={deleteImages}
                isShown={deleteImagesAlert.isShown}
                imageName={deleteImagesAlert.imagesToDelete}
            />

            <AddTagAlert
                isShown={tagAlert.isShown}
                imageName={tagAlert.imageName}
                hideAction={() => setTagAlert({isShown: false, imageName: null,})}
                reloadAlbumTags={getAlbumTags}
            />

            <div id="albumPageTop">
                <div id="albumPageTopLeft">
                    <h1>{albumName}</h1>
                    {
                    (imagesSelected > 0)
                    ? 
                    <div id="albumPageSelectedInfo">
                        <button 
                        id="albumPageDeleteImagesButton"
                        onClick={() => {
                            setDeleteImagesAlert({
                                isShown: true,
                                imagesToDelete: deleteImagesAlert.imagesToDelete,
                            })
                        }}
                        ><img src={trashIcon}/></button>
                        {
                        (imagesSelected == 1)
                        ? <p>Delete 1 image</p>
                        : <p>Delete {imagesSelected} images</p>
                        }
                    </div>
                    : null
                    }
                </div>
                <div id="albumPageTopControls">
                    <label>
                        {
                        (isUploading)
                        ? "Uploading.."
                        : "Upload images"
                        }
                        <input 
                        type="file" 
                        multiple
                        accept="image/*" 
                        onChange={(e) => postImages(e.target.files)}
                        style={{ display: "none" }}
                        />
                    </label>
                    <HomeButton/>
                </div>
            </div>

            <div id="albumPageContent">
                {
                (imageFileNames.length > 0)
                ?
                <div id="albumPageGalleryWrapper">
                    {
                    (albumTags.length > 0)
                    ?
                    <div id="albumPageTagDisplayer">
                    {
                    albumTags.map((t) => (<p key={`album_tag_${t.id}`}>{t.name}</p>))
                    }
                    </div>
                    : null
                    }  
                    <div id="albumPageGallery">
                    {
                        imageFileNames.map((imageName) => (
                            <div 
                            key={imageName} 
                            className="albumPageImageWrapper"
                            onMouseEnter={() => getTags(imageName)}
                            onMouseLeave={() => setImageTags([])}
                            >
                                <img src={`http://localhost:5000/get_image_file/${imageName}`}/>
                                {
                                (imagesSelected == 0)
                                ?
                                <button 
                                className="albumPageDeleteButton"
                                onClick={() => setDeleteImagesAlert({
                                    isShown: true,
                                    imagesToDelete: [...deleteImagesAlert.imagesToDelete, imageName],
                                })}
                                ><img src={trashIcon}/></button>
                                : null
                                }
                                <input
                                className="albumPageSelectorBox"
                                type="checkbox"
                                onChange={(e) => {
                                    // For CSS to always render if an image is selected
                                    e.target.className = `albumPageSelectorBox ${(e.target.checked) ? "albumPageSelected" : ""}`;
                                    setDeleteImagesAlert(() => {
                                        // Box is checked and image is not marked to delete
                                        if (e.target.checked && !deleteImagesAlert.imagesToDelete.includes(imageName)) {
                                            setImagesSelected(imagesSelected+1);
                                            return {isShown: deleteImagesAlert.isShown, 
                                                    imagesToDelete: [...deleteImagesAlert.imagesToDelete, imageName]};
                                        }
                                        // Box is unchecked but image is still marked to delete
                                        else if (!e.target.checked && deleteImagesAlert.imagesToDelete.includes(imageName)) {
                                            setImagesSelected(imagesSelected-1);
                                            return {isShown: deleteImagesAlert.isShown, 
                                                    imagesToDelete: deleteImagesAlert.imagesToDelete.filter((img) => img !== imageName)};
                                        }
                                        // If no real change is detected just leave the state as it is
                                        else {
                                            return {isShown: deleteImagesAlert.isShown, 
                                                    imagesToDelete: deleteImagesAlert.imagesToDelete};
                                        }
                                    })
                                }}
                                />
                                <div className="albumPageTagsWrapper">
                                    <button
                                    className="albumPageTagButton"
                                    onClick={() => setTagAlert({
                                        isShown: true,
                                        imageName: imageName,
                                    })}>
                                    <img src={tagIcon}/>
                                    </button>
                                    {
                                    (imageTags.length > 0)
                                    ? 
                                        (imageTags.length == 1)
                                        ? <p className="albumPageTagAmount">1 tag</p>
                                        : <p className="albumPageTagAmount">{imageTags.length} tags</p>
                                    : null
                                    }
                                    {
                                    (imageTags.length > 0)
                                    ? 
                                    imageTags.map((t) => (
                                        <div className="albumPageTagWrapper" key={t.id}>
                                            <p>{t.name}</p>
                                            <img 
                                            src={xIcon}
                                            onClick={() => {
                                                deleteTagFromImage(t.id, imageName)
                                            }}
                                            />
                                        </div>
                                    ))
                                    :
                                    <p className="albumPageTagP">Add tag</p>
                                    }
                                </div>    
                            </div>
                        ))
                    }
                    </div>
                    <p id="albumPageEndP">You have reached the end of this album</p>
                </div>
                : 
                <p id="albumPageUploadP">Start by uploading some images..</p>
                }
            </div>
        </div>
    );
}

export default AlbumPage;