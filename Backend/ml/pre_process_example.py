def rgb2gray(rgb):
    """Convert the input image into grayscale"""
    import numpy as np
    return np.dot(rgb[...,:3], [0.299, 0.587, 0.114])


def resize_img(img_to_resize):
    """Resize image to MNIST model input dimensions"""
    import cv2
    r_img = cv2.resize(img_to_resize, dsize=(28, 28), interpolation=cv2.INTER_AREA)
    r_img.resize((1, 1, 28, 28))
    return r_img


def preprocess_image(img_to_preprocess):
    """Resize input images and convert them to grayscale."""
    if img_to_preprocess.shape == (28, 28):
        img_to_preprocess.resize((1, 1, 28, 28))
        return img_to_preprocess

    grayscale = rgb2gray(img_to_preprocess)
    processed_img = resize_img(grayscale)
    return processed_img

# preprocess_result['result'] = preprocess_image(image) ## 此句必须添加

import numpy as np
# import torch
import cv2

def defualt_process(img):
    img = cv2.resize(img, (28, 28))
    img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    img = img / 255
    img = np.ascontiguousarray(img)
    # img = torch.from_numpy(img)
    img = img.astype(np.float)
    img = img.reshape(1,1,28,28)
    # if img.ndimension() == 3:
    #     img = img.unsqueeze(0)
    return img