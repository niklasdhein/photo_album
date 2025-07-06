import "./DeleteImagesAlertBox.css";

function DeleteImageAlertBox({ message, hideAction, confirmAction, isShown }) {
    return (
        (isShown)
        ?
        <div id="deleteAlbumAlertBoxWrapper">
            <div id="deleteAlbumAlertBoxWidget">
                <h2>{message}</h2>
                <div id="deleteAlbumAlertBoxButtons">
                    <button 
                    id="deleteAlbumAlertBoxCancel" 
                    onClick={hideAction}>Cancel</button>
                    <button 
                    id="deleteAlbumAlertBoxConfirm"
                    onClick={() => {
                        confirmAction(imageName);
                        hideAction();
                    }}>Delete</button>
                </div>  
            </div>
        </div>
        :
        null
    );
}

export default DeleteImageAlertBox;