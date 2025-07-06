import "./AlbumPage.css";
import trashIcon from "./../Icons/trash.png";

import { useSearchParams } from "react-router-dom";
import { useState, useEffect } from "react";

import HomeButton from "./../Components/HomeButton";
import DeleteImagesAlertBox from "../Components/DeleteImagesAlertBox";

function AlbumPage() {
    const [searchParams] = useSearchParams();

    const albumId = searchParams.get("id");
    const albumName = searchParams.get("name");

    const [imageFileNames, setImageFileNames] = useState([]);
    const [isUploading, setIsUploading] = useState(false);

    const [deleteImagesAlert, setDeleteImagesAlert] = useState({
        isShown: false,
        imagesToDelete: [],
    });
    const [imagesSelected, setImagesSelected] = useState(0);

    // Called on page (re)load
    useEffect(() => {
        getImages();
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

    // --- Some custom components ---
    function OnSelectedBar() {
        return (
            <div id="albumPageOnSelectedBarWrapper">
                <h2>Selection</h2>
                <div id="albumPageOnSelectedBar">
                    <button onClick={() => {
                        setDeleteImagesAlert({isShown: true, 
                        imagesToDelete: deleteImagesAlert.imagesToDelete})
                        }}>
                        <img src={trashIcon}/>
                    </button>
                    {
                    (imagesSelected > 1)
                    ? <p>Delete {imagesSelected} images</p>
                    : <p>Delete 1 image</p>
                    }
                </div>
            </div>
        );
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

            <div id="albumPageTop">
                <h1>{albumName}</h1>
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
                { (imagesSelected > 0) ? <OnSelectedBar/> : null }
                {
                (imageFileNames.length > 0)
                ?
                <div id="albumPageGalleryWrapper">
                    <div id="albumPageGallery">
                    {
                        imageFileNames.map((imageName) => (
                            <div key={imageName} class="albumPageImageWrapper">
                                <img src={`http://localhost:5000/get_image_file/${imageName}`}/>
                                {
                                (imagesSelected == 0)
                                ?
                                <button 
                                class="albumPageDeleteButton"
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
                            </div>
                        ))
                    }
                    </div>
                    <p>You have reached the end of this album</p>
                </div>
                : 
                <p>Start by uploading some images..</p>
                }
            </div>
        </div>
    );
}

export default AlbumPage;