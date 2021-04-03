from flask import Flask
from flask import redirect, render_template, request
from flask_sqlalchemy import SQLAlchemy
from os import getenv
import useful_function as uf

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = getenv("DATABASE_URL")
db = SQLAlchemy(app)

@app.route("/")
def index():
	return render_template("index.html")

@app.route("/all")
def all_list():
	result = db.session.execute("SELECT COUNT(*) FROM albums")
	count = result.fetchone()[0]
	result = db.session.execute("SELECT albums.id, album_name, artist_name, genre_name FROM albums, artists, genres WHERE artists.id = albums.artist_id AND albums.album_genre_id = genres.id;")
	albs = result.fetchall()
	return render_template("allalbums.html", count=count, albums=albs)

@app.route("/genre")
def list_genres():
	result = db.session.execute("SELECT * FROM genres")
	allgenres = result
	return render_template("allgenres.html", gnrs = allgenres)
	
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
	
	sql = "SELECT artist_name FROM artists, albums WHERE albums.id=:id"
	result = db.session.execute(sql, {"id":id})
	artistname = result.fetchone()[0]
	
	return render_template("album.html", id=id,alb_name=albumname, art_name=artistname, alb_con=con_list)
@app.route("/genre/<int:id>")
def genre_albums(id):
	sql = "SELECT albums.id, album_name, artist_name FROM albums, artists, genres WHERE artists.id = albums.artist_id AND albums.album_genre_id=:id;"
	result = db.session.execute(sql, {"id":id})
	albs = result.fetchall()
	sql = "SELECT COUNT(albums.id) FROM albums, genres WHERE genres.id =:id"
	result = db.session.execute(sql, {"id":id}) 
	count = result.fetchone()[0]
	sql = "SELECT genre_name FROM genres WHERE genres.id =:id"
	result = db.session.execute(sql, {"id":id}) 
	gname = result.fetchone()[0]
	return render_template("genre.html", id=id, genrename=gname, count=count, albums=albs)