from datetime import datetime
from typing import Dict

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi.encoders import jsonable_encoder

from app.models.charity_project import CharityProject
from app.models.donation import Donation


async def investing(
        obj_data: Dict,
        session: AsyncSession,
) -> Dict:
    obj_full_ammount = obj_data['full_amount']
    obj_invested_amount = 0
    if 'user_id' in obj_data:
        not_fully_invested = await session.execute(
            select(CharityProject).where(CharityProject.fully_invested == '0')
        )
    else:
        not_fully_invested = await session.execute(
            select(Donation).where(Donation.fully_invested == '0')
        )
    not_fully_invested_list = not_fully_invested.scalars().all()
    while obj_invested_amount < obj_full_ammount and not_fully_invested_list:
        delta = obj_full_ammount - obj_invested_amount
        invest_obj = not_fully_invested_list[0]
        invest_obj_data = jsonable_encoder(invest_obj)
        left_amount = (
            invest_obj_data['full_amount'] - invest_obj_data['invested_amount']
        )
        if left_amount <= delta:
            obj_invested_amount += left_amount
            not_fully_invested_list.pop(0)
            setattr(
                invest_obj,
                'invested_amount',
                invest_obj_data['full_amount']
            )
            setattr(invest_obj, 'fully_invested', True)
            setattr(invest_obj, 'close_date', datetime.utcnow())
            session.add(invest_obj)
        else:
            obj_invested_amount = obj_full_ammount
            setattr(
                invest_obj,
                'invested_amount',
                invest_obj_data['invested_amount'] + delta
            )
            session.add(invest_obj)
    obj_data['invested_amount'] = obj_invested_amount
    if obj_invested_amount == obj_full_ammount:
        obj_data['fully_invested'] = True
        obj_data['close_date'] = datetime.utcnow()
    return obj_data
