# Web Services Engineering - Final Project
## GIMP Extension Website Proposal
## Created by John Foster, Fatima Kahbi, Alex Smith, Roshni Patel, and Moises Valles

### What is this?
This project is a proposed implementation of the ["Extension Website"](https://developer.gimp.org/core/internship/ideas/#extension-website) that is listed on GIMP's Project ideas page. Its a simple website using Python, HTML, and Javascript website for hosting GIMP extensions, similar to the old [GIMP Registry](https://www.gimp.org/registry/).

The Original Requirements list proposed by Jehan can be found on the GNOME [GitLab Repository](https://gitlab.gnome.org/Infrastructure/gimp-extensions-web/-/blob/master/docs/README.md)

### How to Run Locally
To run this program, you will need to download [PostgreSQL](https://www.postgresql.org/) to run a local database alongside this program.
The simplest way to run is the `run_app.bat` file used to start the application. You will be prompted to input the database name, username,and password.  It will also provide an IP address (for me its http://127.0.0.1:5000/) to access the client.html template file and interact with the database.
If you have an IDE, you can set up a python virtual environment with Flask downloaded, and run app.py to also launch the program. The URL that's generated should be the same.

### API Documentation
[Original Class API Schema Google Sheet](https://docs.google.com/document/d/1Hy8mu29JaC8YT_zD_RM68AxtDEgFvCD3gcOVnuhJORw/edit?tab=t.0#heading=h.5izcxrb3yy7p)

Documentation for this API is hosted via [Postman](https://documenter.getpostman.com/view/35187635/2sB2cd5yne)