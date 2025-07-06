import "./DeleteImagesAlertBox.css";

function DeleteImageAlertBox({ message, hideAction, confirmAction, isShown, imageName }) {
    return (
        (isShown)
        ?
        <div id="deleteImageAlertBoxWrapper">
            <div id="deleteImageAlertBoxWidget">
                <h2>{message}</h2>
                <div id="deleteImageAlertBoxButtons">
                    <button 
                    id="deleteImageAlertBoxCancel" 
                    onClick={hideAction}>Cancel</button>
                    <button 
                    id="deleteImageAlertBoxConfirm"
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