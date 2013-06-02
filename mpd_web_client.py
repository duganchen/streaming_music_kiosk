import contextlib
import flask
import mpd
import urllib
import yaml

app = flask.Flask(__name__)


@app.route("/favicon.ico")
def favicon():
    return app.send_static_file("favicon.ico")


@app.route('/')
def albums():
    with mpd_client() as client:
        albums = sorted((urllib.quote(album), album)
                        for album in client.list('album'))
    return flask.render_template('albums.html', albums=albums)


@app.route('/album/<album>')
def album(album):
    track_order = lambda song: (song['track'] if 'track' in song
                                else song['title'].lower().strip())
    with mpd_client() as client:
        songs = client.find('album', urllib.unquote(album))
        sorted_songs = sorted(songs, key=track_order)
    return flask.render_template('album.html', album=album, songs=sorted_songs)


@app.route('/playlist')
def playlist():
    with mpd_client() as client:
        songs = client.playlistinfo()
    return flask.render_template('playlist.html', songs=songs)


@app.route('/queue-album', methods=['POST'])
def queue_album():

    with mpd_client() as client:
        for song in flask.request.form.getlist('songs'):
            client.add(song)

    return flask.redirect('/playlist')


@app.route('/remove-songs', methods=['POST'])
def remove_album():

    with mpd_client() as client:
        for song in flask.request.form.getlist('songs'):
            client.deleteid(song)

    return flask.redirect('/playlist')


@app.route('/choose-song')
def choose_song_album():

    with mpd_client() as client:
        songs = client.playlistinfo()

    return flask.render_template('choose_song.html', songs=songs)


@app.route('/play-song', methods=['POST'])
def play_song():

    with mpd_client() as client:
        client.playid(flask.request.form['song'])

    with open('settings.yaml') as f:
        settings = yaml.load(f)

    return flask.redirect(settings['stream-url'])


@contextlib.contextmanager
def mpd_client():

    with open('settings.yaml') as f:
        settings = yaml.load(f)

    client = mpd.MPDClient(use_unicode=True)
    client.connect(settings['connection']['host'],
                   settings['connection']['port'])
    yield client
    client.close()
    client.disconnect()


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0')
