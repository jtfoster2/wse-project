# Standard Library
import sys
import logging
from datetime import timedelta

# Flask & Extensions
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from flask_jwt_extended import create_access_token, JWTManager, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash

# Third-Party
from rapidfuzz import process, fuzz

# Local Modules
from database import setup_db, db
from database import Users, Extension, Version

def create_app():
    
    app = Flask(__name__, template_folder='./templates')
    logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
    app.logger.setLevel(logging.DEBUG)
    app.config['JWT_SECRET_KEY'] = 'a_very_secret_key'

    CORS(app) 
    setup_db(app)
    JWTManager(app)

    return app

app = create_app()


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

# Get metadata for all extensions
@app.route('/repository/metadata', methods=['GET'])
def get_repository_metadata():
    extensions = Extension.query.all()
    extensions_dict = [extension.to_dict() for extension in extensions]
    return jsonify(extensions_dict), 200

# Gets a single extension's metadata
@app.route('/extension/<int:extension_id>', methods=['GET'])
def get_single_extension(extension_id):
    extension = Extension.query.filter_by(id=extension_id).first()
    if not extension:
        return jsonify({"error": "Extension not found"}), 404
    return jsonify(extension.to_dict()), 200

# Upload new extension w/new version - protected endpoint requires auth
@app.route('/extension', methods=['PUT'])
@jwt_required()
def add_extension():
    try:
        current_user_id = int(get_jwt_identity()) # get user_id for linking to extension
        data = request.get_json()

        new_extension = Extension(
            title=data['title'],
            meta_license=data['meta_license'],
            project_license=data['project_license'],
            creator=current_user_id,
            extends=data['extends'],
            summary=data['summary'],
            description=data['description'],
            tags=data.get('tags', []),
            screenshots=data.get('screenshots', []), # takes url links
            releases=data.get('releases', [])
        )
        db.session.add(new_extension)
        db.session.flush()  # get new_extension.id before commit

        new_version = Version(
            extension_id=new_extension.id,
            version=data.get('releases', [])[0],
            plugin_url=data['plugin_url'], # takes url links
        )
        db.session.add(new_version)
        new_extension.releases.append(new_version.version)

        db.session.commit()
        return jsonify({
            "extension": new_extension.to_dict(),
            "version": new_version.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

# Update an new version to an existing extention - protected endpoint requires auth
@app.route('/extension/<int:extension_id>', methods=['PUT'])
@jwt_required()
def put_extension(extension_id):

    # Verify that the user is adding a version to an extension they created
    current_user_id = int(get_jwt_identity())
    extension = Extension.query.filter_by(id=extension_id).first()
    if not extension:
        return jsonify({"error": "Extension not found"}), 404
    if extension.creator != current_user_id:
        return jsonify({'error': 'Unauthorized to update this extension'}), 403

    try:
        data = request.get_json()
        new_version = Version(
            extension_id=extension.id,
            version=data['version'],
            plugin_url=data['plugin_url'],
        )
        db.session.add(new_version)
        db.session.flush()

        extension.releases = extension.releases + [new_version.version]
        db.session.commit()
        return jsonify({
            "extension": extension.to_dict(),
            "version": new_version.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

# Download a specified extension version
@app.route('/repository/extension/<int:extension_id>/<path:version>', methods=['GET'])
def get_extension_download(extension_id, version):
    target_version = Version.query.filter_by(extension_id=extension_id, version=version).first()
    if not target_version:
        return jsonify({"error": "Version not found"}), 404
    return jsonify(target_version.to_dict()), 200

# Download a specified extension version
@app.route('/plugin/<int:extension_id>', methods=['GET'])
def get_plugin(extension_id):
    return get_single_extension(extension_id)

# Flag an extension for review
@app.route('/extension/<int:extension_id>/flag', methods=['POST'])
def post_extension_flag(extension_id):
    extension = Extension.query.filter_by(id=extension_id).first()
    if not extension:
        return jsonify({"error": "Extension not found, unable to flag"}), 404

    extension.is_flagged = True

    try:
        db.session.commit()
        return jsonify(extension.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

# Deletes an extension version - protected endpoint requires auth
@app.route('/extension/<int:extension_id>/<int:version_id>', methods=['DELETE'])
@jwt_required()
def delete_extension(extension_id, version_id):
    # Verify that the user is deleting an extension version that they created
    app.logger.debug(f"jwt identity: {get_jwt_identity()}")
    current_user_id = int(get_jwt_identity())
    extension = Extension.query.filter_by(id=extension_id).first()
    if extension.creator != current_user_id:
        return jsonify({'error': 'Unauthorized to delete this extension'}), 403

    version = Version.query.filter_by(id=version_id, extension_id=extension_id).first()
    if not version:
        return jsonify({'error': 'Version not found'}), 404

    db.session.delete(version)
    db.session.commit()
    return jsonify({'success': True}), 200

# Searches for a subset of extensions
@app.route('/extension/searchExtensions/<string:query>/<string:tags>', methods=['GET'])
def search_extensions(query, tags):
    extensions = Extension.query.all()
    results = []

    # Convert query to lowercase 
    # TODO: FK - handle spaces send as %20 or whatever
    query = query.strip().lower()

    # Fuzzy match extention titles
    if query != '_':

        title_to_exts = {}
        for ext in extensions:
            title_to_exts.setdefault(ext.title.lower(), []).append(ext)

        titles = list(title_to_exts.keys())
        matches = process.extract(query, titles, scorer=fuzz.WRatio, limit=20)

        for match in matches:
            title, score, _ = match
            if score > 70:
                results.extend(title_to_exts[title])

    else:
        results = extensions  # no query, include all


    # Filter by tag
    if tags != '_':
        requested_tags = tags.split(",")
        filtered_results = []
        for ext in results:
            lowercase_ext_tags = [tag.lower() for tag in ext.tags]
            for tag in requested_tags:
                if tag.lower() in lowercase_ext_tags:
                    filtered_results.append(ext)
                    break
        results = filtered_results

    return jsonify([ext.to_dict() for ext in results]), 200

@app.route('/auth/login', methods=['POST'])
def login():
    data = request.form  # assuming form data
    user = Users.query.filter_by(email=data['email']).first()
    app.logger.debug(f"login user: {data['email']}")
    users = Users.query.all()
    app.logger.debug(f"emails: {[u.email for u in users]}")
    if not user or not check_password_hash(user.password, data['password']):
        return jsonify({'message': 'Invalid email or password'}), 400

    # Create the JWT token with the user ID as a string
    app.logger.debug(f"user id requesting access token: {user.id}")
    access_token = create_access_token(identity=str(user.id), expires_delta=timedelta(hours=1))
    app.logger.debug(f"access_token: {access_token}")
    return jsonify(access_token=access_token, username=user.username), 200

@app.route('/auth/register', methods=['POST'])
def register():
    data = request.form  # assuming form data

    existing_user = Users.query.filter_by(email=data['email']).first()
    if existing_user:
        return jsonify({'message': 'Email already in use'}), 400

    hashed_password = generate_password_hash(data['password'], method='pbkdf2:sha256')
    new_user = Users(
        username=data['username'],
        email=data['email'],
        password=hashed_password,
    )

    db.session.add(new_user)
    db.session.commit()

    # Create the JWT token with the new user's ID as a string
    app.logger.debug(f"user id requesting access token: {users.id}")
    access_token = create_access_token(identity=str(new_user.id), expires_delta=timedelta(hours=1))
    return jsonify(access_token=access_token, username=new_user.username), 201

# TODO: implement
# IMO terrible name from the class API Doc, should probably come up with a better name
@app.route('/extension/sanitizeExtension', methods=['PUT'])
# Class Description: Process ran as a part of extension uploading to check against metadata guidelines.
def put_sanitize_extension(id):
    # TODO: Figure out what needs to be done here.
    return None

# This function can be used in an IDE to run the app locally instead of using run_app.bat
if __name__ == '__main__':
    app.run(debug=True)