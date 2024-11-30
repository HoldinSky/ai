import os
from PIL import Image
import sys
import bson
import pymongo
import numpy as np
from pymongo.synchronous.database import Database

CLEAR_COLLECTIONS_FLAG = False
TRAIN_FLAG = False
SETUP_FLAG = False
TEST_FLAG = False
N = 10


class Block:
    def __init__(self, collection):
        self._collection = collection

    def add(self, data_vector, association=None):
        block = {
            "data": data_vector
        }
        if association is not None:
            block["association"] = association

        self._collection.insert_one(block)

    def find_all(self):
        return self._collection.find({})

    def find_by_id(self, block_id):
        return self._collection.find_one({"_id": bson.ObjectId(block_id)})

    def find_one(self):
        return self._collection.find_one()


class Weight:
    def __init__(self, collection):
        self._collection = collection

    def adjust(self, old_data, data):
        weights = {
            "data": data
        }

        present = self._collection.find_one({"data": old_data})
        if present is None:
            self._collection.insert_one(weights)
        else:
            self._collection.replace_one(present, weights)

    def add(self, data):
        weights = {
            "data": data
        }

        self._collection.insert_one(weights)

    def find_one(self):
        return self._collection.find_one()


def train(db: Database):
    blocks = Block(db.get_collection("blocks"))
    weights = Weight(db.get_collection("weights"))

    block_arr = blocks.find_all().to_list()
    weights_arr = np.zeros((N*N, N*N))

    for b in block_arr:
        data = b["data"]

        input_x = np.array([int(el) for el in data]).reshape(-1, 1)
        weights_arr += input_x @ input_x.T

    for i in range(len(weights_arr)):
        weights_arr[i][i] = 0

    weights.add(weights_arr.tolist())


def recognize(data, weights_collection):
    weights = np.array(weights_collection.find_one().get("data"))

    x = np.array(data).reshape(-1)
    answer = x @ weights.T

    return np.where(answer > 0, 1, -1).flatten()


def setup_collections(db: Database):
    for name in db.list_collection_names():
        db[name].drop()

    db.create_collection("blocks")
    db.create_collection("weights")

def clear_collections(db: Database):
    collection = db.get_collection("blocks")
    collection.delete_many({})

    collection = db.get_collection("weights")
    collection.delete_many({})

def upload_etalons(db: Database):
    data_dir = ".\\data\\lab2\\train"
    block = Block(db.get_collection("blocks"))

    for img_name in os.listdir(data_dir):
        vector = img_to_vector(f"{data_dir}\\{img_name}")
        block.add(vector, img_name.split(".")[0])

def img_to_vector(img_path):
    img_arr = np.asarray(Image.open(img_path))
    img_shape = img_arr.shape

    vector = []

    for i in range(img_shape[0]):
        for ii in range(img_shape[1]):
            if img_arr[i][ii][0] == 0:
                vector.append(1)
            else:
                vector.append(-1)

    return vector

def test(db: Database):
    test_data = img_to_vector(".\\data\\lab2\\test\\f-bad.png")

    res = recognize(test_data, db.get_collection("weights"))
    return res.reshape((10, 10))

def parse_args():
    global CLEAR_COLLECTIONS_FLAG, TRAIN_FLAG, SETUP_FLAG, TEST_FLAG
    CLEAR_COLLECTIONS_FLAG = "--clear" in sys.argv
    TRAIN_FLAG = "--train" in sys.argv
    SETUP_FLAG = "--setup" in sys.argv
    TEST_FLAG = "--test" in sys.argv

if __name__ == "__main__":
    parse_args()
    client = pymongo.MongoClient('localhost', 27017)
    db = client["ai_lab2"]

    try:
        if SETUP_FLAG:
            setup_collections(db)
            clear_collections(db)
            upload_etalons(db)
        if TRAIN_FLAG:
            train(db)
        if TEST_FLAG:
            output = test(db)

            img_data = np.where(output == 1, 0, 255).astype(np.uint8)
            img = Image.fromarray(img_data, mode="L")
            img.save(".\\data\\lab2\\test\\recognized.png")

    finally:
        client.close()
