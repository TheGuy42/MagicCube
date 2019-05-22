import os
import pickle


class Pickler:

    @staticmethod
    def dump(file_name, data):
        with open(file_name, 'wb') as MyData:
            pickle.dump(data, MyData)
        MyData.close()

    @staticmethod
    def load(file_name):
        if os.path.exists(file_name):
            with open(file_name, 'rb') as MyData:
                tmp_data = pickle.load(MyData)
            MyData.close()
            return tmp_data
        return None
