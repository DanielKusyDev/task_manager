from bson import SON

from task_manager import mongo


class Model:
    def __init__(self, collection_name: str):
        self.collection_name = collection_name
        self.collection = getattr(mongo.db, collection_name)

    def all(self):
        return self.filter()

    def filter(self, **kwargs):
        cursor = self.collection.find(kwargs)
        return cursor

    def get_one(self, raise_404=True, **kwargs):
        selection_fn = self.collection.find_one_or_404 if raise_404 else self.collection.find_one
        return selection_fn(kwargs)

    def insert(self, many=False, **data):
        insertion_fn = self.collection.insert_many if many else self.collection.insert_one
        _id = insertion_fn(data).inserted_id
        return str(_id)

    def update(self, data: dict, many=False, **filters):
        update_fn = self.collection.update_many if many else self.collection.update_one
        update_fn(filters, {"$set": data})
        return data

    def delete(self, many=False, **kwargs):
        delete_fn = self.collection.delete_many if many else self.collection.delete_one
        delete_fn(kwargs)
        return kwargs

    def aggregate(self, pipeline, evaluate=True):
        result = self.collection.aggregate(pipeline)
        return list(result) if evaluate else result

    def count(self):
        return self.collection.count()


class AggregationPipeline:
    def __init__(self):
        self.pipeline = []

    def add_projection(self, **kwargs):
        projection = {"$project": {}}
        for key, value in kwargs.items():
            projection["$project"][key] = value
        self.pipeline.append(projection)

    def add_match(self, **kwargs):
        match = {"$match": {}}
        for key, value in kwargs.items():
            match["$match"][key] = value
        self.pipeline.append(match)

    def add_group(self, **kwargs):
        grouping = {"$group": {}}
        for key, value in kwargs.items():
            grouping["$group"][key] = value
        self.pipeline.append(grouping)

    def add_sorting(self, order_by: list):
        ordering = [(field, 1) for field in order_by]
        sorting = {"$sort": SON(ordering)}
        return sorting
