FROM mcr.microsoft.com/azureml/onnxruntime:v1.2.0

RUN wget https://github.com/onnx/models/raw/master/vision/object_detection_segmentation/mask-rcnn/model/MaskRCNN-10.onnx
RUN wget https://github.com/onnx/models/raw/master/vision/object_detection_segmentation/mask-rcnn/dependencies/coco_classes.txt

COPY requirements.txt /code
RUN pip install -r requirements.txt

# opencv
RUN apt-get update
RUN apt-get install -y libglib2.0-0 libsm6 libxrender-dev

COPY *.py /code/
ENTRYPOINT python socket_client.py
