import numpy as np
import sys
from skimage.measure import find_contours
from shapely.geometry import Polygon, MultiPolygon
from skimage import measure
import json
import os
from keras.preprocessing.image import load_img, img_to_array
from mrcnn.visualize import display_instances
from mrcnn.config import Config
from mrcnn.model import MaskRCNN
import matplotlib.pyplot as plt
import logging
import warnings


os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
logging.getLogger("tensorflow").setLevel(logging.WARNING)
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=Warning)
os.environ["KMP_WARNINGS"] = "0"

import tensorflow as tf


tf.compat.v1.logging.set_verbosity(tf.compat.v1.logging.ERROR)

# tf.logging.set_verbosity(tf.logging.ERROR)


def annotateResult(result, image_name, label):
    n = len(result["class_ids"])
    annotations = []
    annotationId = 1
    for i in range(n):
        if class_names[result["class_ids"][i]] == label:
            annotation = create_sub_mask_annotation(
                result["masks"][:, :, i],
                result["rois"][i],
                annotationId,
                result["class_ids"][i],
                image_name,
            )
            # annotations.append(annotation)
            annotations = annotation
            annotationId += 1
    return annotations


def create_sub_mask_annotation(
    sub_mask, bounding_box, annotationId, classId, image_name, class_names
):
    # Find contours (boundary lines) around each sub-mask
    contours = measure.find_contours(sub_mask, 0.5, positive_orientation="low")
    # print(contours)
    np.savetxt("contour.csv", contours[0], fmt=("%s, %f"))
    # contours.ndarray.tofile('output.txt')
    # np.save('output.txt', contours)

    segmentations = []
    polygons = []
    for contour in contours:
        # Flip from (row, col) representation to (x, y)
        # and subtract the padding pixel
        for i in range(len(contour)):
            row, col = contour[i]
            contour[i] = (col - 1, row - 1)

        # Make a polygon and simplify it
        poly = Polygon(contour)
        poly = poly.simplify(1.0, preserve_topology=False)
        polygons.append(poly)
        segmentation = np.array(poly.exterior.coords).ravel().tolist()
        segmentations.append(segmentation)

    # Combine the polygons to calculate the bounding box and area
    multi_poly = MultiPolygon(polygons)
    x, y, max_x, max_y = multi_poly.bounds
    width = max_x - x
    height = max_y - y
    bbox = (x, y, width, height)
    area = multi_poly.area
    contour_json = contour.tolist()
    # my own

    annotation = {
        "images": [
            {
                "file_name": image_name,
                # "height": 3872,
                # "width": 2592,
                "id": annotationId,
            }
        ],
        "annotations": [
            {
                "id": 0,
                "iscrowd": 0,
                "image_id": 1,
                "category_id": 1,
                "segmentation": segmentations,
                "bbox": bbox,
                "area": area,
                "contour": contour_json,
            }
        ],
        "categories": [
            {
                "id": 1,
                "name": str(class_names[classId]),
            }
        ],
    }

    # annotation = {
    #         "filename": image_name,
    #         "id": annotationId,
    #         "label": str(class_names[classId]),
    #         "bbox": bbox,
    #         "segmentation": segmentations,
    # "regions": [
    #     {
    #         "shape_attributes": {
    #             "name": "polygon",
    #             "all_points_x": contour[:, 0].tolist(),
    #             "all_points_y": contour[:, 1].tolist(),
    #         },
    #         "region_attributes": {"label": "frog_stomach"},
    #     },
    # ],
    #     }

    return annotation


def writeToJSONFile(path, fileName, data):
    fileName = fileName.split(".")[0]
    filePathNameWExt = path + "/" + fileName + ".json"
    with open(filePathNameWExt, "w") as fp:
        json.dump(data, fp)


def annotateAndSaveAnnotations(r, directory, image_name, label):
    annotationsJson = annotateResult(r, image_name, label)
    writeToJSONFile(directory, image_name, annotationsJson)


def annotateImagesInDirectory(rcnn, directory_path, label, multiple_annotation):
    for fileName in os.listdir(directory_path):
        if (
            fileName.endswith(".jpg")
            or fileName.endswith(".jpeg")
            or fileName.endswith(".png")
            or fileName.endswith(".tif")
            or fileName.endswith(".tiff")
        ):
            # load image
            print("Evaluating Image: " + fileName)

            img = load_img(directory_path + "/" + fileName)
            img = img_to_array(img)
            # make prediction
            results = rcnn.detect([img], verbose=0)
            # get dictionary for first prediction
            result = results[0]
            if len(result["scores"]) != 1:
                multiple_annotation.append(fileName)

            if class_names.index(label) in result["class_ids"]:
                print("Label found in image: " + fileName)
                print("Annotating...")
                annotateAndSaveAnnotations(result, directory_path, fileName, label)
                if args.displayMaskedImages is True:
                    label = label
                    # display_instances(
                    #    img,
                    #    result["rois"],
                    #    result["masks"],
                    #    result["class_ids"],
                    #    class_names,
                    #    class_names.index(label),
                    #    result["scores"],
                    # )
            else:
                print("Label not found in image: " + fileName)


def annotateSingleImage(weights_path, fileName, label):
    class InferenceCustomConfig(Config):
        NAME = "inferenceCustom"
        GPU_COUNT = 1
        IMAGES_PER_GPU = 1
        NUM_CLASSES = 1 + 1

    config = InferenceCustomConfig()
    class_names = ["BG"]
    class_names.append(label)

    rcnn = MaskRCNN(mode="inference", config=config, model_dir="./")

    rcnn.load_weights(weights_path, by_name=True)

    # load image
    print("Evaluating Image: " + fileName, flush=True)

    img = load_img(fileName)
    img = img_to_array(img)
    # make prediction
    results = rcnn.detect([img], verbose=0)
    # get dictionary for first prediction
    result = results[0]

    if class_names.index(label) in result["class_ids"]:
        print("Label found in image: " + fileName, end=' - ')
        print("Annotating...", flush=True)
        annotateAndSaveAnnotationsSingle(result, fileName, label, class_names)
    else:
        print("Label not found in image: " + fileName, flush=True)


def annotateAndSaveAnnotationsSingle(r, image_name, label, class_names):
    annotationsJson = annotateResultSingle(r, image_name, label, class_names)
    directory = os.path.split(image_name)
    directory, image_name = directory[0], directory[1]
    writeToJSONFileSingle(directory, image_name, annotationsJson)


def annotateResultSingle(result, image_name, label, class_names):
    n = len(result["class_ids"])
    annotations = []
    annotationId = 1
    for i in range(n):
        if class_names[result["class_ids"][i]] == label:
            annotation = create_sub_mask_annotation(
                result["masks"][:, :, i],
                result["rois"][i],
                annotationId,
                result["class_ids"][i],
                image_name,
                class_names,
            )
            # annotations.append(annotation)
            annotations = annotation
            annotationId += 1
    return annotations


def writeToJSONFileSingle(path, fileName, data):
    fileName = fileName.split(".")[0]
    filePathNameWExt = path + "/" + fileName + ".json"
    with open(filePathNameWExt, "w") as fp:
        json.dump(data, fp)


ROOT_DIR = os.path.abspath("./")
COCO_WEIGHTS_PATH = os.path.join(ROOT_DIR, "./mask_rcnn_coco.h5")

# Directory to save logs, if not provided
# through the command line argument --logs
DEFAULT_LOGS_DIR = os.path.join(ROOT_DIR, "logs")
COCO_DATASET_LABELS = [
    "BG",
    "person",
    "bicycle",
    "car",
    "motorcycle",
    "airplane",
    "bus",
    "train",
    "truck",
    "boat",
    "traffic light",
    "fire hydrant",
    "stop sign",
    "parking meter",
    "bench",
    "bird",
    "cat",
    "dog",
    "horse",
    "sheep",
    "cow",
    "elephant",
    "bear",
    "zebra",
    "giraffe",
    "backpack",
    "umbrella",
    "handbag",
    "tie",
    "suitcase",
    "frisbee",
    "skis",
    "snowboard",
    "sports ball",
    "kite",
    "baseball bat",
    "baseball glove",
    "skateboard",
    "surfboard",
    "tennis racket",
    "bottle",
    "wine glass",
    "cup",
    "fork",
    "knife",
    "spoon",
    "bowl",
    "banana",
    "apple",
    "sandwich",
    "orange",
    "broccoli",
    "carrot",
    "hot dog",
    "pizza",
    "donut",
    "cake",
    "chair",
    "couch",
    "potted plant",
    "bed",
    "dining table",
    "toilet",
    "tv",
    "laptop",
    "mouse",
    "remote",
    "keyboard",
    "cell phone",
    "microwave",
    "oven",
    "toaster",
    "sink",
    "refrigerator",
    "book",
    "clock",
    "vase",
    "scissors",
    "teddy bear",
    "hair drier",
    "toothbrush",
]


