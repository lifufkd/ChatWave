import factory
import copy

from models import Users
from utilities import Hash
from constants.users import UsersConstants


class UserFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Users

    username = factory.Faker('user_name')
    password_hash = Hash.hash_password(UsersConstants.DEFAULT_PASSWORD)
    nickname = factory.Faker('user_name')
    birthday = factory.Faker('date_of_birth')
    bio = factory.Faker('text')

    @classmethod
    async def _save(cls, model_class, session, args, kwargs):
        obj = model_class(*args, **kwargs)
        session.add(obj)
        await session.flush()
        d_obj = copy.copy(obj)
        await session.commit()
        return d_obj
