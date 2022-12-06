from datetime import datetime

from typing import Optional

from pydantic import BaseModel, Extra, PositiveInt


class DonationBase(BaseModel):
    comment: Optional[str]
    full_amount: PositiveInt

    class Config:
        extra = Extra.forbid


class DonationDBCustomUser(DonationBase):
    id: int
    create_date: datetime

    class Config:
        orm_mode = True


class DonationDBSuperUser(DonationDBCustomUser):
    invested_amount: int
    fully_invested: bool
    close_date: Optional[datetime]
    user_id: int
