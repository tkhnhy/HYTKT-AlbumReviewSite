from flask import Flask
from flask import redirect, render_template, request, session
from flask_sqlalchemy import SQLAlchemy
from os import getenv
from werkzeug.security import check_password_hash, generate_password_hash
import useful_function as uf

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = getenv("DATABASE_URL").replace("://", "ql://", 1)
app.secret_key = getenv("SECRET_KEY")
db = SQLAlchemy(app)

#TODO
#Add ratings to albums, needs just a new sql table with album_id, user_id and rating 1-10
#Add login functionality
#Add reviews

@app.route("/")
def index():
	return render_template("index.html")

@app.route("/all")
def all_list():
	result = db.session.execute("SELECT COUNT(*) FROM albums")
	count = result.fetchone()[0]
	sql = "SELECT albums.id, album_name, artist_name, genre_name FROM albums, artists, genres "\
		  "WHERE artists.id = albums.artist_id AND albums.album_genre_id = genres.id;"
	result = db.session.execute(sql)
	albs = result.fetchall()
	return render_template("allalbums.html", count=count, albums=albs)

@app.route("/genre")
def list_genres():
	result = db.session.execute("SELECT * FROM genres")
	allgenres = result
	return render_template("allgenres.html", gnrs = allgenres)

@app.route("/genre/add")
def add_genre_site():
	return render_template("newgenre.html")

@app.route("/creategenre", methods=["POST"])
def create_genre():
	genre_name = request.form["genre_name"]
	sql = "INSERT INTO genres (genre_name) VALUES (:genre_name)"
	result = db.session.execute(sql, {"genre_name":genre_name})
	db.session.commit()
	return redirect("/genre")

@app.route("/album/<int:id>")
def album(id):
	sql = "SELECT song_name, song_length_seconds FROM songs,albums WHERE albums.id = songs.album_id AND albums.id=:id ORDER BY songs.id;"
	result = db.session.execute(sql, {"id":id})
	alb_content = result.fetchall()
	con_list = []
	for i in alb_content:
		val1 = i[0]
		val2 = uf.convert(i[1])
		temtuple = (val1, val2)
		con_list.append(temtuple)
	
	sql = "SELECT album_name FROM albums WHERE id=:id"
	result = db.session.execute(sql, {"id":id})
	albumname = result.fetchone()[0]
	
	sql = "SELECT artist_name FROM artists, albums WHERE albums.id=:id AND albums.artist_id = artists.id"
	result = db.session.execute(sql, {"id":id})
	artistname = result.fetchone()[0]
	return render_template("album.html", id=id,alb_name=albumname, art_name=artistname, alb_con=con_list)

@app.route("/genre/<int:id>")
def genre_albums(id):
	sql = "SELECT albums.id, album_name, artist_name FROM albums, artists, genres " \
          "WHERE artists.id = albums.artist_id AND albums.album_genre_id=:id AND genres.id=:id;"
	result = db.session.execute(sql, {"id":id})
	albs = result.fetchall()
	sql = "SELECT COUNT(albums.id) FROM albums, genres WHERE genres.id =:id AND albums.album_genre_id=:id"
	result = db.session.execute(sql, {"id":id}) 
	count = result.fetchone()[0]
	sql = "SELECT genre_name FROM genres WHERE genres.id =:id"
	result = db.session.execute(sql, {"id":id}) 
	gname = result.fetchone()[0]
	return render_template("genre.html", id=id, genrename=gname, count=count, albums=albs)
	
@app.route("/addalbum")
def add_album_site(): 
	result = db.session.execute("SELECT genres.genre_name FROM genres")
	available_genres = result.fetchall()
	return render_template("newalbum.html", genres=available_genres)

@app.route("/createalbum", methods=["POST"])
def create_album():
	album_name_new = request.form["album_name"]
	artist_name_text = request.form["artist_name"]
	album_genre_text = request.form["alb_genre"]
	
	result = db.session.execute(f"SELECT artists.id FROM artists WHERE artists.artist_name='{artist_name_text}'")
	is_artist = result.fetchone()
	if is_artist == None:
		sql = f"INSERT INTO artists (artist_name) VALUES ('{artist_name_text}')"
		result = db.session.execute(sql)
	
	result = db.session.execute(f"SELECT artists.id FROM artists WHERE artists.artist_name='{artist_name_text}'")
	artist_id_new = result.fetchone()
	
	result = db.session.execute(f"SELECT genres.id FROM genres WHERE genres.genre_name='{album_genre_text}'")
	genre_id_new = result.fetchone()
	sql = "INSERT INTO albums (album_name,artist_id,album_genre_id) VALUES (:album_name,:artist_id,:genre_id)"
	result = db.session.execute(sql, {"album_name":album_name_new,"artist_id":artist_id_new[0],"genre_id":genre_id_new[0]})
	db.session.commit()
	sql = "SELECT albums.id FROM albums WHERE albums.album_name=:album_name"
	result = db.session.execute(sql, {"album_name":album_name_new})
	id = result.fetchone()
	return redirect(f"/album/{id[0]}")

@app.route("/album/<int:id>/add_song")
def addsong(id):	
	return render_template("addsong.html", id=id)

@app.route("/create_song", methods=["POST"])
def create_song():
	song_name_new = request.form["song_name"]
	song_length_new = request.form["song_length"]
	album_id_new = request.form["album_id"]
	sql = "INSERT INTO songs (album_id,song_name,song_length_seconds) VALUES (:album_id,:song_name,:song_length)"
	result = db.session.execute(sql, {"album_id":album_id_new,"song_name":song_name_new,"song_length":song_length_new})
	db.session.commit()
	return redirect(f"/album/{album_id_new}")
	
@app.route("/loginpage")
def login_page():
	return render_template("loginpage.html")

@app.route("/login", methods=["POST"])
def login():
	username = request.form["username"]
	password = request.form["password"]
	sql = "SELECT user_password FROM users WHERE username=:username"
	result = db.session.execute(sql, {"username":username})
	user = result.fetchone()    
	
	if user == None:
		return redirect("/loginpage")
	else:
		hash_value = user[0]
		if check_password_hash(hash_value,password):
			session["username"] = username
			return redirect("/")
		else:
			return redirect("/loginpage")

@app.route("/logout")
def logout():
    del session["username"]
    return redirect("/")

@app.route("/registerpage")
def register_page():
	return render_template("/registerpage.html")
	
@app.route("/register", methods=["POST"])
def register():
	username = request.form["username"]
	password = request.form["password"]
	sql = f"SELECT COUNT(*) FROM users WHERE users.username='{username}'"
	result = db.session.execute(sql)
	is_user = result.fetchall()
	if is_user[0][0] > 0:
		session["taken"] = True
		return redirect("/registerpage")
	else:
		basic_role = 1
		hash_value = generate_password_hash(password)
		sql = "INSERT INTO users (username, user_password, user_role) VALUES (:username,:password,:role)"
		db.session.execute(sql, {"username":username,"password":hash_value,"role":basic_role})
		db.session.commit()
		return redirect("/loginpage")



