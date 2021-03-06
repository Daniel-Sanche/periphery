import onnxruntime as rt
import numpy as np
from PIL import Image
import math
import cv2
import envars


class OnnxModel():
    def __init__(self, model_path='MaskRCNN-10.onnx',
                 class_path='coco_classes.txt'):
        self.name = model_path.split('.')[0]
        self.sess = rt.InferenceSession("MaskRCNN-10.onnx")
        self.inputs = self.sess.get_inputs()
        self.outputs = self.sess.get_outputs()
        self.classes = [line.rstrip('\n') for line in open('coco_classes.txt')]

        # print input/output details
        print("backend: {}".format(rt.get_device()))
        print("inputs:")
        for i, input in enumerate(self.inputs):
            print("{} - {}: {} - {}".format(
                i, input.name, input.shape, input.type))
        print("outputs:")
        for i, output in enumerate(self.outputs):
            print("{} - {}: {} - {}".format(
                i, output.name, output.shape, output.type))

    def preprocess(self, pil_image):
        """
        Reformat generic PIL image to onnx input form
        """
        # Resize
        # ratio = 800.0 / min(pil_image.size[0], pil_image.size[1])
        # image = pil_image.resize((int(ratio * pil_image.size[0]),
        #       int(ratio * pil_image.size[1])), Image.BILINEAR)
        image = pil_image
        # Convert to BGR
        image = np.array(image)[:, :, [2, 1, 0]].astype('float32')
        # HWC -> CHW
        image = np.transpose(image, [2, 0, 1])
        # Normalize
        mean_vec = np.array([102.9801, 115.9465, 122.7717])
        for i in range(image.shape[0]):
            image[i, :, :] = image[i, :, :] - mean_vec[i]
        # Pad to be divisible of 32
        padded_h = int(math.ceil(image.shape[1] / 32) * 32)
        padded_w = int(math.ceil(image.shape[2] / 32) * 32)
        padded_image = np.zeros((3, padded_h, padded_w), dtype=np.float32)
        padded_image[:, :image.shape[1], :image.shape[2]] = image
        img = padded_image
        # return in onnx tensor format
        return {'image': img}

    def run(self, input_dict):
        """
        Run one prediction
        """
        pred = self.sess.run(None, input_dict)
        return pred

    def postprocess(self, orig_image, output_dict):
        """
        Reformat output into standard annotations
        """
        # ratio = 800.0 / min(orig_image.size[0], orig_image.size[1])
        boxes = output_dict[0]
        labels = output_dict[1]
        scores = output_dict[2]
        masks = output_dict[3]
        points = [None for _ in labels]
        if envars.OUTPUT_MASKS():
            points = self._extract_image_masks(orig_image, boxes, labels, scores, masks)

        annotations = []
        confidence_threshold = envars.CONFIDENCE_THRESHOLD()
        for _, box, label, score, point_list in zip(masks, boxes, labels, scores, points):
            if score <= confidence_threshold:
                continue
            if envars.OUTPUT_BOXES():
                this_annotation = {'kind': 'box',
                                    'x': int(box[0]),
                                    'y': int(box[1]),
                                    'height': int(box[3]-box[1]),
                                    'width': int(box[2]-box[0]),
                                    'label': self.classes[label],
                                    'confidence':float(score)}
                annotations.append(this_annotation)
            if envars.OUTPUT_MASKS():
                mask_annotation = {'kind': 'mask',
                                   'points': point_list,
                                   'label': self.classes[label],
                                   'confidence':float(score)}
                annotations.append(mask_annotation)
        return {'name': self.name, 'annotations': annotations}

    def _extract_image_masks(self, image, boxes, labels, scores, masks):
        # taken from https://github.com/onnx/models/tree/master/vision/object_detection_segmentation/mask-rcnn
        image = np.array(image)
        points_arr = []
        confidence_threshold = envars.CONFIDENCE_THRESHOLD()

        for mask, box, label, score in zip(masks, boxes, labels, scores):
            # Showing boxes with score > 0.7
            if score <= confidence_threshold:
                continue

            # Finding contour based on mask
            mask = mask[0, :, :, None]
            int_box = [int(i) for i in box]
            mask = cv2.resize(mask, (int_box[2]-int_box[0]+1, int_box[3]-int_box[1]+1))
            mask = mask > 0.5
            im_mask = np.zeros((image.shape[0], image.shape[1]), dtype=np.uint8)
            x_0 = max(int_box[0], 0)
            x_1 = min(int_box[2] + 1, image.shape[1])
            y_0 = max(int_box[1], 0)
            y_1 = min(int_box[3] + 1, image.shape[0])
            mask_y_0 = max(y_0 - int_box[1], 0)
            mask_y_1 = mask_y_0 + y_1 - y_0
            mask_x_0 = max(x_0 - int_box[0], 0)
            mask_x_1 = mask_x_0 + x_1 - x_0
            im_mask[y_0:y_1, x_0:x_1] = mask[
                mask_y_0 : mask_y_1, mask_x_0 : mask_x_1
            ]
            im_mask = im_mask[:, :, None]
            # OpenCV version 4.x
            contours, hierarchy = cv2.findContours(
                im_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE
            )
            contour_list =[{'x':int(a[0]), 'y':int(a[1])} for a in list(np.squeeze(contours[0]))]
            points_arr.append(contour_list)
        return points_arr


if __name__ == '__main__':
    imarray = np.random.rand(1920, 1080, 3) * 255
    img = Image.fromarray(imarray.astype('uint8')).convert('RGB')
    model = OnnxModel()
    input_dict = model.preprocess(img)
    output_dict = model.run(input_dict)
    annotations = model.postprocess(img, output_dict)
    print(annotations)
