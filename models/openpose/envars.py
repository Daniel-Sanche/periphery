from os import environ
import inspect


def CONTROLLER_ADDRESS():
    """
    The address of the controller server
    """
    var_name = inspect.stack()[0][3]
    return environ.get(var_name, 'localhost:8080')


def INACTIVITY_THRESHOLD():
    """
    How long (in seconds) to wait for a response before stating to poll
    """
    var_name = inspect.stack()[0][3]
    return int(environ.get(var_name, 5))


def POLL_TIME():
    """
    How often to send new frame requests when controller isn't responding
    """
    var_name = inspect.stack()[0][3]
    return int(environ.get(var_name, 1))


def AUTO_RUN():
    """
    Sets whether the model should request images from the controller
    """
    var_name = inspect.stack()[0][3]
    return environ.get(var_name, 'True') == 'True'


def INCLUDE_TOTAL_TIME():
    """
    Sets whether responses should include total processing time
    """
    var_name = inspect.stack()[0][3]
    return environ.get(var_name, 'True') == 'True'


def INCLUDE_INFERENCE_TIME():
    """
    Sets whether responses should include inference processing time
    """
    var_name = inspect.stack()[0][3]
    return environ.get(var_name, 'False') == 'True'


#############################################

def USE_GPU():
    """
    Determines whether to use GPU for inference instead of CPU
    """
    var_name = inspect.stack()[0][3]
    return environ.get(var_name, 'False') != 'False'


def OUTPUT_BOXES():
    """
    Include bounding boxes in output
    """
    var_name = inspect.stack()[0][3]
    return environ.get(var_name, 'False') == 'True'


def OUTPUT_POSES():
    """
    Include sementic masks in output
    """
    var_name = inspect.stack()[0][3]
    return environ.get(var_name, 'True') == 'True'
