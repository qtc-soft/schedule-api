from sqlalchemy.sql import any_

from .BaseModel import BaseModel

from entity.validators import ScheduleDetailCreateSchema, ScheduleDetailSchema
from entity.schedule import Schedule
from entity.schDetail import SCHDetail


# business-model by entity User
class ScheduleDetailModel(BaseModel):
    def __init__(self, allowed_schedule_ids: set, select_fields: set=set(), creater_id: int = -1):
        """
        :param select_fields: set, list fields for result
        """
        super().__init__(
            entity_cls=SCHDetail,
            all_fields=(
                'id',
                'time',
                'description',
                'members',
                'schedule_id',
                'created_at',
                'updated_at',
            ),
            select_fields=select_fields
        )
        # get creter id for current session
        self.creater_id = creater_id
        # allowed schedules
        self.allowed_schedule_ids = allowed_schedule_ids

    # Schema for create
    @classmethod
    def _get_create_schema(self):
        return ScheduleDetailCreateSchema()

    # Schema for update
    @classmethod
    def _get_update_schema(self):
        return ScheduleDetailSchema()

    # GET Entity
    async def get_entities(self, ids: list, schedule_ids: set = None) -> tuple:
        # result vars
        result = []
        errors = []

        allowed_schedule_ids = self.allowed_schedule_ids
        if schedule_ids:
            # condition by allowed Schedules
            allowed_schedule_ids = self.allowed_schedule_ids.intersection(schedule_ids)

        # conditions for select details, by allowed schedule
        conditions = [self.entity_cls.schedule_id == any_(allowed_schedule_ids)]

        # condition by selector ids
        if ids:
            conditions.append(self.entity_cls.id == any_(ids))

        # select by conditions
        records = await self.entity_cls.select_where(
            str_fields=self.select_fields,
            conditions=conditions
        )

        self.calc_result(records, ids, result, errors)

        return result, errors

    # CREATE Entity
    async def create_entity(self, data: dict, **kwargs) -> tuple:
        # result vars
        result = []

        # schedule id from request params
        sch_id = data.get('schedule_id', -1)

        # if schedule accessable
        if sch_id in self.allowed_schedule_ids:
            result, errors = await super().create_entity(data, **kwargs)
        else:
            errors = self.get_error_item('id', 'You have not such schedule')

        # get entites
        return result, errors

    # UPDATE Entity
    async def update_entity(self, data: dict, **kwargs) -> tuple:
        # result vars
        result = []
        errors = []

        # schedule id from request params
        sch_id = data.get('schedule_id', -1)

        # if schedule accessable
        if sch_id in self.allowed_schedule_ids:
            result, errors = await super().update_entity(data, **kwargs)
        else:
            errors = self.get_error_item('id', 'You have not such schedule')

        # get entites
        return result, errors