import "./Gallery.css";

// --- TEST IMAGES ---
import fields from "./../TestImages/fields.jpg";
import mountains from "./../TestImages/mountains.jpg";
import rx_7 from "./../TestImages/rx-7_slammed.jpg";
import starman from "./../TestImages/starman.png";
import twilight from "./../TestImages/twilight.jpg";

function Gallery() {
    return(
        <div id="galleryWrapper">
            <h1>Recommended for you</h1>
            <div id="gallery">
                <img src={fields}/>
                <img src={mountains}/>
                <img src={rx_7}/>
                <img src={starman}/>
                <img src={twilight}/>
            </div>
        </div>
    );
}

export default Gallery;