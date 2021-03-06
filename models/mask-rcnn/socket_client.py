import socketio
import time
from model import OnnxModel
from image_functions import data_url_to_pil
import envars

_last_activity_time = time.time()

sio = socketio.Client()


@sio.event
def connect():
    print('connection established')
    sio.emit('register', model.name)
    sio.emit('frame_request')


@sio.on("process_frame")
def process_frame(data_url):
    global _last_activity_time
    start_time = time.time()
    _last_activity_time = start_time
    # process image
    img = data_url_to_pil(data_url)
    input_dict = model.preprocess(img)
    inference_start = time.time()
    output_dict = model.run(input_dict)
    inference_end = time.time()
    payload = model.postprocess(img, output_dict)
    # build payload
    end_time = time.time()
    _last_activity_time = end_time
    print("[INFO] {} processing time: {:.6f} seconds"
          .format(model.name, end_time - start_time))
    if envars.INCLUDE_TOTAL_TIME():
        payload['time'] = end_time - start_time
    if envars.INCLUDE_INFERENCE_TIME():
        payload['inference_time'] = inference_end - inference_start
    sio.emit('frame_complete', payload)
    # request a new frame
    if envars.AUTO_RUN():
        sio.emit('frame_request')


@sio.event
def disconnect():
    print('disconnected from server')


def poll_timer():
    global _last_activity_time
    while True:
        time.sleep(envars.POLL_TIME())
        elapsed_time = time.time() - _last_activity_time
        if envars.AUTO_RUN() and elapsed_time > envars.INACTIVITY_THRESHOLD():
            print('No activity. Querying controller again')
            sio.emit('frame_request')


if __name__ == '__main__':
    model = OnnxModel()
    sio.connect('http://{}'.format(envars.CONTROLLER_ADDRESS()))
    poll_timer()
