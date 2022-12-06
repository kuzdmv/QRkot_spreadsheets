from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.crud.donation import donation_crud
from app.schemas.donation import (
    DonationDBSuperUser,
    DonationDBCustomUser,
    DonationBase
)
from app.core.user import current_superuser, current_user
from app.models.user import User

router = APIRouter()


@router.get(
    '/',
    response_model=List[DonationDBSuperUser],
    response_model_exclude_none=True,
    dependencies=[Depends(current_superuser)],
)
async def get_all_donations(
        session: AsyncSession = Depends(get_async_session),
):
    all_donations = await donation_crud.get_multi(session)
    return all_donations


@router.post(
    '/',
    response_model=DonationDBCustomUser,
    response_model_exclude_none=True,
)
async def create_donation(
        donation: DonationBase,
        session: AsyncSession = Depends(get_async_session),
        user: User = Depends(current_user),
):

    new_donation = await donation_crud.create(
        donation, session, user
    )
    return new_donation


@router.get(
    '/my',
    response_model=List[DonationDBCustomUser],
    response_model_exclude={'user_id'},
)
async def get_user_donations(
        session: AsyncSession = Depends(get_async_session),
        user: User = Depends(current_user),
):
    """Получает список всех пожертвований для текущего пользователя."""
    donations = await donation_crud.get_by_user(
        session=session, user=user
    )
    return donations
