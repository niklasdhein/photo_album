import sqlite3

conn = sqlite3.connect("app.db")
cursor = conn.cursor()


# --- users ---
# 2:n relation to friendships
# 1:n relation to album_connectors
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL
);
""")

# --- friendships ---
# n:2 relation to users
cursor.execute("""
CREATE TABLE IF NOT EXISTS friendships (
    user_id_1 INTEGER NOT NULL,
    user_id_2 INTEGER NOT NULL,
    PRIMARY KEY (user_id_1, user_id_2),
    FOREIGN KEY (user_id_1) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id_2) REFERENCES users(id) ON DELETE CASCADE
);
""")

# --- friend_requests ---
# n:2 relation to users
cursor.execute("""
CREATE TABLE IF NOT EXISTS friend_requests (
    from_user_id INTEGER NOT NULL,
    to_user_id INTEGER NOT NULL,
    PRIMARY KEY (from_user_id, to_user_id),
    FOREIGN KEY (from_user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (to_user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE(from_user_id, to_user_id)
);
""")

# --- albums ---
# 1:n relation to album_connectors
# 1:n relation to image_connectors
cursor.execute("""
CREATE TABLE IF NOT EXISTS albums (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL
);
""")

# --- album_connectors ---
# n:1 relation to users
# n:1 relation to albums
cursor.execute("""
CREATE TABLE IF NOT EXISTS album_connectors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    album_id INTEGER NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (album_id) REFERENCES albums(id) ON DELETE CASCADE,
    UNIQUE(user_id, album_id)
);
""")

# --- images ---
# 1:n relation to image_connectors
cursor.execute("""
CREATE TABLE IF NOT EXISTS images (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    extension TEXT NOT NULL,
    upload_date DATETIME DEFAULT CURRENT_TIMESTAMP
);
""")

# --- image_connectors ---
# n:1 relation to albums 
# n:1 relation to images
cursor.execute("""
CREATE TABLE IF NOT EXISTS image_connectors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    album_id INTEGER NOT NULL,
    image_id INTEGER NOT NULL,
    FOREIGN KEY (album_id) REFERENCES albums(id) ON DELETE CASCADE,
    FOREIGN KEY (image_id) REFERENCES images(id) ON DELETE CASCADE,
    UNIQUE(album_id, image_id)          
);
""")

# --- tags ---
# n:1 relation to tag_connectors
cursor.execute("""
CREATE TABLE IF NOT EXISTS tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL    
);
""")

# --- tag_connectors ---
# n:1 relation to tags
# n:1 relation to images
cursor.execute("""
CREATE TABLE IF NOT EXISTS tag_connectors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tag_id INTEGER NOT NULL,
    image_id INTEGER NOT NULL,
    FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE,
    FOREIGN KEY (image_id) REFERENCES images(id) ON DELETE CASCADE,
    UNIQUE(tag_id, image_id)                
);
""")

# --- indices  ---
cursor.execute("CREATE INDEX IF NOT EXISTS idx_album_connectors_user_id ON album_connectors(user_id);")
cursor.execute("CREATE INDEX IF NOT EXISTS idx_album_connectors_album_id ON album_connectors(album_id);")

cursor.execute("CREATE INDEX IF NOT EXISTS idx_image_connectors_album_id ON image_connectors(album_id);")
cursor.execute("CREATE INDEX IF NOT EXISTS idx_image_connectors_image_id ON image_connectors(image_id);")


cursor.execute("CREATE INDEX IF NOT EXISTS idx_tag_connectors_tag_id ON tag_connectors(tag_id);")
cursor.execute("CREATE INDEX IF NOT EXISTS idx_tag_connectors_image_id ON tag_connectors(image_id);")

conn.commit()
conn.close()