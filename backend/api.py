from flask import Flask, request, jsonify, session, send_file
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os

import sqlite3

app = Flask(__name__)
app.secret_key = "\xe1\t\x16\x7fO\x07}\x84\xcf\x8a\xb2Q&\xd8\xb6\x06\x16\xee\x0c0\xcap4\x04\x84\x8f\x18\xfc\xe7\xf4\r6M\xe6\xc8]d{\xad\xb1r$"
CORS(app, supports_credentials=True)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE_NAME = os.path.join(BASE_DIR, "app.db")
DB_NAME = "app"

UPLOADED_IMAGES_FOLDER = os.path.join(BASE_DIR, "uploaded_images")
os.makedirs(UPLOADED_IMAGES_FOLDER, exist_ok=True)


# --- helper functions ---
def get_conn_and_cursor():
    """
    Returns conn and cursor set up in a way, where rows after fetch are in dictionary format
    and sqlite3 uses foreign keys with cascade correctly.
    """

    conn = sqlite3.connect(DB_FILE_NAME)        # Connects
    conn.row_factory = sqlite3.Row              # Rows in dictionary format
    cursor = conn.cursor()                      # Creates cursor
    cursor.execute("PRAGMA foreign_keys = ON;") # Uses foreign keys so that they respond to cascade

    return conn, cursor

def get_user_id_by_email(email):
    """
    Returns the user id to given user email. 
    If no user with this email was found, the function returns None. 
    """
    conn, cursor = get_conn_and_cursor()
    cursor.execute("""
    SELECT id
    FROM users
    WHERE email = ?
    """, (email,))
    row = cursor.fetchone()
    conn.close()
    return row["id"] if row else None

def is_user_logged_in():
    """
    Checks, by using the session, if the user is logged in.
    Returns True if he is and False if he is not.
    """
    return session.get("isLoggedIn") == True

def check_if_friendship_exists(user_id, friend_id):
    if user_id < friend_id:
        user_id_1 = user_id
        user_id_2 = friend_id
    else:
        user_id_1 = friend_id
        user_id_2 = user_id

    conn, cursor = get_conn_and_cursor()
    cursor.execute("""
    SELECT *
    FROM friendships
    WHERE user_id_1 = ? AND user_id_2 = ?
    """, (user_id_1, user_id_2))
    row = cursor.fetchone()
    conn.close()
    
    if row: return True
    return False



# +-------+
# | LOGIN |
# +-------+

@app.route("/login", methods=["POST"])
def login():
    # Store request data in usable vars 
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    # Check if user is already logged in
    if session.get("isLoggedIn"):
        return jsonify(ans=f"You are already logged in as {session.get("email")}"), 400

    # Check if both email and password are given
    if not email or not password:
        return jsonify(ans="Please enter both, email and password"), 400
    
    # Connect database
    conn, cursor = get_conn_and_cursor()

    # Check database for passed email
    cursor.execute(f"SELECT * FROM users WHERE email = ?", (email,))
    row = cursor.fetchone()

    # Case no account with this email exists
    if not row:
        conn.close()
        return jsonify(ans=f"Wrong email or password"), 401
    
    # Check for valid password
    if check_password_hash(row["password"], password):      # Password is valid
        conn.close()
        session["email"] = email
        session["isLoggedIn"] = True
        return jsonify(ans="Login successful"), 201
    else:
        conn.close()
        return jsonify(ans="Wrong email or password"), 401  # Password is invalid



# +------------------+
# | GET_LOGIN_STATUS |
# +------------------+

@app.route("/get_login_status", methods=["GET"])
def get_login_status():
    return jsonify({
        "email": session.get("email"),
        "isLoggedIn": session.get("isLoggedIn"),
    })



# +--------+
# | LOGOUT |
# +--------+

@app.route("/logout", methods=["POST"])
def logout():
    is_logged_in = session.get("isLoggedIn")
    if is_logged_in:
        session.pop("email")
        session.pop("isLoggedIn")
        return jsonify(ans="Logged out"), 201
    else:
        return jsonify(ans="Nobody logged in to log out"), 400



# +--------------+
# | REGISTRATION |
# +--------------+

@app.route("/register", methods=["POST"])
def register():
    # Store request data in usable vars 
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    # Check first of both email and password are given
    if not email or not password:
        return jsonify(ans="Please enter both, email and password"), 400

    # Connect database
    conn, cursor = get_conn_and_cursor()

    # Check database for passed email
    cursor.execute(f"SELECT * FROM users WHERE email = ?", (email,))
    row = cursor.fetchone()

    # Case email is alredy in use
    if row and row["email"] == email:
        conn.close()
        return jsonify(ans=f"Email {email} already in use"), 409
    
    # Create account and store in database
    cursor.execute(f"INSERT INTO users (email, password) VALUES (?, ?)", 
                   (email, generate_password_hash(password)))
    
    conn.commit()
    conn.close()

    return jsonify(ans=f"Created account with email {email}"), 201



# +-----------+
# | ADD ALBUM |
# +-----------+

@app.route("/add_album", methods=["POST"])
def add_album():
    data = request.get_json()
    name = data.get("name")

    # Connect database
    conn, cursor = get_conn_and_cursor()

    # Get id of currently logged in user
    cursor.execute("SELECT id FROM users WHERE email = ?", (session.get("email"),))
    user_id = cursor.fetchone()["id"]

    # Create album
    cursor.execute("INSERT INTO albums (name) VALUES (?)", (name,))

    # Get id of created album
    album_id = cursor.lastrowid

    # Link user and his album together
    cursor.execute("INSERT INTO album_connectors (user_id, album_id) VALUES (?, ?)", (user_id, album_id))

    # Connect and close
    conn.commit()
    conn.close()

    return jsonify(ans=f"Created album {name}"), 201



# +------------+
# | GET ALBUMS |
# +------------+

@app.route("/get_albums", methods=["GET"])
def get_albums():
    # Return if no user is logged in
    if not session.get("isLoggedIn"):
        return jsonify(ans="You're not logged in"), 400

    # Connect database
    conn, cursor = get_conn_and_cursor()

    # Get all album names with users email  
    cursor.execute("""
    SELECT albums.name, albums.id
    FROM albums
    JOIN album_connectors ON album_connectors.album_id = albums.id
    JOIN users ON users.id = album_connectors.user_id
    WHERE users.email = ?
    ORDER BY albums.id DESC
    """, (session.get("email"),))

    albums_data = cursor.fetchall()
    conn.close()

    return jsonify([{"id": row["id"], "name": row["name"]} for row in albums_data])



# +--------------+
# | DELETE ALBUM |
# +--------------+

@app.route("/delete_album", methods=["POST"])
def delete_album():
    # Return if no user is logged in
    if not session.get("isLoggedIn"):
        return jsonify(ans="Unauthorized"), 401

    email = session.get("email")
    data = request.get_json()

    # Check for valid request
    try:
        album_id = int(data.get("albumId"))
    except ValueError:
        return jsonify(ans="Invalid albumId"), 400
    
    # Check if the user actually owns the passed album
    conn, cursor = get_conn_and_cursor()
    cursor.execute("""
    SELECT albums.id
    FROM albums
    JOIN album_connectors ON albums.id = album_connectors.album_id
    JOIN users ON album_connectors.user_id = users.id
    WHERE users.email = ? AND albums.id = ?
    """, (email, album_id))
    row = cursor.fetchone()

    # Return if no album to that id in relation to logged in user was found
    # --> user does not own this album (somebody trying hacky stuff)
    if not row:
        conn.close()
        return jsonify(ans="Unauthorized"), 401

    # Get all images from album
    cursor.execute("""
    SELECT images.id, images.extension
    FROM images
    JOIN image_connectors ON images.id = image_connectors.image_id
    JOIN albums ON image_connectors.album_id = albums.id
    WHERE albums.id = ?
    """,(album_id,))
    rows = cursor.fetchall()

    # Only remove images from album if the album is not empty
    if rows:
        # Get ids and filenames of all album images
        image_ids = [int(r["id"]) for r in rows]
        image_filenames = [f"{r["id"]}.{r["extension"]}" for r in rows]    

        # Deleting album images from database
        placeholders = ",".join("?"*len(image_ids))
        cursor.execute(f"""
        DELETE FROM images
        WHERE id IN ({placeholders})
        """, image_ids)

        # Remove images of album from drive
        for i in image_filenames:
            filepath = os.path.join(UPLOADED_IMAGES_FOLDER, i)
            if not os.path.exists(filepath):
                print(f"Could not find {filepath} in order to delete")
                continue
            os.remove(filepath)
            print(f"Deleted {filepath} from drive")

    # Remove album from database
    cursor.execute("""
    DELETE FROM albums
    WHERE id = ?
    """, (album_id,))

    conn.commit()
    conn.close()

    return jsonify(ans=f"Deleted album {album_id}"), 201



# +-------------+
# | POST IMAGES |
# +-------------+

@app.route("/post_images", methods=["POST"])
def post_images():
    # Check if user is logged in
    if not session.get("isLoggedIn"):
        return jsonify(ans="Unauthorized"), 401

    # Check if images are included in the request
    if "images" not in request.files:
        return jsonify(ans="No images are included in the post request"), 400
    
    # Get files from request
    images = request.files.getlist("images")
    saved_files = []

    # Get album id from request
    album_id = request.form.get("albumId")
    if not album_id:
        return jsonify(ans="album_id missing"), 400

    # Setup database
    conn, cursor = get_conn_and_cursor()

    # Ensure save filepath and store on server
    for image in images:
        # Skip empty filenames
        if image.filename == "":
            continue

        # Get secure filename
        secure_image_filename = secure_filename(image.filename)

        # Get image file's extension
        _, ext = os.path.splitext(secure_image_filename)
        ext = ext.lower().lstrip(".")

        # Insert new image in database
        cursor.execute("""
        INSERT INTO images (extension)
        VALUES (?)
        """, (ext,))

        # Get id of just inserted image
        image_id = cursor.lastrowid

        # Create link between album and image
        cursor.execute("""
        INSERT INTO image_connectors (album_id, image_id)
        VALUES (?, ?)
        """, (album_id, image_id))

        # Actually store image on server in directory
        image_filepath = os.path.join(UPLOADED_IMAGES_FOLDER, f"{image_id}.{ext}")
        image.save(image_filepath)
        saved_files.append(f"{image_id}.{ext}")

    # Commit changes and close database connection
    conn.commit()
    conn.close()

    return jsonify({"ans": saved_files}), 200



# +------------+
# | GET IMAGES |
# +------------+

@app.route("/get_images", methods=["GET"])
def get_images():
    # Check if user is logged in
    if not session.get("isLoggedIn"):
        return jsonify(ans="Unauthorized"), 401

    try:
        album_id = int(request.args.get("albumId"))
        tag_id = request.args.get("tagId")
        if tag_id != "": tag_id = int(tag_id)
        else: tag_id = None
    except ValueError: 
        return jsonify(ans="Bad request"), 400

    conn, cursor = get_conn_and_cursor()

    if (tag_id):
        cursor.execute("""
        SELECT images.id, images.extension
        FROM images
        JOIN image_connectors ON image_connectors.image_id = images.id
        JOIN albums ON albums.id = image_connectors.album_id
        JOIN album_connectors ON album_connectors.album_id = albums.id
        JOIN users ON users.id = album_connectors.user_id
        JOIN tag_connectors ON tag_connectors.image_id = images.id
        JOIN tags ON tag_connectors.tag_id = tags.id
        WHERE users.email = ? AND albums.id = ? AND tags.id = ?
        ORDER BY images.id DESC 
        """, (session.get("email"), album_id, tag_id))
    else:
        cursor.execute("""
        SELECT images.id, images.extension
        FROM images
        JOIN image_connectors ON image_connectors.image_id = images.id
        JOIN albums ON albums.id = image_connectors.album_id
        JOIN album_connectors ON album_connectors.album_id = albums.id
        JOIN users ON users.id = album_connectors.user_id
        WHERE users.email = ? AND albums.id = ?
        ORDER BY images.id DESC
        """, (session.get("email"),album_id))

    # Get filenames of album images
    image_filenames = [f"{row["id"]}.{row["extension"]}" for row in cursor.fetchall()]

    # Close connection
    conn.close()

    # Return image filenames
    return jsonify(image_filenames)



# +----------------+
# | GET IMAGE FILE |
# +----------------+

@app.route("/get_image_file/<string:image_file_name>", methods=["GET"])
def get_image_file(image_file_name):
    # Check if user is logged in
    if not session.get("isLoggedIn"):
        return jsonify(ans="Unauthorized"), 401
    
    # Get id and extension
    id, ext = os.path.splitext(image_file_name)
    id = int(id)
    ext = ext.lower().lstrip(".")

    # Check if the user owns this image (security check)
    conn, cursor = get_conn_and_cursor()
    cursor.execute("""
    SELECT images.id, images.extension
    FROM images
    JOIN image_connectors ON images.id = image_connectors.image_id
    JOIN albums ON image_connectors.album_id = albums.id
    JOIN album_connectors ON albums.id = album_connectors.album_id
    JOIN users ON album_connectors.user_id = users.id
    WHERE users.email = ? AND images.id = ? AND images.extension = ?
    """, (session.get("email"), id, ext))

    row = cursor.fetchone()
    conn.close()

    # If the user is related to this image row should not be empty
    if not row:
        return jsonify(ans="Unauthorized"), 401
    
    # Build filepath
    filepath = os.path.join(UPLOADED_IMAGES_FOLDER, image_file_name)

    # Check if file exists on server
    if not os.path.exists(filepath):
        return jsonify(ans="File missing on server"), 404
    
    # Actually sending file
    return send_file(filepath)



# +---------------+
# | DELETE IMAGES |
# +---------------+

@app.route("/delete_images", methods=["POST"])
def delete_images():
    # Check if user is logged in
    if not session.get("isLoggedIn"):
        return jsonify(ans="Unauthorized"), 401
    
    # Get image file names
    data = request.get_json()
    image_names = data.get("imageNames")

    ids = []
    # Loop through all images and get the id of each one
    for i in image_names:
        # Get database id and image's extension
        id, _ = os.path.splitext(i)
        try:
            id = int(id)
        except ValueError:
            return jsonify(ans="Invalid imageId"), 400
        ids.append(id)

    # Get all images the user owns
    conn, cursor = get_conn_and_cursor()
    cursor.execute("""
    SELECT images.id
    FROM images
    JOIN image_connectors ON images.id = image_connectors.image_id
    JOIN albums ON image_connectors.album_id = albums.id
    JOIN album_connectors ON albums.id = album_connectors.album_id
    JOIN users ON album_connectors.user_id = users.id
    WHERE users.email = ?
    """, (session.get("email"),))

    # Fetch all ids and store them
    rows = cursor.fetchall()
    conn.close()

    # Prevents unauthorized access if no images to that user were found
    if not rows:
        return jsonify(ans="Unauthorized"), 401 
    
    # Checking if the ids the user requests to delete are actually his images
    users_image_ids = [int(i["id"]) for i in rows]
    for i in ids:
        # Return immediately if there is an id in users request, that does not belong to his images
        if not i in users_image_ids:
            return jsonify(ans="Unauthorized"), 401 

    # Actually deleting images from drive
    for i in image_names:
        filepath = os.path.join(UPLOADED_IMAGES_FOLDER, i)
        if not os.path.exists(filepath):
            return jsonify(ans="File missing on server"), 404
        os.remove(filepath)

    # Deleting from database
    placeholders = ",".join(["?"] * len(ids))
    conn, cursor = get_conn_and_cursor()
    cursor.execute(f"""
    DELETE FROM images 
    WHERE id IN ({placeholders})
    """, (ids))

    # Commit the deletion and close database
    conn.commit()
    conn.close()

    print(f"""
--- deletion summary ---
amount deleted: {len(ids)}
ids deleted: {ids}
images deleted: {image_names}
---- end of summary ----
""")

    return jsonify(ans=f"{len(ids)} image(s) deleted"), 200



# +---------+
# | ADD TAG |
# +---------+

@app.route("/add_tag", methods=["POST"])
def add_tag():
    # Check if user is logged in
    if not session.get("isLoggedIn"):
        return jsonify(ans="Unauthorized"), 401
    
    data = request.get_json()

    # Check for bad request
    if not data.get("imageName") or not data.get("tag"):
        return jsonify(ans="Bad request"), 400

    image_name = data.get("imageName")
    tag = data.get("tag")

    # Extract id from image_name
    id, _ = os.path.splitext(image_name)
    try:
        id = int(id)
    except ValueError:
        return jsonify(ans="Invalid imageId"), 400
    
    # Check in database if the requested image is his
    conn, cursor = get_conn_and_cursor()
    cursor.execute("""
    SELECT images.id
    FROM images
    JOIN image_connectors ON images.id = image_connectors.image_id
    JOIN albums ON image_connectors.album_id = albums.id
    JOIN album_connectors ON albums.id = album_connectors.album_id
    JOIN users ON album_connectors.user_id = users.id
    WHERE images.id = ? AND users.email = ?
    """, (id, session.get("email")))

    row = cursor.fetchone()

    # Return if user does not own this image
    if not row:
        conn.close()
        return jsonify(ans="Unauthorized"), 401
    
    # Actually create tag in database
    cursor.execute("""
    INSERT INTO tags (name)
    VALUES (?)
    """, (tag,))
    tag_id = cursor.lastrowid

    cursor.execute("""
    INSERT INTO tag_connectors (image_id, tag_id)
    VALUES (?, ?)
    """, (id, tag_id))

    # EXTRA - Run through database and remove all tags that are not connected to any image
    # This can happen if an image with tags on it or an album which contained images was deleted.
    # This solution is a bit crappy but gets the job done. It prevents memory overflow by unused tags
    cursor.execute("""
    DELETE FROM tags
    WHERE tags.id NOT IN (SELECT tag_id FROM tag_connectors)
    """)
    print("[ NOTE ] Deleted unused tags")

    conn.commit()
    conn.close()

    return jsonify(ans=f"Created tag {tag} for image {image_name}"), 201     



# +------------------+
# | ADD EXISTING TAG |
# +------------------+

@app.route("/add_existing_tag", methods=["POST"])
def add_existing_tag():
    # Check if user is logged in
    if not session.get("isLoggedIn"):
        return jsonify(ans="Unauthorized"), 401
    
    data = request.get_json()

    # Check for bad request
    if not data.get("imageName") or not data.get("tagId"):
        return jsonify(ans="Bad request"), 400

    image_name = data.get("imageName")
    tag_id = data.get("tagId")

    # Extract id from image_name
    image_id, _ = os.path.splitext(image_name)
    try:
        image_id = int(image_id)
        tag_id = int(tag_id)
    except ValueError:
        return jsonify(ans="Bad request"), 400
    
    # Check in database if the requested image is his
    conn, cursor = get_conn_and_cursor()
    cursor.execute("""
    SELECT images.id
    FROM images
    JOIN image_connectors ON images.id = image_connectors.image_id
    JOIN albums ON image_connectors.album_id = albums.id
    JOIN album_connectors ON albums.id = album_connectors.album_id
    JOIN users ON album_connectors.user_id = users.id
    WHERE images.id = ? AND users.email = ?
    """, (image_id, session.get("email")))
    row = cursor.fetchone()

    # Return if user does not own this image
    if not row:
        conn.close()
        return jsonify(ans="Unauthorized"), 401
    

    # Check if the tag is already connected to the image
    cursor.execute("""
    SELECT * 
    FROM tag_connectors
    WHERE image_id = ? AND tag_id = ?
    """, (image_id, tag_id))
    row = cursor.fetchone()
    if row:
        conn.close()
        return jsonify(ans="Conflict"), 409
    
    # Actually connect image and tag
    cursor.execute("""
    INSERT INTO tag_connectors (image_id, tag_id)
    VALUES (?, ?)
    """, (image_id, tag_id))
    conn.commit()
    conn.close()

    return jsonify(ans=f"Added tag {tag_id} to image {image_id}"), 201


# +----------+
# | GET TAGS |
# +----------+

@app.route("/get_tags", methods=["GET"])
def get_tags():
    # Check if user is logged in
    if not session.get("isLoggedIn"):
        return jsonify(ans="Unauthorized"), 401
    
    image_name = request.args.get("imageName")
    
    # Check for bad request
    if not image_name:
        return jsonify(ans="Bad request"), 400


    # Extract id from image_name
    image_id, _ = os.path.splitext(image_name)
    try:
        image_id = int(image_id)
    except ValueError:
        return jsonify(ans="Invalid imageId"), 400
    
    # Check if the passed id is actually an image of the user
    conn, cursor = get_conn_and_cursor()
    cursor.execute("""
    SELECT images.id
    FROM images
    JOIN image_connectors ON images.id = image_connectors.image_id
    JOIN albums ON image_connectors.album_id = albums.id
    JOIN album_connectors ON albums.id = album_connectors.album_id
    JOIN users ON album_connectors.user_id = users.id
    WHERE images.id = ? AND users.email = ?
    """, (image_id, session.get("email")))
    row = cursor.fetchone()

    # Return if the requested image is not the users
    if not row:
        conn.close()
        return jsonify(ans="Unauthorized"), 401

    # Actually get all tags from a user
    cursor.execute("""
    SELECT DISTINCT tags.id, tags.name
    FROM tags
    JOIN tag_connectors ON tags.id = tag_connectors.tag_id
    JOIN images ON images.id = tag_connectors.image_id
    JOIN image_connectors ON images.id = image_connectors.image_id
    JOIN albums ON image_connectors.album_id = albums.id
    JOIN album_connectors ON albums.id = album_connectors.album_id
    JOIN users ON album_connectors.user_id = users.id
    WHERE users.email = ?
    ORDER BY tags.name
    """, (session.get("email"),))

    tags = [{"id": t["id"], "name": t["name"]} for t in cursor.fetchall()]
    conn.close()

    return jsonify(tags), 201



# +-------------------+
# | GET TAGS OF IMAGE |
# +-------------------+

@app.route("/get_tags_of_image", methods=["GET"])
def get_tags_of_image():
    # Check if user is logged in
    if not session.get("isLoggedIn"):
        return jsonify(ans="Unauthorized"), 401
    
    image_name = request.args.get("imageName")
    
    # Check for bad request
    if not image_name:
        return jsonify(ans="Bad request"), 400

    # Extract id from image_name
    image_id, _ = os.path.splitext(image_name)
    try:
        image_id = int(image_id)
    except ValueError:
        return jsonify(ans="Invalid imageId"), 400

    # Check if the passed id is actually an image of the user
    conn, cursor = get_conn_and_cursor()
    cursor.execute("""
    SELECT images.id
    FROM images
    JOIN image_connectors ON images.id = image_connectors.image_id
    JOIN albums ON image_connectors.album_id = albums.id
    JOIN album_connectors ON albums.id = album_connectors.album_id
    JOIN users ON album_connectors.user_id = users.id
    WHERE images.id = ? AND users.email = ?
    """, (image_id, session.get("email")))
    row = cursor.fetchone()

    # Return if the requested image is not the users
    if not row:
        conn.close()
        return jsonify(ans="Unauthorized"), 401
    
    # Actually get all tags from that image
    cursor.execute("""
    SELECT tags.id, tags.name
    FROM tags
    JOIN tag_connectors ON tags.id = tag_connectors.tag_id
    JOIN images ON tag_connectors.image_id = images.id
    WHERE images.id = ?
    ORDER BY tags.name
    """, (image_id,))
    
    tags = [{"id": t["id"], "name": t["name"]} for t in cursor.fetchall()]
    conn.close()

    return jsonify(tags), 201



# +-------------------+
# | GET TAGS OF ALBUM |
# +-------------------+

@app.route("/get_tags_of_album", methods=["GET"])
def get_tags_of_album():
    # Check if user is logged in
    if not session.get("isLoggedIn"):
        return jsonify(ans="Unauthorized"), 401    
    email = session.get("email")

    # Check for bad request
    album_id = request.args.get("albumId")
    if not album_id:
        return jsonify(ans="Bad request"), 400   
    try:
        album_id = int(album_id)
    except ValueError:
        return jsonify(ans="Bad request"), 400 
    
    # Check if the album actually is owned by the user
    conn, cursor = get_conn_and_cursor()
    cursor.execute("""
    SELECT albums.id
    FROM albums
    JOIN album_connectors ON albums.id = album_connectors.album_id
    JOIN users ON album_connectors.user_id = users.id
    WHERE users.email = ? AND albums.id = ?
    """,(email, album_id))
    row = cursor.fetchone()

    if not row:
        conn.close()
        return jsonify(ans="Unauthorized"), 401
    
    # Get all tags used by images in that album
    cursor.execute("""
    SELECT DISTINCT tags.id, tags.name
    FROM tags
    JOIN tag_connectors ON tags.id = tag_connectors.tag_id
    JOIN images ON tag_connectors.image_id = images.id
    JOIN image_connectors ON images.id = image_connectors.image_id
    JOIN albums ON image_connectors.album_id = albums.id
    WHERE albums.id = ?
    ORDER BY tags.name
    """, (album_id,))
    tags = [{"id": r["id"], "name": r["name"]} for r in cursor.fetchall()]
    conn.close()

    return jsonify(tags), 201


# +------------+
# | DELETE TAG |
# +------------+

@app.route("/delete_tag", methods=["POST"])
def delete_tag():
    # Check if user is logged in
    if not session.get("isLoggedIn"):
        return jsonify(ans="Unauthorized"), 401
    email = session.get("email")

    # Get and validate tag_id
    data = request.get_json()
    tag_id = data.get("tagId")
    if not tag_id:
        return jsonify(ans="Bad request"), 400
    
    # Check if the user owns that tag
    conn, cursor = get_conn_and_cursor()
    cursor.execute("""
    SELECT tags.id
    FROM tags
    JOIN tag_connectors ON tags.id = tag_connectors.tag_id
    JOIN images ON images.id = tag_connectors.image_id
    JOIN image_connectors ON images.id = image_connectors.image_id
    JOIN albums ON image_connectors.album_id = albums.id
    JOIN album_connectors ON albums.id = album_connectors.album_id
    JOIN users ON album_connectors.user_id = users.id
    WHERE users.email = ? AND tags.id = ?
    """, (email, tag_id))
    row = cursor.fetchone()

    # If not tag was found user is unauthorized
    if not row:
        conn.close()
        return jsonify(ans="Unauthorized"), 401

    # Delete tag from database, connector will be deleted automatically
    cursor.execute("""
    DELETE FROM tags
    WHERE id = ?    
    """, (tag_id,))

    conn.commit()
    conn.close()

    return jsonify(ans=f"Deleted tag {tag_id}")



# +-----------------------+
# | DELETE TAG FROM IMAGE |
# +-----------------------+

@app.route("/delete_tag_from_image", methods=["POST"])
def delete_tag_from_image():
    # Check if user is logged in
    if not session.get("isLoggedIn"):
        return jsonify(ans="Unauthorized"), 401
    email = session.get("email")

    # Get and validate tag_id
    data = request.get_json()
    tag_id = data.get("tagId")
    if not tag_id:
        return jsonify(ans="Bad request"), 400
    try:
        tag_id = int(tag_id)
    except ValueError:
        return jsonify(ans="Invalid tagId"), 400
    
    # Extract id from image_name
    image_name = data.get("imageName")
    image_id, _ = os.path.splitext(image_name)
    try:
        image_id = int(image_id)
    except ValueError:
        return jsonify(ans="Invalid imageId"), 400
    
    # Check if the user owns that tag and if the tag is actually connected to image
    conn, cursor = get_conn_and_cursor()
    cursor.execute("""
    SELECT tags.id
    FROM tags
    JOIN tag_connectors ON tags.id = tag_connectors.tag_id
    JOIN images ON images.id = tag_connectors.image_id
    JOIN image_connectors ON images.id = image_connectors.image_id
    JOIN albums ON image_connectors.album_id = albums.id
    JOIN album_connectors ON albums.id = album_connectors.album_id
    JOIN users ON album_connectors.user_id = users.id
    WHERE users.email = ? AND images.id = ? AND tags.id = ? 
    """, (email, image_id, tag_id))
    row = cursor.fetchone()

    # If no tag was found user is unauthorized
    if not row:
        conn.close()
        return jsonify(ans="Unauthorized"), 401
    
    # Check if tag is only connected to one image
    # If it is, this means this image is the last one the tag belongs to, so just remove the
    # whole tag instead of the connection.
    # If only the connection would be removed there would remain an unused tag.
    cursor.execute("""
    SELECT images.id
    FROM images
    JOIN tag_connectors ON images.id = tag_connectors.image_id
    JOIN tags ON tag_connectors.tag_id = tags.id
    WHERE tags.id = ?
    """, (tag_id,))
    rows = cursor.fetchall()

    # Delete complete tag
    if len(rows) == 1:
        cursor.execute("""
        DELETE FROM tags
        WHERE id = ?
        """, (tag_id,))
        conn.commit()
        conn.close()
        return jsonify(ans=f"Deleted tag {tag_id} since {image_id} was the last image it was connected to"), 201

    # Just delete connection between image and tag
    else:
        cursor.execute("""
        DELETE FROM tag_connectors
        WHERE image_id = ? AND tag_id = ?
        """, (image_id, tag_id))
        conn.commit()
        conn.close()
        return jsonify(ans=f"Deleted connection between tag {tag_id} and image {image_id}")



# +------------+
# | ADD FRIEND |
# +------------+

@app.route("/add_friend", methods=["POST"])
def add_friend():
    # Check if user is logged in
    if not session.get("isLoggedIn"):
        return jsonify(ans="Unauthorized"), 401
    
    # Check for bad request
    data = request.get_json()
    if not data.get("friendName"):
        return jsonify(ans="Bad request"), 400
    friend_name = data.get("friendName")

    # Check if the user wants to add himself
    if friend_name == session.get("email"):
        return jsonify(ans="Bad request"), 400

    # Check if the wanted friend is valid, if so get his id
    conn, cursor = get_conn_and_cursor()
    friend_id = get_user_id_by_email(friend_name)
    if not friend_id:
        return jsonify(ans=f"User {friend_name} not found"), 404

    # Get id of logged in user
    cursor.execute("""
    SELECT id
    FROM users
    WHERE email = ?
    """, (session.get("email"),))
    logged_in_user_id = cursor.fetchone()["id"] 

    # The smaller id is user_id_1 and the greater one is user_id_2
    user_id_1 = min(logged_in_user_id, friend_id)
    user_id_2 = max(logged_in_user_id, friend_id)

    # Before creating the friendship, check if the friendship already exists
    cursor.execute("""
    SELECT *
    FROM friendships
    WHERE user_id_1 = ? AND user_id_2 = ?
    """, (user_id_1, user_id_2))
    row = cursor.fetchone()
    if row:
        conn.close()
        return jsonify(ans=f"You are already friends with {friend_name}"), 409

    try:
        # Actually create the friendship
        cursor.execute("""
        INSERT INTO friendships (user_id_1, user_id_2)
        VALUES (?, ?)
        """, (user_id_1, user_id_2))
        conn.commit()
    except sqlite3.IntegrityError:
        # Catch error when creation goes wrong
        conn.rollback()
        return jsonify(ans="Friendship could not be created"), 500
    finally:
        conn.close()

    return jsonify(ans=f"{session.get("email")} ({logged_in_user_id}) and {friend_name} ({friend_id}) are now friends"), 200



# +-------------+
# | GET FRIENDS |
# +-------------+

@app.route("/get_friends", methods=["GET"])
def get_friends():
    # Check if user is authorized
    if not is_user_logged_in(): return jsonify(ans="Unauthorized"), 401

    # Get user's id
    user_id = get_user_id_by_email(session.get("email"))

    # Get all friend ids of user from database
    conn, cursor = get_conn_and_cursor()
    cursor.execute("""
    SELECT u.email AS friend_email, u.id AS friend_id
    FROM friendships AS f
    JOIN users u 
    ON u.id = CASE
                WHEN f.user_id_1 = ? THEN f.user_id_2
                ELSE f.user_id_1
              END
    WHERE f.user_id_1 = ? OR f.user_id_2 = ?
    """, (user_id, user_id, user_id))
    rows = cursor.fetchall()
    conn.close()

    # Return an empty list if user has no friends
    if not rows: return jsonify([]), 200

    # Get each friends id and email and store nicely in list of objects
    friends = [{"id": r["friend_id"], "email": r["friend_email"]} for r in rows]

    return jsonify(friends), 200



# +---------------+
# | REMOVE FRIEND |
# +---------------+

@app.route("/remove_friend", methods=["POST"])
def remove_friend():
    # Check if user is authorized
    if not is_user_logged_in(): return jsonify(ans="Unauthorized"), 401

    # Check for bad request
    data = request.get_json()
    friend_id = data.get("friendId")

    if not friend_id: return jsonify(ans="Bad request"), 400
    try: friend_id = int(friend_id)
    except ValueError: return jsonify(ans="Bad request"), 400

    # Get user id
    user_id = get_user_id_by_email(session.get("email"))

    # Check if friendship requested to delete actually exists
    if not check_if_friendship_exists(user_id, friend_id):
        return jsonify("Friendship does not exist"), 404
    
    # Actually remove the friendship
    user_id_1 = min(user_id, friend_id)
    user_id_2 = max(user_id, friend_id)

    conn, cursor = get_conn_and_cursor()
    cursor.execute("""
    DELETE FROM friendships
    WHERE user_id_1 = ? AND user_id_2 = ?
    """, (user_id_1, user_id_2))
    conn.commit()
    conn.close()

    return jsonify(ans=f"Removed friendship between {user_id_1} and {user_id_2}")



# +--------------------+
# | ADD FRIEND REQUEST |
# +--------------------+

@app.route("/add_friend_request", methods=["POST"])
def add_friend_request():
    # Check if user is authorized
    if not is_user_logged_in(): return jsonify(ans="Unauthorized"), 401

    # Check for bad request
    data = request.get_json()
    if not data.get("friendName"):
        return jsonify(ans="Bad request"), 400
    friend_name = data.get("friendName")

    # Check if the user wants to add himself
    if friend_name == session.get("email"):
        return jsonify(ans="Bad request"), 400

    # Get id of the requested user
    to_user_id = get_user_id_by_email(friend_name)
    if not to_user_id:
        return jsonify(ans=f"User {friend_name} not found"), 404

    # Get id of the logged in user
    from_user_id = get_user_id_by_email(session.get("email"))

    # Check if the friend request already exists
    conn, cursor = get_conn_and_cursor()
    cursor.execute("""
    SELECT *
    FROM friend_requests
    WHERE from_user_id = ? AND to_user_id = ?
    """, (from_user_id, to_user_id))
    row = cursor.fetchone()
    
    if row: 
        conn.close()
        return jsonify(ans="Request already sent"), 409

    # Check if the friendship itself already exists
    if from_user_id < to_user_id:
        user_id_1 = from_user_id
        user_id_2 = to_user_id
    else:
        user_id_1 = to_user_id
        user_id_2 = from_user_id
    
    cursor.execute("""
    SELECT *
    FROM friendships
    WHERE user_id_1 = ? AND user_id_2 = ?
    """, (user_id_1, user_id_2))
    row = cursor.fetchone()
    if row:
        conn.close()
        return jsonify(ans="You're already friends with the requested user"), 409

    # Actually create the request in the database
    try:
        cursor.execute("""
        INSERT INTO friend_requests (from_user_id, to_user_id)
        VALUES (?, ?)
        """, (from_user_id, to_user_id))
        conn.commit()
    except sqlite3.IntegrityError:
        conn.rollback()
        return jsonify(ans="Error while creating friend request"), 500
    finally:
        conn.close()

    return jsonify(ans=f"Created friendrequest from {session.get("email")} ({from_user_id}) to {friend_name} ({to_user_id})"), 200



# +---------------------+
# | GET FRIEND REQUESTS |
# +---------------------+

@app.route("/get_friend_requests", methods=["GET"])
def get_friend_requests():
    # Check if user is authorized
    if not is_user_logged_in(): return jsonify(ans="Unauthorized"), 401

    # Get id of the logged in user
    user_id = get_user_id_by_email(session.get("email"))

    # Get all requests sent to and by the user
    friend_requests = {"toUser": [], "byUser": []}
    conn, cursor = get_conn_and_cursor()

    # Get all requests sent to the user
    cursor.execute("""
    SELECT friend_requests.from_user_id, users.email
    FROM friend_requests
    JOIN users ON friend_requests.from_user_id = users.id
    WHERE to_user_id = ?
    """, (user_id,))
    rows = cursor.fetchall()

    if rows:
        friend_requests["toUser"] = [{"id": r["from_user_id"], "email": r["email"]} for r in rows]

    # Get all requests sent by the user
    cursor.execute("""
    SELECT friend_requests.to_user_id, users.email
    FROM friend_requests
    JOIN users ON friend_requests.to_user_id = users.id
    WHERE friend_requests.from_user_id = ?
    """, (user_id,))
    rows = cursor.fetchall()

    if rows:
        friend_requests["byUser"] = [{"id": r["to_user_id"], "email": r["email"]} for r in rows]

    conn.close()
    return jsonify(friend_requests), 200



# +------------------------+
# | DELETE REQUEST TO USER |
# +------------------------+

@app.route("/delete_request_to_user", methods=["POST"])
def delete_request_to_user():
    # Check if user is authorized
    if not is_user_logged_in(): return jsonify(ans="Unauthorized"), 401

    # Get the id of the user who sent the request from post request
    data = request.get_json()
    from_user_id = data.get("fromUserId")

    # Check for bad request
    if not from_user_id: return jsonify(ans="Bad request"), 400
    try: from_user_id = int(from_user_id)
    except ValueError: return jsonify(ans="Bad request"), 400

    # Get the id of the logged in user
    to_user_id = get_user_id_by_email(session.get("email"))

    # Actually try to delete the request from the database
    conn, cursor = get_conn_and_cursor()
    try:
        cursor.execute("""
        DELETE FROM friend_requests
        WHERE from_user_id = ? AND to_user_id = ?
        """, (from_user_id, to_user_id))
        conn.commit()
    except sqlite3.IntegrityError: 
        conn.rollback()
        return jsonify(ans="Error while trying to delete the friendrequest"), 500
    finally:
        conn.close()

    return jsonify(ans=f"Deleted request from {from_user_id} to {to_user_id}"), 200



# +------------------------+
# | DELETE REQUEST BY USER |
# +------------------------+

@app.route("/delete_request_by_user", methods=["POST"])
def delete_request_by_user():
    # Check if user is authorized
    if not is_user_logged_in(): return jsonify(ans="Unauthorized"), 401

    # Get the id of the user who received the friend request
    data = request.get_json()
    to_user_id = data.get("toUserId")

    # Check for bad request
    if not to_user_id: return jsonify(ans="Bad request"), 400
    try: to_user_id = int(to_user_id)
    except ValueError: return jsonify(ans="Bad request"), 400

    # Get the id of the logged in user
    from_user_id = get_user_id_by_email(session.get("email"))

    # Actually try to delete the request from the database
    conn, cursor = get_conn_and_cursor()
    try:
        cursor.execute("""
        DELETE FROM friend_requests
        WHERE from_user_id = ? AND to_user_id = ?
        """, (from_user_id, to_user_id))
        conn.commit()
    except sqlite3.IntegrityError: 
        conn.rollback()
        return jsonify(ans="Error while trying to delete the friendrequest"), 500
    finally:
        conn.close()

    return jsonify(ans=f"Deleted request from {from_user_id} to {to_user_id}"), 200    



# +----------------+
# | ACCEPT REQUEST |
# +----------------+

@app.route("/accept_request", methods=["POST"])
def accept_request():
    # Check if user is authorized
    if not is_user_logged_in(): return jsonify(ans="Unauthorized"), 401

    # Get the id of the user who sent the request from post request
    data = request.get_json()
    from_user_id = data.get("fromUserId")

    # Check for bad request
    if not from_user_id: return jsonify(ans="Bad request"), 400
    try: from_user_id = int(from_user_id)
    except ValueError: return jsonify(ans="Bad request"), 400

    # Get the id of the logged in user
    to_user_id = get_user_id_by_email(session.get("email"))

    # Check if the friendship the user wants to accept already exists
    user_id_1 = min(from_user_id, to_user_id)
    user_id_2 = max(from_user_id, to_user_id)
    
    conn, cursor = get_conn_and_cursor()
    cursor.execute("""
    SELECT *
    FROM friendships
    WHERE user_id_1 = ? AND user_id_2 = ?
    """, (user_id_1, user_id_2))
    row = cursor.fetchone()

    if row:
        conn.close()
        return jsonify(ans="You're already friends with the user you want to receive the friendrequest from"), 409

    # Try to remove the friend request from database and create the friendship
    try:
        cursor.execute("""
        DELETE FROM friend_requests
        WHERE from_user_id = ? AND to_user_id = ?
        """, (from_user_id, to_user_id))

        cursor.execute("""
        INSERT INTO friendships (user_id_1, user_id_2)
        VALUES (?, ?)
        """, (user_id_1, user_id_2))
        conn.commit()
    except sqlite3.IntegrityError:
        conn.rollback()
        return jsonify(ans="Error while trying to establish the friendship"), 500
    finally:
        conn.close()

    return jsonify(ans=f"Accepted request by {from_user_id} and created friendship between {user_id_1} and {user_id_2}"), 200

if __name__ == "__main__":
    app.run(debug=True)