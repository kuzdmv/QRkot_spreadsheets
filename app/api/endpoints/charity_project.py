from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.crud.charity_project import charityproject_crud
from app.api.validators import (
    check_charityproject_exists,
    check_charityproject_ammount,
    check_charityproject_invested_ammount,
    check_name_duplicate,
    check_charityproject_fully_invested
)
from app.schemas.charity_project import (
    CharityProjectCreate,
    CharityProjectUpdate,
    CharityProjectDB
)
from app.core.user import current_superuser


router = APIRouter()


@router.post(
    '/',
    response_model=CharityProjectDB,
    response_model_exclude_none=True,
    dependencies=[Depends(current_superuser)],
)
async def create_charity_project(
        charityproject: CharityProjectCreate,
        session: AsyncSession = Depends(get_async_session),
):
    """
    Только для суперюзеров.
    Создает благотворительный проект.
    """
    await check_name_duplicate(charityproject.name, session)
    new_project = await charityproject_crud.create(charityproject, session)
    return new_project


@router.get(
    '/',
    response_model=List[CharityProjectDB],
    response_model_exclude_none=True,
)
async def get_all_charity_projects(
        session: AsyncSession = Depends(get_async_session),
):
    """Получает список всех проектов."""
    all_project = await charityproject_crud.get_multi(session)
    return all_project


@router.patch(
    '/{project_id}',
    response_model=CharityProjectDB,
    dependencies=[Depends(current_superuser)],
)
async def update_charity_project(
        project_id: int,
        obj_in: CharityProjectUpdate,
        session: AsyncSession = Depends(get_async_session),
):
    """Только для суперюзеров.
    Закрытый проект нельзя редактировать,
    также нельзя установить требуемую сумму меньше уже вложенной.
    """
    charityproject = await check_charityproject_exists(
        project_id, session
    )
    await check_charityproject_fully_invested(charityproject)
    if obj_in.name is not None:
        await check_name_duplicate(obj_in.name, session)
    if obj_in.full_amount is not None:
        await check_charityproject_ammount(obj_in.full_amount, charityproject)
    charityproject = await charityproject_crud.update(
        charityproject, obj_in, session
    )
    return charityproject


@router.delete(
    '/{project_id}',
    response_model=CharityProjectDB,
    dependencies=[Depends(current_superuser)],
)
async def delete_charity_project(
        project_id: int,
        session: AsyncSession = Depends(get_async_session),
):
    """Только для суперюзеров.
    Удаляет проект.
    Нельзя удалить проект, в который уже были инвестированы средства,
    его можно только закрыть.
    """
    charityproject = await check_charityproject_exists(
        project_id, session
    )
    await check_charityproject_invested_ammount(charityproject)
    charityproject = await charityproject_crud.remove(charityproject, session)
    return charityproject
