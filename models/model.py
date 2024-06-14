from typing_extensions import List
from pydantic import BaseModel
from firebase import db
from connect_s3 import check_folder
from datetime import datetime
class Model(BaseModel):
    
    # The line `id: Union(str | None)` in the `Model` class is defining the `id` attribute as a Union
    # of two types - `str` and `None`. This means that the `id` attribute can hold either a string
    # value or a `None` value. This is useful when you want to allow a field to be optional and
    # potentially have a `None` value in addition to a specific type.
    id: str = ""
    name: str = ''
    method: int = -1
    init_cls: int = 0
    inc_cls: int = 0
    data: List[str] = []
    cls_list: List[str] = []
    created_at: str = datetime.now()
    async def create_in_firebase(self):
        data = {
            "name": self.name, 
            "method": self.method, 
            "init_cls": self.init_cls, 
            "inc_cls": self.inc_cls, 
            "data": self.data,
            "created_at": self.created_at}
        cls_list = []
        data.update({"cls_list": cls_list})
        for x in self.data:
            cls_list.extend(await check_folder(x))
        update_time, model_ref = db.collection("models").add(data)
        snapshot = model_ref.get()
        
        if(snapshot.exists):
            return {"message": "Successfully create a model with id" + snapshot.id, "data":{"id": snapshot.id, **snapshot.to_dict()}}
        else:
            return {"message": "A error has ocurred", "data": None}
    async def get_model_from_firebase(self, id):
        model_ref = db.collection("models").document(id)
        snapshot = model_ref.get()
        return {"id": snapshot.id, **snapshot.to_dict()}
    def apply_dict_to_model(self, d=None):
        if d is not None:
            for key, value in d.items():
                setattr(self, key, value) 
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "method": self.method,
            "init_cls": self.init_cls,
            "inc_cls": self.inc_cls,
            "data": self.data,
            "created_at": self.created_at,
            "cls_list": self.cls_list}
    def minimized_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "created_at": self.created_at,
            "cls_list": self.cls_list,
            "cls_number": len(self.cls_list)
        }
async def get_all_model(search: str = None, order_by: str='name'):
    docs  = db.collection("models").order_by(order_by).stream()
    result = []
    for doc in docs:
        data = doc.to_dict()
        model = Model()
        model.apply_dict_to_model(data)
        result.append(model)
    return result
async def get_model(id: str):
    doc = db.collection("models").document(id)
    snapshot = doc.get()
    if snapshot.exits:
        data = snapshot.to_dict()
        model = Model()
        model.apply_dict_to_model(data)
        return model
    else:
        return None