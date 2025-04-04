# Web Services Engineering - Final Project
## GIMP Extension Website Proposal
## Created by John Foster, Fatima Kahbi, Alex Smith, Roshni Patel, and Moises Valles

### What is this?
This project is a proposed implementation of the ["Extension Website"](https://developer.gimp.org/core/internship/ideas/#extension-website) that is listed on GIMP's Project ideas page. Its a simple website using Python, HTML, and Javascript website for hosting GIMP extensions, similar to the old [GIMP Registry](https://www.gimp.org/registry/).

The Original Requirements list proposed by Jehan can be found on the GNOME [GitLab Repository](https://gitlab.gnome.org/Infrastructure/gimp-extensions-web/-/blob/master/docs/README.md)

### How to Run Locally
The simplest way to run is the `run_app.bat` file used to start the Flask server. This will create a new database.db file if you don't have one or deleted it. It will also provide an IP address (for me its http://127.0.0.1:5000/) to access the client.html template file and interact with the database.
If you have an IDE, you can set up a python virtual environment with Flask downloaded, and run app.py to also launch the program. The URL that's generated should be the same.

### API Documentation
[Original Class API Schema Google Sheet](https://docs.google.com/document/d/1Hy8mu29JaC8YT_zD_RM68AxtDEgFvCD3gcOVnuhJORw/edit?tab=t.0#heading=h.5izcxrb3yy7p)

| METHOD | ENDPOINT                                   | DESCRIPTION                                                                                         | EXAMPLE REQUEST [PLACEHOLDER]                                                                 | EXAMPLE RESPONSE [PLACEHOLDER]                                       |
|--------|--------------------------------------------|-----------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------|----------------------------------------------------------------------|
| GET    | /repository/metadata                       | Gets repository metadata. Returns the current repository listing containing all extension metadata. | `GET /repository/metadata`                                                                    | `[{"id": 1, "title": "Example", "creator": "John Doe", ...}]`        |
| GET    | /repository/extension/{id}/{version}       | Download specified extension version package.                                                       | `GET /repository/extension/1/1.0`                                                             | `{"version": "1.0", "download_link": "http://example.com/download"}` |
| PUT    | /extension                                 | Uploads a new extension.                                                                            | `PUT /extension` with JSON body: `{"title": "Example", "creator": "John Doe", ...}`           | `{"success": true}`                                                  |
| GET    | /extension/{id}                            | Returns a single extension's metadata.                                                              | `GET /extension/1`                                                                            | `{"id": 1, "title": "Example", "creator": "John Doe", ...}`          |
| PUT    | /extension/{id}                            | Updates a single extension with a new version.                                                      | `PUT /extension/1` with JSON body: `{"title": "Updated Example", "creator": "John Doe", ...}` | `{"success": true}`                                                  |
| DELETE | /extension/{id}                            | Deletes an extension version.                                                                       | `DELETE /extension/1`                                                                         | `{"success": true}`                                                  |
| POST   | /extension/{id}/flag                       | Flag an extension for review.                                                                       | `POST /extension/1/flag`                                                                      | `{"success": true}`                                                  |
| POST   | /auth/register                             | Create registration for a new user.                                                                 | `POST /auth/register` with JSON body: `{"username": "johndoe", "password": "password123"}`    | `{"success": true}`                                                  |
| POST   | /auth/login                                | Authenticate an existing user who's logging in.                                                     | `POST /auth/login` with JSON body: `{"username": "johndoe", "password": "password123"}`       | `{"success": true}`                                                  |
| GET    | /plugin/{id}                               | Get a plugin and details about it.                                                                  | `GET /plugin/1`                                                                               | `{"id": 1, "title": "Example", "creator": "John Doe", ...}`          |
| PUT    | /extension/sanitizeExtension               | Process ran as a part of extension uploading to check against metadata guidelines.                  | `PUT /extension/sanitizeExtension` with JSON body: `{"id": 1, "title": "Example", ...}`       | `{"success": true}`                                                  |
| DELETE | /extension/searchExtensions/{query}/{tags} | Searches for a subset of extensions.                                                                | `DELETE /extension/searchExtensions/query/tags`                                               | `[{"id": 1, "title": "Example", "creator": "John Doe", ...}]`        |