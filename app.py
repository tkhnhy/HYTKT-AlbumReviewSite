from flask import Flask
from flask import redirect, render_template, request, session
from flask_sqlalchemy import SQLAlchemy
from os import getenv
from werkzeug.security import check_password_hash, generate_password_hash
import useful_function as uf

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = getenv("DATABASE_URL").replace("://", "ql://", 1)
#app.config["SQLALCHEMY_DATABASE_URI"] = getenv("DATABASE_URL")
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
	message = session.get("notification")
	session["notification"] = ""
	
	return render_template("newgenre.html", message=message)

@app.route("/creategenre", methods=["POST"])
def create_genre():
	genre_name = request.form["genre_name"]
	if len(genre_name) <= 0:
		session["notification"] = "Genre form has to be filled!"
		return redirect("/genre/add")
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
	
	sql = "SELECT reviews.content, reviews.review_date, users.username FROM reviews, users WHERE reviews.album_id=:id AND users.id=reviews.user_id"
	result = db.session.execute(sql, {"id":id})
	review_content = result.fetchall()
	
	if len(review_content) == 0:
		review_content = ["Seems like there are no reviews yet."]
	return render_template("album.html", id=id,alb_name=albumname, art_name=artistname, alb_con=con_list,review_content=review_content)

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
	message = session.get("notification")
	session["notification"] = ""
	
	result = db.session.execute("SELECT genres.genre_name FROM genres")
	available_genres = result.fetchall()
	return render_template("newalbum.html", genres=available_genres, message=message)

@app.route("/createalbum", methods=["POST"])
def create_album():
	album_name_new = request.form["album_name"]
	artist_name_text = request.form["artist_name"]
	album_genre_text = request.form["alb_genre"]
	
	if len(album_name_new) <= 0:
		session["notification"] = "Album form has to be filled!"
		return redirect("/addalbum")
	if len(artist_name_text) <= 0:
		session["notification"] = "Artist form has to be filled!"
		return redirect("/addalbum")
	
	sql = ("SELECT artists.id FROM artists WHERE artists.artist_name=:artist_name_text")
	result = db.session.execute(sql, {"artist_name_text":artist_name_text})
	is_artist = result.fetchone()
	if is_artist == None:
		sql = "INSERT INTO artists (artist_name) VALUES (:artist_name_text)"
		result = db.session.execute(sql, {"artist_name_text":artist_name_text})
	
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
	message = session.get("notification")
	session["notification"] = ""
	
	return render_template("addsong.html", id=id, message=message)

@app.route("/create_song", methods=["POST"])
def create_song():
	song_name_new = request.form["song_name"]
	song_length_new = request.form["song_length"]
	album_id_new = request.form["album_id"]
	
	if len(song_name_new) <= 0:
		session["notification"] = "Song name form has to be filled!"
		return redirect(f"/album/{album_id_new}/add_song")
	if int(song_length_new) <= 0 or int(song_length_new) >= 100000:
		session["notification"] = "Song lenght cannot be negative or over 100000s"
		return redirect(f"/album/{album_id_new}/add_song")
	sql = "INSERT INTO songs (album_id,song_name,song_length_seconds) VALUES (:album_id,:song_name,:song_length)"
	result = db.session.execute(sql, {"album_id":album_id_new,"song_name":song_name_new,"song_length":song_length_new})
	db.session.commit()
	return redirect(f"/album/{album_id_new}")
	
@app.route("/loginpage")
def login_page():
	message = session.get("notification")
	session["notification"] = ""
	
	return render_template("loginpage.html", message=message)

@app.route("/login", methods=["POST"])
def login():
	username = request.form["username"]
	password = request.form["password"]
	sql = "SELECT user_password FROM users WHERE username=:username"
	result = db.session.execute(sql, {"username":username})
	user = result.fetchone()    
	
	if user == None:
		session["notification"] = "Username or password is incorrect"
		return redirect("/loginpage")
	else:
		hash_value = user[0]
		if check_password_hash(hash_value,password):
			session["username"] = username
			#sql = "SELECT user_role FROM users WHERE users.username=:username"
			#result = db.session.execute(sql, {"username":username})
			#session["user_role"] = result.fetchone()
			return redirect("/")
		else:
			session["notification"] = "Username or password is incorrect"
			return redirect("/loginpage")

@app.route("/logout")
def logout():
    del session["username"]
    return redirect("/")

@app.route("/registerpage")
def register_page():
	message = session.get("notification")
	session["notification"] = ""
	return render_template("/registerpage.html", message=message)
	
@app.route("/register", methods=["POST"])
def register():
	username = request.form["username"]
	password = request.form["password"]
	if len(username) <= 0:
		notification = "Username form cannot be empty!"
		session["notification"] = notification
		return redirect("/registerpage") 
	else:
		if len(password) <= 6:
			notification = "Password has to be over 6 characters!"
			session["notification"] = notification
			return redirect("/registerpage") 
		else:
			sql = "SELECT COUNT(*) FROM users WHERE users.username=:username"
			result = db.session.execute(sql, {"username":username})
			is_user = result.fetchall()
			if is_user[0][0] > 0:
				notification = "This username is already taken"
				session["notification"] = notification
				return redirect("/registerpage") 
			else:
				basic_role = 1
				hash_value = generate_password_hash(password)
				sql = "INSERT INTO users (username, user_password, user_role) VALUES (:username,:password,:role)"
				db.session.execute(sql, {"username":username,"password":hash_value,"role":basic_role})
				db.session.commit()
				return redirect("/loginpage")

@app.route("/searchresults", methods=["GET"])
def searchresults():
	query = request.args["query"]
	sql = "SELECT albums.id, album_name, artist_name, genre_name FROM albums, artists, genres "\
		  "WHERE artists.id = albums.artist_id AND albums.album_genre_id = genres.id "\
		  "AND (albums.album_name ILIKE :query OR artists.artist_name ILIKE :query OR genres.genre_name ILIKE :query);"
	result = db.session.execute(sql, {"query":"%"+query+"%"})
	albs = result.fetchall()
	return render_template("searchresults.html",keyword=query, albums=albs)

