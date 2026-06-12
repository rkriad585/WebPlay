import os
import sys
import json
import tempfile
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

os.environ['SECRET_KEY'] = 'test-secret'


@pytest.fixture
def media_dir():
    with tempfile.TemporaryDirectory() as tmpdir:
        videos = os.path.join(tmpdir, 'videos')
        os.makedirs(videos)
        f1 = os.path.join(videos, 'test1.mp4')
        f2 = os.path.join(videos, 'test2.mkv')
        f3 = os.path.join(videos, 'subdir')
        os.makedirs(f3)
        f4 = os.path.join(f3, 'test3.mp4')
        for f in [f1, f2, f4]:
            with open(f, 'wb') as fh:
                fh.write(b'\x00\x00\x00\x00')
        yield tmpdir


@pytest.fixture
def app(media_dir):
    from app import app
    db_path = os.path.join(media_dir, 'test.db')
    app.config.update({
        'TESTING': True,
        'API_KEY': 'valid-key-123',
        'DATABASE_PATH': db_path,
    })
    import app as app_module
    app_module.CURRENT_ROOT = media_dir
    app_module.Config.ensure_dirs()
    app_module.init_db()
    yield app
    app.config['API_KEY'] = None
    if os.path.exists(db_path):
        os.remove(db_path)


@pytest.fixture
def client(app):
    return app.test_client()


class TestAuth:
    def test_free_mode_allows_all(self, client, app):
        app.config['API_KEY'] = None
        resp = client.get('/')
        assert resp.status_code == 200

    def test_secured_mode_rejects_missing_key(self, client):
        resp = client.get('/')
        assert resp.status_code == 403

    def test_secured_mode_rejects_wrong_key(self, client):
        resp = client.get('/?key=wrong-key')
        assert resp.status_code == 403

    def test_secured_mode_accepts_valid_key(self, client):
        resp = client.get('/?key=valid-key-123')
        assert resp.status_code == 200

    def test_api_route_returns_json_on_unauth(self, client):
        resp = client.post('/api/save_progress')
        assert resp.status_code == 403
        assert resp.is_json


class TestPathTraversal:
    def test_player_rejects_outside_root(self, client, media_dir):
        resp = client.get(f'/player?path=/etc/passwd&key=valid-key-123')
        assert resp.status_code == 404

    def test_player_rejects_dotdot(self, client, media_dir):
        resp = client.get(f'/player?path={media_dir}/../outside&key=valid-key-123')
        assert resp.status_code == 404

    def test_player_rejects_nonexistent(self, client, media_dir):
        resp = client.get(f'/player?path={media_dir}/videos/nope.mp4&key=valid-key-123')
        assert resp.status_code == 404

    def test_player_accepts_valid_file(self, client, media_dir):
        p = os.path.join(media_dir, 'videos', 'test1.mp4')
        resp = client.get(f'/player?path={p}&key=valid-key-123')
        assert resp.status_code == 200

    def test_stream_rejects_outside_root(self, client, media_dir):
        resp = client.get(f'/stream?path=/etc/hostname&key=valid-key-123')
        assert resp.status_code == 404

    def test_thumbnail_rejects_outside_root(self, client, media_dir):
        resp = client.get(f'/thumbnail?path=/etc/hostname&key=valid-key-123')
        assert resp.status_code == 404

    def test_subtitle_rejects_outside_root(self, client, media_dir):
        resp = client.get(f'/subtitle?path=/etc/hostname&key=valid-key-123')
        assert resp.status_code == 404

    def test_rename_rejects_outside_root(self, client, media_dir):
        resp = client.post('/api/rename', json={
            'old_path': '/etc/hostname',
            'new_name': 'test'
        }, query_string={'key': 'valid-key-123'})
        assert resp.status_code == 400


class TestRename:
    def test_rename_strips_double_extension(self, client, media_dir):
        p = os.path.join(media_dir, 'videos', 'test1.mp4')
        resp = client.post('/api/rename', json={
            'old_path': p,
            'new_name': 'newname.mp4'
        }, query_string={'key': 'valid-key-123'})
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['success']
        assert data['new_path'].endswith('.mp4')
        assert 'newname.mp4.mp4' not in data['new_path']
        assert os.path.exists(os.path.join(media_dir, 'videos', 'newname.mp4'))

    def test_rename_rejects_existing_target(self, client, media_dir):
        p = os.path.join(media_dir, 'videos', 'test1.mp4')
        collision = os.path.join(media_dir, 'videos', 'collision.mp4')
        with open(collision, 'wb') as f:
            f.write(b'\x00')
        resp = client.post('/api/rename', json={
            'old_path': p,
            'new_name': 'collision'
        }, query_string={'key': 'valid-key-123'})
        assert resp.status_code == 409

    def test_rename_does_not_leak_paths(self, client, media_dir):
        p = os.path.join(media_dir, 'videos', 'nonexistent.mp4')
        resp = client.post('/api/rename', json={
            'old_path': p,
            'new_name': 'whatever'
        }, query_string={'key': 'valid-key-123'})
        assert resp.status_code == 400
        data = resp.get_json()
        assert 'message' not in data or media_dir not in data['message']

    def test_rename_valid_name(self, client, media_dir):
        p = os.path.join(media_dir, 'videos', 'test1.mp4')
        resp = client.post('/api/rename', json={
            'old_path': p,
            'new_name': 'Renamed File 1'
        }, query_string={'key': 'valid-key-123'})
        assert resp.status_code == 200
        assert os.path.exists(os.path.join(media_dir, 'videos', 'Renamed File 1.mp4'))


class TestGallery:
    def test_index_returns_html(self, client):
        resp = client.get('/?key=valid-key-123')
        assert resp.status_code == 200
        assert b'WebPlay' in resp.data

    def test_index_list_view(self, client):
        resp = client.get('/?view=list&key=valid-key-123')
        assert resp.status_code == 200


class TestSaveProgress:
    def test_save_progress(self, client, media_dir):
        p = os.path.join(media_dir, 'videos', 'test1.mp4')
        resp = client.post('/api/save_progress', json={
            'path': p,
            'time': 42.5
        }, query_string={'key': 'valid-key-123'})
        assert resp.status_code == 200
        assert resp.get_json()['success']

    def test_save_progress_missing_fields(self, client):
        resp = client.post('/api/save_progress', json={},
                           query_string={'key': 'valid-key-123'})
        assert resp.status_code == 400
