import requests
from flask import Blueprint, request, redirect, url_for, current_app, make_response, send_from_directory
from flask_login import login_required, login_user, logout_user, current_user
from . import db
from .exts import scheduler
from .classes import Frog, Image, User, add_user
from .secrets import Secrets
from .common import _print, make_json_response
from .settings import Settings
import os
import csv
from werkzeug.utils import secure_filename
import datetime


IMAGE_FILE_EXTENSIONS = {'jpg', 'jpeg'}
app = Blueprint('app', __name__)


@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"


@app.route("/heartbeat")
def heartbeat():
    return {"status": "online"}


def has_file_extension(filename, file_extensions=None):
    if file_extensions is None:
        file_extensions = IMAGE_FILE_EXTENSIONS
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in file_extensions


def replace_file_extension(filename):
    if has_file_extension(filename, {'jpeg'}):
        return filename.rsplit('.', 1)[0] + '.jpg'
    return filename


def remove_file_extension(filename):
    return filename.rsplit('.', 1)[0] if '.' in filename else filename


@app.route('/frog-image/<frog_folder>/<filename>')
def send_frog_image(frog_folder, filename):
    path = current_app.config['FROG_IMAGE_FOLDER']
    return send_from_directory(path, frog_folder+'/'+filename, as_attachment=False)


def web_format_scores():
    max_matches = 10
    image = Image.query.filter_by(ml_status='done', frog_id=None).first()
    if not image:
        return ""
    csv_path = os.path.join(current_app.config['UPLOAD_FOLDER'], remove_file_extension(image.filename) + '.csv')
    response = ""
    if os.path.exists(csv_path):
        with open(csv_path) as file:
            reader = csv.reader(file, delimiter=',')
            header = next(reader)
            for row in reader:
                max_matches -= 1
                if max_matches <= 0:
                    break
                response += f'''
                <p>Score: {row[1]}</p>
                <img src="/frog-image/{row[0].split('/identified/', 1)[1]}" style="max-width: 350px"><br>
                '''
    return response


@app.route('/web-print-scores')
def web_print_scores():
    response = make_response(web_format_scores())
    return response


def handle_image_upload():
    if request.method == 'POST':
        # Check a file has been included
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        # Check if file is empty
        if file.filename == '':
            return redirect(request.url)
        if file and has_file_extension(file.filename):
            filename = secure_filename(replace_file_extension(file.filename))
            new_image = Image(filename='none.none')
            try:
                if current_user and current_user.is_authenticated():
                    new_image.user = current_user.id
            except Exception as e:
                pass
            db.session.add(new_image)
            db.session.commit()
            new_image.filename = str('_' + str(new_image.id) + '.').join(filename.rsplit('.', 1))
            file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], new_image.filename))
            new_image.ml_status = 'queued'
            db.session.commit()
            return make_json_response(msg="file uploaded")
    else:
        return '''
            <!doctype html><title>Frog</title><h1>Upload image</h1><form method="post" enctype=multipart/form-data>
            <input type="file" name="file"><input type="submit" value="Upload"></form>
            '''


@app.route('/upload-frog-image', methods=['GET', 'POST'])
def upload_frog_image():
    response = make_response(handle_image_upload())
    # Used in development - can be removed
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response






@scheduler.task('interval', id='initialize_db', seconds=30, max_instances=1, misfire_grace_time=1)
def initialize_db():
    # Initializes database tables and default accounts on startup.
    with scheduler.app.app_context():
        existing_tables, class_tables = db.inspect(db.get_engine()).get_table_names(), db.metadata.tables.keys()
        if False in [i in existing_tables for i in class_tables]:
            db.create_all()
            db.session.commit()
            _print(f"[SQL] Created tables: {list(class_tables)}")
        for user in Settings.default_users:
            add_user(db, user)
    scheduler.remove_job('initialize_db')
    auto_config_ip()
    # Check for images not registered in database
    with scheduler.app.app_context():
        for _dirpath, _dirnames, _filenames in os.walk(current_app.config['FROG_IMAGE_FOLDER']):
            for _dirname in _dirnames:
                for dirpath, dirnames, filenames in os.walk(os.path.join(_dirpath, _dirname)):
                    for file in filenames:
                        if not has_file_extension(file, {'jpg'}) or Image.query.filter_by(filename=file).first():
                            continue
                        new_image = Image(filename=file, datetime=datetime.datetime.now(), ml_status='done')
                        frog_id = int(_dirname)
                        frog = Frog.query.get(frog_id)
                        if not frog:
                            frog = Frog(id=frog_id, datetime=datetime.datetime.now(), name='frog_'+str(frog_id))
                            db.session.add(frog)
                            db.session.commit()
                        new_image.frog_id = frog.id
                        db.session.add(new_image)
                        db.session.commit()
                    break
            break
        for dirpath, dirnames, filenames in os.walk(current_app.config['UPLOAD_FOLDER']):
            for file in filenames:
                if not has_file_extension(file, {'jpg'}) or Image.query.filter(Image.filename == file).first():
                    continue
                new_image = Image(filename=file, datetime=datetime.datetime.now(), ml_status='queued')
                db.session.add(new_image)
                db.session.commit()
            break


# Updates the IP of the DDNS domain name
@scheduler.task('interval', id='auto_config_ip', seconds=60*60*12, max_instances=1, misfire_grace_time=1)
def auto_config_ip():
    with scheduler.app.app_context():
        _print("", end='')
        # Update IP of DDNS
        username = "frog.resolve.bar"
        password = "9wjavjd2o9gv"
        url = f"https://{username}:{password}@www.dnshome.de/dyndns.php"
        data = {"ip": "10.225.149.82"}
        try:
            result = requests.post(url, data)
        except Exception as e:
            pass


