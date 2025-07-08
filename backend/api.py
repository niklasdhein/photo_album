from flask import Flask, request, jsonify, session, send_file
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os

import sqlite3

app = Flask(__name__)
app.secret_key = "\xe1\t\x16\x7fO\x07}\x84\xcf\x8a\xb2Q&\xd8\xb6\x06\x16\xee\x0c0\xcap4\x04\x84\x8f\x18\xfc\xe7\xf4\r6M\xe6\xc8]d{\xad\xb1r$"
CORS(app, supports_credentials=True)

DB_FILE_NAME = "app.db"
DB_NAME = "app"

UPLOADED_IMAGES_FOLDER = "./uploaded_images"


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

    amount = int(request.args.get("amount"))

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

    albums_data = cursor.fetchmany(amount)
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

    # Get album id from post request
    album_id = int(request.args.get("albumId"))

    # Get all images of an album
    conn, cursor = get_conn_and_cursor()
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
    return jsonify(ans=image_filenames)



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

if __name__ == "__main__":
    app.run(debug=True)