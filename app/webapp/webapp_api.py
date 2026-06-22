from fastapi import FastAPI

from sqlalchemy import select
from sqlalchemy import delete
from sqlalchemy import update

from app.database.database import async_session
from app.database.models.deposit import Deposit

from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from pydantic import BaseModel

from contextlib import asynccontextmanager

from app.database.database import engine
from app.database.database import Base

@asynccontextmanager
async def lifespan(app):

    async with engine.begin() as conn:
        await conn.run_sync(
            Base.metadata.create_all
        )

    yield

app = FastAPI(
    lifespan=lifespan
)

app.mount(
    "/static",
    StaticFiles(directory="app/webapp/static"),
    name="static"
)

class DepositCreate(BaseModel):
    user_id: int
    bank: str
    deposit_name: str
    amount: float
    rate: float
    months: int
    capitalization: bool = False

@app.get("/")
async def index():
    return FileResponse(
        "app/webapp/static/index.html"
    )

@app.get("/api/deposits/{telegram_id}")
async def get_deposits(
        telegram_id: int
):

    async with async_session() as session:

        result = await session.execute(
            select(Deposit)
            .where(
                Deposit.user_id == telegram_id
            )
        )

        deposits = result.scalars().all()

        return [
            {
                "id": d.id,
                "bank": d.bank,
                "deposit_name": d.deposit_name,
                "amount": float(d.amount),
                "rate": float(d.rate),
                "months": d.months
            }
            for d in deposits
        ]


@app.get("/api/summary/{telegram_id}")
async def get_summary(telegram_id: int):

    async with async_session() as session:

        result = await session.execute(
            select(Deposit).where(
                Deposit.user_id == telegram_id
            )
        )

        deposits = result.scalars().all()

        total_amount = sum(
            float(dep.amount)
            for dep in deposits
        )

        total_income = 0

        for dep in deposits:
            total_income += (
                float(dep.amount)
                * float(dep.rate)
                / 100
            )

        return {
            "count": len(deposits),
            "total_amount": total_amount,
            "total_income": round(total_income, 2)
        }


@app.post("/api/deposits")
async def create_deposit(data: DepositCreate):

    async with async_session() as session:

        deposit = Deposit(
            user_id=data.user_id,
            bank=data.bank,
            deposit_name=data.deposit_name,
            amount=data.amount,
            rate=data.rate,
            months=data.months,
            capitalization=data.capitalization
        )

        session.add(deposit)

        await session.commit()
        await session.refresh(deposit)

        return {
            "success": True,
            "id": deposit.id
        }


@app.delete("/api/deposits/{deposit_id}")
async def delete_deposit(deposit_id: int):

    async with async_session() as session:

        await session.execute(
            delete(Deposit).where(
                Deposit.id == deposit_id
            )
        )

        await session.commit()

        return {
            "success": True
        }


@app.put("/api/deposits/{deposit_id}")
async def update_deposit(
    deposit_id: int,
    data: DepositCreate
):

    async with async_session() as session:

        await session.execute(
            update(Deposit)
            .where(
                Deposit.id == deposit_id
            )
            .values(
                bank=data.bank,
                deposit_name=data.deposit_name,
                amount=data.amount,
                rate=data.rate,
                months=data.months,
                capitalization=data.capitalization
            )
        )

        await session.commit()

        return {
            "success": True
        }


@app.get("/api/deposit/{deposit_id}")
async def get_deposit(
    deposit_id: int
):

    async with async_session() as session:

        deposit = await session.get(
            Deposit,
            deposit_id
        )

        if not deposit:
            return {
                "success": False
            }

        return {
            "id": deposit.id,
            "bank": deposit.bank,
            "deposit_name": deposit.deposit_name,
            "amount": float(deposit.amount),
            "rate": float(deposit.rate),
            "months": deposit.months,
            "capitalization": deposit.capitalization
        }