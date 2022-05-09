from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db_connector import db_uri
from app.classes import Frog, Image, User
from app.common import _print
import time
from cutout.cutout_main import cutout_main
from auto_annotate.annotate_server import annotateSingleImage
import os
import csv
import traceback


ROOT_IMAGE_PATH = '/frog_images/'
UNKNOWN_IMAGE_PATH = os.path.join(ROOT_IMAGE_PATH, './unknown/')
IDENTIFIED_IMAGE_PATH = os.path.join(ROOT_IMAGE_PATH, './identified/')


def remove_file_extension(filename):
    return filename.rsplit('.', 1)[0] if '.' in filename else filename


def save_csv(score_list, path, filename):
    with open(os.path.join(path, remove_file_extension(filename)+'.csv'), 'w') as file:
        write = csv.writer(file)
        write.writerow(['image_path', 'num_matches'])
        write.writerows(score_list)


def cutout_wrapper(image):
    image_path = os.path.join(UNKNOWN_IMAGE_PATH, image.filename)
    result = cutout_main(image_path, IDENTIFIED_IMAGE_PATH)
    save_csv(result, UNKNOWN_IMAGE_PATH, image.filename)


def annotate_wrapper(image):
    file_path = os.path.join(UNKNOWN_IMAGE_PATH, image.filename)
    annotateSingleImage("/auto_annotate/mask_rcnn_frog_stomach_0029.h5", file_path, "frog_stomach")


def main():
    time.sleep(40)
    while True:
        engine = create_engine(db_uri)
        Session = sessionmaker(bind=engine)
        try:
            with Session() as session:
                image = session.query(Image).filter(Image.ml_status == 'queued').first()
                if not image:
                    continue
                _print(f"[ML] found image {image.filename}, ml_status={image.ml_status}")
                annotate_wrapper(image)
                cutout_wrapper(image)
                image.ml_status = 'done'
                session.commit()
                _print(f"[ML] done with image {image.filename}, ml_status={image.ml_status}")
        except Exception as e:
            _print("[ML] Pattern recognition error:", e)
            _print(traceback.format_exception(None, e, e.__traceback__))
            traceback.print_exc()
            time.sleep(60*2)
        time.sleep(1)






if __name__ == '__main__':
    main()


