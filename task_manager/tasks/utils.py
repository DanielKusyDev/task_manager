import abc
import calendar
from copy import deepcopy
from datetime import datetime
from functools import wraps

from bson import ObjectId
from flask_jwt_extended import get_jwt_identity

from task_manager.db import Model, AggregationPipeline


def task_owner_only(fn):
    @wraps(fn)
    def wrapper(task_id, *args, **kwargs):
        user_id = get_jwt_identity()["_id"]
        tasks_model = Model("tasks")
        tasks_model.get_one(raise_404=True, _id=ObjectId(task_id), user_id=user_id)
        return fn(task_id, *args, **kwargs)

    return wrapper


class AbstractReportService(abc.ABC):
    model = Model("tasks")
    keys = None

    @abc.abstractmethod
    def get_report_partial_pipeline(self, pipeline, done_only):
        raise NotImplementedError

    def generate_reports(self):
        user_id = get_jwt_identity()["_id"]
        Model("users").get_one(raise_404=True, _id=ObjectId(user_id))
        total = {"done": 0, "not_done": 0}
        values = [total.copy() for _ in self.keys]

        base_pipeline = AggregationPipeline()
        base_pipeline.add_match(user_id=user_id)
        base_pipeline.add_projection(done=1, end_date=1)
        for done_only in True, False:
            pipeline = deepcopy(base_pipeline)
            pipeline = self.get_report_partial_pipeline(pipeline, done_only)
            pipeline.add_sorting(["_id"])
            cursor = self.model.aggregate(pipeline.pipeline, evaluate=False)
            done_key = "done" if done_only else "not_done"
            for task in cursor:
                index = task["_id"] - 1
                values[index][done_key] = task["count"]
                total[done_key] += task["count"]
        return values, total

    def get_reports(self):
        values, total = self.generate_reports()
        result = {
            "total": total,
            "keys": self.keys,
            "values": values,
        }
        return result


class WeeklyReportService(AbstractReportService):
    keys = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']

    def get_report_partial_pipeline(self, pipeline, done_only):
        pipeline.add_projection(week={"$week": "$end_date"}, day={"$day": "$end_date"})
        pipeline.add_match(done=done_only, week=datetime.utcnow().isocalendar()[1] - 1)
        pipeline.add_group(_id="$day", count={"$sum": 1})
        return pipeline


class MonthlyReportService(AbstractReportService):
    keys = calendar.monthrange(datetime.utcnow().year, datetime.utcnow().month)

    def get_report_partial_pipeline(self, pipeline, done_only):
        pipeline.add_projection(day={"$day": "$end_date"})
        pipeline.add_match(done=done_only, month=datetime.utcnow().month)
        pipeline.add_group(_id="$day", count={"$sum": 1})


class YearlyReportService(AbstractReportService):
    keys = calendar.month_name[1:]

    def get_report_partial_pipeline(self, pipeline, done_only):
        pipeline.add_projection(month={"$month": "$end_date"})
        pipeline.add_match(done=done_only, month=datetime.utcnow().month)
        pipeline.add_group(_id="$month", count={"$sum": 1})
        return pipeline
