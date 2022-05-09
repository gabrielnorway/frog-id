import numpy as np
import json
import cv2
import os
import shutil




def frog_region(path, contour):
    img = cv2.imread(path)
    pts = np.array(contour).astype(int)
    color = [255, 255, 255]

    stencil = np.zeros(img.shape).astype(img.dtype)
    cv2.fillPoly(stencil, [pts], color)

    result = cv2.bitwise_and(img, stencil)

    (topy, topx) = (np.min(pts[:, 1]), np.min(pts[:, 0]))
    (bottomy, bottomx) = (np.max(pts[:, 1]), np.max(pts[:, 0]))
    result = result[topy : bottomy + 1, topx : bottomx + 1]

    result = cv2.cvtColor(result, cv2.COLOR_BGR2GRAY)

    result = cv2.medianBlur(result, 1)

    result = cv2.adaptiveThreshold(
        result, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 101, 1
    )
    # display(result)
    # display(img)
    # path = path[:-4]
    # print(path)
    # cv2.imwrite(path+'_region.jpg', result)
    return result


# function to detect the features by finding key points and descriptors from the image
def detector(image1, image2):
    # creating ORB detector
    detect = cv2.ORB_create()

    # finding key points and descriptors of both images using detectAndCompute() function
    key_point1, descrip1 = detect.detectAndCompute(image1, None)
    key_point2, descrip2 = detect.detectAndCompute(image2, None)
    return (key_point1, descrip1, key_point2, descrip2)


def json_read_contour(image_path):
    with open(image_path + ".json", "r") as read_file:
        json_tmp = json.load(read_file)
    return json_tmp["annotations"][0]["contour"]


def read_json_directory(path):
    dir_list = []
    for root, dir, files in os.walk(path):
        test = root + "/"
        for file in files:
            if file.endswith(".json"):
                json = file
                dir_list.append(os.path.join(test + json[: len(json) - 5]))
    return dir_list


def matches_sort(matches, images_list):
    matches = np.dstack((np.array(images_list), np.array(matches)))
    matches = matches[0]
    return matches[np.argsort(matches[:, 1].astype(np.int16))[::-1]]


def BF_FeatureMatcher(des1, des2):
    brute_force = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    no_of_matches = brute_force.match(des1, des2)

    # finding the humming distance of the matches and sorting them
    no_of_matches = sorted(no_of_matches, key=lambda x: x.distance)
    return no_of_matches


def display_output(pic1, kpt1, pic2, kpt2, best_match):

    # drawing the feature matches using drawMatches() function
    return cv2.drawMatches(pic1, kpt1, pic2, kpt2, best_match, None, flags=2)
    # cv2.imshow('Output image',output_image)


def id_folder(path):
    path = os.path.split(path)
    path = os.path.split(path[0])
    return path[1]


def successful_match(matches, images_list, target_image):
    matches = matches_sort(matches, images_list)

    successful = 0
    for i in range(10):
        if id_folder(target_image) == id_folder(matches[:, 0][i]):
            successful += 1
    return successful


def show_matches(matches, images_list):
    matches = matches_sort(matches, images_list)
    for i in range(10):
        second_image = matches[i][0]
        second_image_json = second_image[:-4]
        second_image_contour = json_read_contour(second_image_json)

        img2 = frog_region(second_image, second_image_contour)
        key_pt1, descrip1, key_pt2, descrip2 = detector(img1, img2)
        number_of_matches = BF_FeatureMatcher(descrip1, descrip2)

        comparison = display_output(img1, key_pt1, img2, key_pt2, number_of_matches)

        h, w = comparison.shape[0:2]
        neww = 800
        newh = int(neww * (h / w))

        comparison = cv2.resize(comparison, (neww, newh))

        target = cv2.imread(
            os.path.join(path_all_image_directory, target_image + ".jpg")
        )
        target = cv2.resize(target, (neww, newh))

        predict = cv2.imread(matches[i][0])
        predict = cv2.resize(predict, (neww, newh))

        cv2.imshow("compare", comparison)
        cv2.imshow("target", target)
        cv2.imshow("predict", predict)

        cv2.waitKey(0)
        cv2.destroyAllWindows()
        # img2 = cv2.imread(matches[i][0])
        # print(matches[i])
        # display(img2)


if __name__ == "__main__":
    path_single_image_directory = (
        "/home/nos/code-school/bachelor-ikt300/cutout/Photo-data/"
    )
    path_all_image_directory = path_single_image_directory
    path_reduced_image = (
        "/home/nos/code-school/bachelor-ikt300/cutout/Photo-multiple-data/"
    )

    everything = read_json_directory(path_all_image_directory)
    reduced_image = read_json_directory(path_reduced_image)
    total_success = 0

    for image in range(len(reduced_image)):
        print(image)

        # everything without current image
        # print(image)
        ewi = reduced_image
        del ewi[image]
        target_image = reduced_image[image]

        matches = []
        images_list = []

        first_image_contour = json_read_contour(reduced_image[image])
        frog_list = ewi

        img1 = frog_region(
            reduced_image[image] + ".jpg",
            first_image_contour,
        )
        for json_file in range(len(frog_list)):

            # print(frog_list[json_file])

            # second_image_contour = json_read_contour(frog_list[json_file])

            # print(frog_list[json_file])
            # print(json_file)
            second_image = os.path.join(frog_list[json_file] + ".jpg")

            # img2 = frog_region(second_image, second_image_contour)
            region_path = frog_list[json_file] + "_region.jpg"
            img2 = cv2.imread(region_path)


            ###########################################################
            # by brute force matching code from 
            # https://www.geeksforgeeks.org/feature-matching-using-brute-force-in-opencv/
            # laste checked: 2 may 2022
            ############################################################################

            # storing the finded key points and descriptors of both of the images
            key_pt1, descrip1, key_pt2, descrip2 = detector(img1, img2)

            number_of_matches = BF_FeatureMatcher(descrip1, descrip2)
            tot_feature_matches = len(number_of_matches)

            matches.append(int(tot_feature_matches))
            images_list.append(second_image)

        total_success += successful_match(matches, images_list, target_image)

    # print(matches)
    # print(images_list)
    print(total_success)
