# Friend Detector

- Model taken from [ONNX model zoo](https://github.com/onnx/models/tree/master/vision/body_analysis/arcface)
- There are two ways of loading data:
  - add images to /dataset/{name_label}/{image_file}
  - use `SAVE_DATASET_TO_PICKLE` to generate a compressed representation of face data, to avoid keeping PII around in the container
- Try to keep sample numbers consistent across classes
  - The dataset is stored as a [class_num, max_sample_size, 513] vector. Large amounts of sample data could eat up memory
  - It seems like you only need a couple good samples for each face
