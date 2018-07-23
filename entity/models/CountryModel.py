from sqlalchemy.sql import any_
from settings import logger
from entity.validators import CountryCreateSchema, CountrySchema
from .BaseModel import BaseModel
from entity.country import Country


# business-model by entity User
class CountryModel(BaseModel):
    def __init__(self, select_fields: set=set()):
        """
        :param select_fields: set, list fields for result
        """
        super().__init__(
            entity_cls=Country,
            all_fields=(
                'id',
                'label',
                'created_at',
                'updated_at',
            ),
            select_fields=select_fields
        )

    # Schema for create
    def _get_create_schema(self):
        return CountryCreateSchema()

    # Schema for update
    def _get_update_schema(self):
        return CountrySchema()