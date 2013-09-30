#!/usr/bin/env python
# -*- coding: utf-8 -*-

import contextlib
import flask
import mpd
import os
import urllib
import yaml

app = flask.Flask(__name__)


@app.route("/favicon.ico")
def favicon():
    return app.send_static_file("favicon.ico")


@app.route('/')
def albums():
    with mpd_client() as client:
        albums = sorted(client.list('album'))
    return flask.render_template('albums.html', albums=albums, nav="albums")


@app.route('/album/<album>')
def album(album):

    with mpd_client() as client:
        songs = client.find('album', urllib.unquote(album))
        sorted_songs = sorted(songs, key=track_order)
    return flask.render_template('album.html', album=album, songs=sorted_songs,
                                 nav="albums")


def track_order(song):
    if 'track' in song:
        try:
            return int(song['track'])
        except ValueError:
            return song['track']

    if 'title' in song:
        return song['title']

    return os.path.basename(song['file'].lower())


@app.route('/playlist')
def playlist():
    with mpd_client() as client:
        songs = client.playlistinfo()
    return flask.render_template('playlist.html', songs=songs, nav="playlist")


@app.route('/queue-album', methods=['POST'])
def queue_album():

    with mpd_client() as client:
        for song in flask.request.form.getlist('songs'):
            client.add(song)

    return flask.redirect('/playlist')


@app.route('/remove-songs', methods=['POST'])
def remove_songs():

    with mpd_client() as client:
        for song in flask.request.form.getlist('songs'):
            client.deleteid(song)

    return flask.redirect('/playlist')


@app.route('/choose-song')
def choose_song():

    with mpd_client() as client:
        songs = client.playlistinfo()

    return flask.render_template('choose_song.html', songs=songs,
                                 nav="playlist")


@app.route('/edit_edit')
def edit_playlist():

    with mpd_client() as client:
        songs = client.playlistinfo()

    return flask.render_template('edit_playlist.html', songs=songs,
                                 nav="playlist")


@app.route('/save_playlist', methods=['GET', 'POST'])
def save_playlist():
    with mpd_client() as client:
        if flask.request.method == 'GET':
            songs = client.playlistinfo()
            return flask.render_template('save_playlist.html', songs=songs,
                                         nav="playlist")

        client.save(flask.request.form['playlist'])
        return flask.redirect('/stored_playlists')


@app.route('/stored_playlists', methods=['GET'])
def stored_playlists():
    with mpd_client() as client:
        playlists = [playlist['playlist'] for playlist in
                     client.listplaylists()]
        return flask.render_template('stored_playlists.html',
                                     playlists=playlists,
                                     nav="stored_playlists")


@app.route('/stored-playlist/<playlist>', methods=['GET'])
def stored_playlist(playlist):
    with mpd_client() as client:
        songs = client.listplaylistinfo(playlist)
        return flask.render_template('stored_playlist.html',
                                     playlist=playlist,
                                     songs=songs, nav="stored_playlist")


@app.route('/remove-playlists', methods=['POST'])
def remove_playlists():
    with mpd_client() as client:
        for playlist in flask.request.form.getlist('playlists'):
            client.rm(playlist)
        return flask.redirect('/stored_playlists')


@app.route('/play-song', methods=['POST'])
def play_song():

    with mpd_client() as client:
        client.playid(flask.request.form['song'])

    return flask.redirect('/stream')


@app.route('/stop', methods=['POST'])
def stop():

    with mpd_client() as client:
        client.stop()

    return flask.redirect('/stream')


@app.route('/stream')
def stream():
    with open('settings.yaml') as f:
        settings = yaml.load(f)

    return flask.render_template('stream.html',
                                 stream_url=settings['stream-url'],
                                 nav="stream")


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
