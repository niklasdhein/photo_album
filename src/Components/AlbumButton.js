import { useNavigate } from "react-router-dom";

function AlbumButton({ id, name }) {
    const navigation = useNavigate();

    return (
        <div class="albumButtonWrapper">
            <button onClick={() => {
                navigation("/album?id="+id+"&name="+name);
            }}
            >{name}</button>
        </div>
    );
}

export default AlbumButton;