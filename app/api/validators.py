from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.charity_project import charityproject_crud
from app.models.charity_project import CharityProject


async def check_name_duplicate(
        project_name: str,
        session: AsyncSession,
) -> None:
    project_id = await charityproject_crud.get_project_id_by_name(
        project_name, session
    )
    if project_id is not None:
        raise HTTPException(
            status_code=400,
            detail='Проект с таким именем уже существует!'
        )


async def check_charityproject_exists(
        project_id: int,
        session: AsyncSession,
) -> CharityProject:
    charityproject = await charityproject_crud.get(project_id, session)
    if charityproject is None:
        raise HTTPException(
            status_code=422,
            detail='Такого проекта нет'
        )
    return charityproject


async def check_charityproject_ammount(
        ammount: int,
        charityproject: CharityProject,
) -> CharityProject:
    invested = charityproject.invested_amount
    if ammount < invested:
        raise HTTPException(
            status_code=400,
            detail='Нельзя установить требуемую сумму меньше уже вложенной'
        )
    return charityproject


async def check_charityproject_fully_invested(
        charityproject: CharityProject,
) -> CharityProject:
    if charityproject.fully_invested:
        raise HTTPException(
            status_code=400,
            detail='Закрытый проект нельзя редактировать!'
        )
    return charityproject


async def check_charityproject_invested_ammount(
        charityproject: CharityProject,
) -> None:
    invested = charityproject.invested_amount
    if invested > 0:
        raise HTTPException(
            status_code=400,
            detail='В проект были внесены средства, не подлежит удалению!'
        )
