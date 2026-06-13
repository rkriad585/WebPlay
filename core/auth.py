import os
from functools import wraps
from flask import request, jsonify, render_template, current_app


def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        required_key = current_app.config.get('API_KEY')
        if required_key:
            auth_key = request.args.get('key')
            if auth_key != required_key:
                if request.path.startswith('/api/'):
                    return jsonify(success=False, error="Unauthorized"), 403
                return render_template('error.html'), 403
        return f(*args, **kwargs)
    return decorated


def validate_media_path(path, current_root):
    if not path:
        return None
    resolved = os.path.realpath(path)
    root = os.path.realpath(current_root)
    if not resolved.startswith(root):
        return None
    if not os.path.exists(resolved):
        return None
    return resolved
