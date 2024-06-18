from pydantic import BaseModel
from firebase import db
from google.cloud.firestore_v1.base_query import FieldFilter
from datetime import datetime
from connect_s3 import client, bucket_name
from botocore.exceptions import ClientError
import os
from .model import get_model, Model, get_method
import json
import logging
class Train(BaseModel):
    id: str = ""
    name: str = ''
    description: str = ''
    model: str = ''
    status: str = "IDLE"
    init_epoch: int = 100
    inc_epoch: int = 80
    created_at: str = datetime.now()
    def create_to_firebase(self):
        data = self.to_dict()
        data.pop("id")
        updated_time, doc_ref = db.collection("trains").add(data)
        snapshot = doc_ref.get()
        if snapshot.exists:
            self.id = snapshot.id
            return self
        else:
            return None
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "model": self.model,
            "status": self.status,
            "init_epoch": self.init_epoch,
            "inc_epoch": self.inc_epoch,
            "created_at": self.created_at
        }
    def apply_dict(self, d=None):
        if d is not None:
            for key, value in d.items():
                setattr(self, key, value) 
    async def train(self):
        db.collection("models").document(self.model).update({"status": "TRAINING", "current_train_session": self.id})
        db.collection("trains").document(self.id).update({"status": "PROCESSING"})
        if not await self.create_train_directory():
            return {"message": "Create training folder unsuccessfully.", "model": self, "train": None}
        return {"message": "Training started", "model": (await get_model(self.model)).to_dict(), "train": self}
    async def create_train_directory(self):
        model = (await get_model(self.model))
        response = client.list_objects_v2(Bucket='pycil.com')
        if "working/" not in response['Contents'][1:]:
            client.put_object(Bucket=bucket_name, Key = "working/")
        folder_path = "working/" + self.model + "_" + str(len(await get_training_session(self.model))) + "/"
        client.put_object(Bucket = bucket_name, Key = folder_path)
        result = await move_data_to_train_directory(model, folder_path)
        if not result:
            return result
        with open("configs/base_config.json", "r") as f:
            config = json.load(f)
            print(isinstance(model.method, dict))
            config['model_name'] = model.method['name'] if isinstance(model.method, dict) else get_method(model.method - 1)["name"]
            config['path'] = folder_path + "data"
            config['init_cls'] = model.init_cls
            config['increment'] = model.inc_cls
            config['init_epochs'] = self.init_epoch
            config['boosting_epochs'] = self.inc_epoch
            f.close()
        with open("config.json", "w+") as fo:
            json.dump(config, fo)
            fo.close()
        try:
            response = client.upload_file("config.json", bucket_name, folder_path + "config.json")
            os.remove("config.json")
        except ClientError as e:
            logging(e)
            return False
        return True
async def get_training_session(id: str):
    docs = db.collection("trains").where(filter=FieldFilter("model", "==", id)).stream()
    result = []
    for doc in docs:
        train_session = Train()
        print(train_session)
        train_session.id = doc.id
        train_session.apply_dict(doc.to_dict())
        result.append(train_session.to_dict())
    return result
async def move_data_to_train_directory(model: Model, training_key : str):
    try:
        client.head_object(Bucket=bucket_name, Key=training_key)
        print(f"Key: '{training_key}' found!")
    except ClientError as e:
        if e.response["Error"]["Code"] == "404":
            logging.error(f"Key: '{training_key}' does not exist!")
        else:
            logging.error("Something else went wrong")
            return False                                            
    client.put_object(Bucket = bucket_name, Key = training_key + "data/")
    for key in model.data:                                                                                                                                                                                         
        try:
            client.put_object(Bucket=bucket_name, Key = training_key + "data/" + key.split("/")[-2])
            response = client.list_objects_v2(Bucket=bucket_name, Prefix=key)
            for object in response['Contents'][1:]:
                copy_response = client.copy(CopySource={'Bucket': bucket_name, 'Key': object["Key"]}, Bucket=bucket_name, Key = training_key + "data/" + object["Key"].split("/")[-1])
        except ClientError as e:
            logging.error(e)
            return False
    return True
async def delete_train(id:str):
    doc_ref = db.collection("trains").document(id)
    if doc_ref.get().exists:
        doc_ref.delete()
        return True
    else:
        return False
async def get_train(id: str):
    doc_ref = db.collection("trains").document(id)
    snapshot = doc_ref.get()
    if not snapshot.exists:
        return None
    train = Train()
    train.apply_dict(snapshot.to_dict())
    return train