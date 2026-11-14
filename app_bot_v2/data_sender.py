data_callback = None

def botDataSender(data):
    if data_callback is not None:
        data_callback(data)