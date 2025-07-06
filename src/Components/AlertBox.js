import "./AlertBox.css";

function AlertBox({ message, onConfirm }) {
    return (
        <div id="alertBoxWrapper">
            <div id="alertBoxWidget">
                <h1>{message}</h1>
                <button onClick={onConfirm}>Okay</button>
            </div>
        </div>
    );
}

export default AlertBox;