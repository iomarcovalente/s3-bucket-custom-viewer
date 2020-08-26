import fnmatch, time
from flask import Flask, render_template, g, request, send_from_directory
from os import listdir, environ as env
from datetime import datetime
from flask_simpleldap import LDAP

app = Flask(__name__)
app.config.update(
    LDAP_HOST = env["LDAP_HOST"],
    LDAP_PORT = env["LDAP_PORT"],
    LDAP_SCHEMA = "ldaps",
    LDAP_USE_SSL = True,
    LDAP_REQUIRE_CERT = False,
    LDAP_USERNAME = env["LDAP_USERNAME"],
    LDAP_PASSWORD = env["LDAP_PASSWORD"],
    LDAP_BASE_DN = env["LDAP_BASE_DN"],
    LDAP_USER_OBJECT_FILTER = env["LDAP_USER_OBJECT_FILTER"]
)

mount_point_dir = env.get("MOUNT_DIR","/data")

test_result_folders = []

def refresh_list():
    global test_result_folders
    test_result_folders_formatted = []
    try:
        if not test_result_folders:
            while not test_result_folders:
                # filtering folders for *_1 since those are the only ones that contain test reports
                test_result_folders = fnmatch.filter( listdir( mount_point_dir ), "*_1")
                app.logger.info("Waiting for s3 files to be mounted...")
                time.sleep(1)
        else:
            test_result_folders = fnmatch.filter( listdir( mount_point_dir ), "*_1")
    except FileNotFoundError:
        print("The mount directory '" + mount_point_dir + "' was not found: likely it has not been mounted yet.")
        time.sleep(1)

    i = 0
    for t in test_result_folders:
        t = t[:-2]
        date = datetime.strptime(t, "%Y%m%d%H%M%S").strftime("%d/%m/%Y-%H:%M:%S")
        test_result_folders_formatted.append({ "name": t, "formatted_date": date })
        i += 1
    return test_result_folders_formatted

ldap = LDAP(app)
refresh_list()

@app.route("/")
@ldap.basic_auth_required
def index():
    test_result_folders_formatted = refresh_list()
    app.logger.info("User login: " + g.ldap_username)
    return render_template("index.html", folders=test_result_folders_formatted[::-1])

@app.route("/about")
def about():
    return render_template("about.html")


# TODO: use nginx to serve files instead!
@app.route("/<path:file_name>")
@ldap.basic_auth_required
def select_file(file_name):
    return send_from_directory( mount_point_dir + "/", file_name)
