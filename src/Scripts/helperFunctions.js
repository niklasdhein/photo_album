var BACKEND_URL = "http://localhost:5000/"

function do_json_post_request(route, body, callOnBackendRes, callOnSuccess) {
    // Do a post request, hand over the passed body
    fetch(BACKEND_URL+route, {
        method: "POST",
        credentials: "include",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify(body)
    })
    .then((res) => {
        if (!res.ok) return res.json();             // If the res wasn't okay, format to json to use it
        else if (callOnSuccess) callOnSuccess();    // If the res was okay, call a callback function (optionally)
    })
    .then((data) => {
        if (data && callOnBackendRes) callOnBackendRes(data.ans);  // Callback for when something wasn't okay, 
    })                                                          // pass backend ans then
    .catch((e) => alert(e));    // Just alert any errors
}

function do_json_get_request(route, callOnBackendRes, callOnSuccess) {
    // Do a get request
    fetch(BACKEND_URL+route, {
        method: "GET",
        credentials: "include"
    })
    .then((res) => res.json())  // Just format the response to json
    .then((data) => {
        if (data.ans && callOnBackendRes) callOnBackendRes(data.ans);   // If there is an answer (only errors) do this callback
        else if (data && callOnSuccess) callOnSuccess(data);
    })
    .catch((e) => alert(e));
}



// Logs an existing user into his account
export function login(email, password, callOnBackendRes, callOnSuccess) {
    do_json_post_request("login", {email: email, password: password}, callOnBackendRes, callOnSuccess);
}

// Gets session login status for a logged in user
export function get_login_status(callOnBackendRes, callOnSuccess) {
    do_json_get_request("get_login_status", callOnBackendRes, callOnSuccess);
}

// Logs a user out of its session
export function logout(callOnBackendRes, callOnSuccess) {
    do_json_post_request(BACKEND_URL+"logout", {}, callOnBackendRes, callOnSuccess);
}

// Reqisters a new account with the given email and password in the database
export function register(email, password, callOnBackendRes, callOnSuccess) {
    do_json_post_request(BACKEND_URL+"register", {email: email, password: password}, callOnBackendRes, callOnSuccess);
}

// Creates an album with the passed name for the currently logged in user in the database
export function add_album(name, callOnBackendRes, callOnSuccess) {
    do_json_post_request(BACKEND_URL+"add_album", {name: name}, callOnBackendRes, callOnSuccess);
}

// Gets all albums of the currently logged in user
export function get_albums(callOnBackendRes, callOnSuccess) {
    do_json_get_request(BACKEND_URL+"get_albums", callOnBackendRes, callOnSuccess);
}

// Deletes the passed album from the database
export function delete_album(albumId, callOnBackendRes, callOnSuccess) {
    do_json_post_request(BACKEND_URL+"delete_album", {albumId: albumId}, callOnBackendRes, callOnSuccess);
}

export function post_images() {
    // TO DO! FILE UPLOADING
}

// Gets all images from an album from the database, can optionally be filtered to only allow images with a given tag
export function get_images(albumId, tagId="", callOnBackendRes, callOnSuccess) {
    do_json_get_request(BACKEND_URL+"get_images?albumId="+albumId+"&tagId="+tagId, callOnBackendRes, callOnSuccess);
}

export function get_image_file() {
    // TO DO! FILE DOWNLOADING
}

// Deletes the passed images from the database
export function delete_images(imageNames, callOnBackendRes, callOnSuccess) {
    do_json_post_request(BACKEND_URL+"delete_images", {imageNames: imageNames}, callOnBackendRes, callOnSuccess);
}

// Creates a new tag in the database and appends it to the passed image
export function add_tag(imageName, tag, callOnBackendRes, callOnSuccess) {
    do_json_post_request(BACKEND_URL+"add_tag", {imageName: imageName, tag: tag}, callOnBackendRes, callOnSuccess);
}

// Connects a tag and an image in the database
export function add_existing_tag(imageName, tagId, callOnBackendRes, callOnSuccess) {
    do_json_post_request(BACKEND_URL+"add_existing_tag", {imageName: imageName, tagId: tagId}, callOnBackendRes, callOnSuccess);
}

// Gets all tags from the user currently logged in, but requires an imageName of one of his images 
export function get_tags(imageName, callOnBackendRes, callOnSuccess) {
    do_json_get_request(BACKEND_URL+"get_tags?imageName="+imageName, callOnBackendRes, callOnSuccess);
}

// Gets all tags an image is connected to
export function get_tags_of_image(imageName, callOnBackendRes, callOnSuccess) {
    do_json_get_request(BACKEND_URL+"get_tags_of_image?imageName="+imageName, callOnBackendRes, callOnSuccess);
}

// Gets all tags used in an album
export function get_tags_of_album(albumId, callOnBackendRes, callOnSuccess) {
    do_json_get_request(BACKEND_URL+"get_tags_of_album?albumId="+albumId, callOnBackendRes, callOnSuccess);
}

// Deletes a tag from the database
export function delete_tag(tagId, callOnBackendRes, callOnSuccess) {
    do_json_post_request(BACKEND_URL+"delete_tag", {tagId: tagId}, callOnBackendRes, callOnSuccess);
}

// Delete the connection between a tag and image in the database
// If this is the last image this tag is connected to, remove the whole tag from the db instead
export function delete_tag_from_image(tagId, imageId, callOnBackendRes, callOnSuccess) {
    do_json_post_request(BACKEND_URL+"delete_tag_from_image", {tagId: tagId, imageId: imageId}, callOnBackendRes, callOnSuccess);
}

// Directly adds a friendship beweteen the currently logged in user and friendName (email)
export function add_friend(friendName, callOnBackendRes, callOnSuccess) {
    do_json_post_request(BACKEND_URL+"add_friend", {friendName: friendName}, callOnBackendRes, callOnSuccess);
}

// Gets all friends from the currently logged in user
export function get_friends(callOnBackendRes, callOnSuccess) {
    do_json_get_request(BACKEND_URL+"get_friends", callOnBackendRes, callOnSuccess);
}

// Removes the friendship between the currently logged in user and the user with friendId from database
export function remove_friend(friendId, callOnBackendRes, callOnSuccess) {
    do_json_post_request(BACKEND_URL+"remove_friend", {friendId: friendId}, callOnBackendRes, callOnSuccess);
}

// Adds a friendrequest in the database between the currently logged in user and the user with friendName
export function add_friend_request(friendName, callOnBackendRes, callOnSuccess) {
    do_json_post_request(BACKEND_URL+"add_friend_request", {friendName: friendName}, callOnBackendRes, callOnSuccess);
}

// Gets all friendrequests sent to and by the currently logged in user
export function get_friend_requests(callOnBackendRes, callOnSuccess) {
    do_json_get_request(BACKEND_URL+"get_friend_requests", callOnBackendRes, callOnSuccess);
}

// Deletes a friendrequest sent to the user from the database
export function delete_request_to_user(fromUserId, callOnBackendRes, callOnSuccess) {
    do_json_post_request(BACKEND_URL+"delete_request_to_user", {fromUserId: fromUserId}, callOnBackendRes, callOnSuccess); 
}

// Deletes a friendship sent by the user from the database
export function delete_request_by_user(toUserId, callOnBackendRes, callOnSuccess) {
    do_json_post_request(BACKEND_URL+"delete_request_by_user", {toUserId: toUserId}, callOnBackendRes, callOnSuccess);
}

// Accept a friendrequest sent by fromUserId to the currently logged in user 
export function accept_request(fromUserId, callOnBackendRes, callOnSuccess) {
    do_json_post_request(BACKEND_URL+"accept_request", {fromUserId: fromUserId}, callOnBackendRes, callOnSuccess);
}