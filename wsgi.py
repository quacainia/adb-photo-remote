import concurrent.futures
import datetime
import flask
import os
import re
import subprocess
import time

CMD_LIST_PHOTOS = (
    "adb shell ls -t --full-time /sdcard/DCIM/Camera/ | head -n 6 | tail -n 5")
CMD_PULL_FILE_FMT = "adb pull /sdcard/DCIM/Camera/{file} {dest}"
CMD_TAKE_PHOTO = "adb shell input keyevent KEYCODE_VOLUME_DOWN"

LS_ISO_DATE_FMT = "%Y-%m-%d %H:%M:%S.%f"

PATH_IMAGES_DIR = "%s/static/images/" % (
    os.path.dirname(os.path.abspath(__file__))
)

app = flask.Flask(__name__)

images = {}
fid_number = 0

executor = concurrent.futures.ThreadPoolExecutor(max_workers=2)


if not os.path.exists(PATH_IMAGES_DIR):
    os.makedirs(PATH_IMAGES_DIR, exist_ok=True)


def download_file(file):
    cmd = CMD_PULL_FILE_FMT.format(
        file=file,
        dest=PATH_IMAGES_DIR
    )
    result = subprocess.run(cmd.split(), capture_output=True)
    return result.returncode == 0


def get_photo(fid, start, end):
    try:
        retry = 0
        while retry < 10:
            retry += 1
            file, error = get_file_name(fid, start, end)
            if file:
                break
            time.sleep(1)

        if file:
            if download_file(file):
                images[fid] = {"image": file}
            else:
                raise Exception("oops")
        else:
            print("no file found")
            images[fid] = {"error": error}

    except BaseException as e:
        print("ERROR")
        print(e)
        images[fid] = {"error": "%s: %s" % (type(e), e)}


def get_file_name(fid, start, end):
    result = subprocess.run(CMD_LIST_PHOTOS.split(), capture_output=True)
    # print(result.stderr)
    file = None
    error = "File Not Found"

    # for i in range(5):
    #     print("=======================")

    if result.returncode == 0:
        for line in result.stdout.decode().split('\n'):
            # print("line", line)
            if not line.strip():
                continue

            match = re.search(
                (
                    r'(2[\d-]{9} +[\d:]+\.[\d]{6})[\d]*( [-+]\d{4})'
                    r' (PXL[\w\.]+)'
                ),
                line
            )
            # print(match)

            if match:
                # print("match")
                file_date = datetime.datetime.strptime(
                    match.group(1),
                    LS_ISO_DATE_FMT)
                # print('start-0.5', start-datetime.timedelta(seconds=0.5))
                # print('file_date', file_date)
                # print('end-4    ', end+datetime.timedelta(seconds=4))
                if (
                        file_date > start-datetime.timedelta(seconds=0.5)
                        and file_date < end+datetime.timedelta(seconds=4)
                ):
                    file = match.group(3)
                    break
                else:
                    error = "Bad Timestamps"
            else:
                error = "No Match"
    else:
        error = "Command error"

    return (file, error)


@app.route("/")
def hello_world():
    return flask.render_template('index.html')


@app.route("/shoot")
def shoot():
    global fid_number
    start = datetime.datetime.now()
    result = subprocess.run(CMD_TAKE_PHOTO.split(), capture_output=True)
    end = datetime.datetime.now()
    fid = None
    if result.returncode == 0:
        fid = str(fid_number)
        fid_number += 1
        executor.submit(get_photo, fid, start, end)
    else:
        print(result.stderr)
    return {"success": result.returncode == 0, "id": fid}


@app.route("/image/<fid>")
def image(fid):
    global images
    return {fid: images.get(fid)}
