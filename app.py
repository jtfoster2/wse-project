
from flask import Flask, request, jsonify, render_template, redirect, url_for
import sqlite3

app = Flask(__name__)

# This function utilizes a database.db file if it exists in the root directory, otherwise it should create one with two tables, metadata, and users.
def _create_db():
    _query_qb('''
        CREATE TABLE IF NOT EXISTS metadata (
            id INTEGER PRIMARY KEY,
            title TEXT, 
            "meta-license" TEXT, 
            "project-license" TEXT, 
            creator TEXT,
            extends TEXT,
            summary TEXT,
            description TEXT,
            "tags" TEXT,
            "screenshots" TEXT,
            "releases" TEXT
        )
    ''')

    _query_qb('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY
            -- TODO: Figure out what fields we need for users
        )
    ''')


# This function handles the SQL queries to the database, so we're not repeating database code across the operations.
def _query_qb(query, params=(), fetch=False):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute(query, params)
    if fetch:
        result = cursor.fetchall()
    else:
        result = None
    conn.commit()
    conn.close()
    return result

# Loads the client.html file when the user accesses the hosting URL.
@app.route('/')
def index():
    return render_template('client.html')

# These endpoints were determined in a class vote via this Google Doc: https://docs.google.com/document/d/1Hy8mu29JaC8YT_zD_RM68AxtDEgFvCD3gcOVnuhJORw/edit?usp=sharing

@app.route('/repository/metadata', methods=['GET'])
# Class Description: Gets repository metadata. Returns the current repository listing containing all extension metadata
def get_repository_metadata():
    metadata = _query_qb('SELECT * FROM metadata')
    # We can reformat extension info that's returned here if needed
    return metadata

@app.route('/repository/extension/<int:id>/string:version>', methods=['GET'])
# Class Description: Download specified extension version package.
def get_extension_download(id, version):
    version_info = _query_qb(f'SELECT version FROM metadata WHERE id = {id}')
    # TODO: Unpack version info to get download link; We'll need to figure out the version formatting first.
    return None

@app.route('/extension', methods=['PUT'])
# Class Description: Uploads a new extension.
def post_extension():
    title = request.form['title']
    creator = request.form['creator']
    extends = request.form['extends']
    summary = request.form['summary']
    meta_license = request.form['meta_license']
    project_license = request.form['project_license']
    description = request.form['description']
    tags = request.form['tags']
    screenshots = request.form['screenshots']
    releases = request.form['releases']

    _query_qb('INSERT INTO metadata (title, creator, extends, summary, meta_license, project_license, description, tags, screenshots, releases) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
              (title, creator, extends, summary, meta_license, project_license, description, tags, screenshots, releases))

    # Doing a redirect here so the page is automatically refreshed with the new entry showing in the database view.
    return redirect(url_for('index'))

@app.route('/extension/<int:id>', methods=['GET'])
# Class Description: Returns a single extension's metadata.
def get_extension(id, version):
    extension_info = _query_qb(f'SELECT * FROM metadata WHERE id = {id}')
    # We can reformat extension info that's returned here if needed
    return extension_info

@app.route('/extension/<int:id>', methods=['PUT'])
# Class Description: Updates a single extension with a new version
def put_extension(id):
    data = request.json
    _query_qb('UPDATE metadata SET title = ?, creator = ?, extends = ?, summary = ?, meta_license = ?, project_license = ?, description = ?, tags = ?, screenshots = ?, releases = ? WHERE id = ?',
              (data['title'], data['creator'], data['extends'], data['summary'], data['meta_license'], data['project_license'], data['description'], data['tags'], data['screenshots'], data['releases'], id))
    return jsonify({'success': True})

@app.route('/extension/<int:id>', methods=['DELETE'])
# Class Description: Deletes an extension version.
def delete_extension(id):
    _query_qb('DELETE FROM metadata WHERE id = ?', (id,))
    return jsonify({'success': True})

@app.route('/extension/<int:id>/flag', methods=['POST'])
# Class Description: Flag an extension for review.
def post_extension_flag(id):
    # TODO: Figure out how flagging will be tracked... Boolean field, or a part of tags?
    return None

@app.route('/auth/register', methods=['POST'])
# Class Description: Create registration for a new user.
def post_user_registration():
    # TODO: HOW ARE WE DOING AUTHENTICATION?
    return None

@app.route('/auth/login', methods=['POST'])
# Class Description: Authenticate an existing user who's logging in.
def post_user_authentication():
    # TODO: HOW ARE WE DOING AUTHENTICATION?
    return None

# This Function sounds like a duplicate of get_extension, but Class API Doc calls for it currently.
@app.route('/plugin/<int:id>', methods=['GET'])
# Class Description: Get a plugin and details about it.
def get_plugin(id):
    extension_info = _query_qb(f'SELECT * FROM metadata WHERE id = {id}')
    # We can reformat extension info that's returned here if needed
    return extension_info

# IMO terrible name from the class API Doc, should probably come up with a better name
@app.route('/extension/sanitizeExtension', methods=['PUT'])
# Class Description: Process ran as a part of extension uploading to check against metadata guidelines.
def put_sanitize_extension(id):
    # TODO: Figure out what needs to be done here.
    return None

@app.route('/extension/searchExtensions/string:query>/string:tags>', methods=['GET'])
# Class Description: Searches for a subset of extensions.
def get_extension_search(query, tags):
    # TODO: Figure out how to search the database for a generalized query and/or tags.
    return None

# This function can be used in an IDE to run the app locally instead of using run_app.bat
if __name__ == '__main__':
    _create_db()
    app.run(debug=True)