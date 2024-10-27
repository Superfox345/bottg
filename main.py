import asyncio
from tortoise.models import Model
from tortoise import fields
from tortoise import Tortoise, run_async 
from config import host, user, password, port, token
import psycopg2
from psycopg2 import Error
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import logging
from aiogram import Bot, Dispatcher, types, Router, F
from aiogram.filters.command import Command
from aiogram.filters import CommandStart , Command
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
try:
    # Подключение к существующей базе данных
    connection = psycopg2.connect(user=user,
                                  password=password,
                                  host=host,
                                  port=port)
    print("[INFO]:PostreSQL connected")
    
    curs = connection.cursor()
    curs.execute("SELECT version();")     
        
    print(f"Version is: {curs.fetchone()}")
 #   curs.execute("""INSERT INTO public."Userdata"(id, first_name) VALUES
 #                ('123', 'lox')""")
   # connection.commit()

except Exception as _ex:
    print("[ERROR]: Can't connect", _ex)
finally:
   # curs.close
   # connection.close()
    print("[INFO]: PostreSQL connection is closed")


     
# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO)
# Объект бота
bot = Bot(token=token)
# Диспетчер
dp = Dispatcher()
router = Router()


class Reg(StatesGroup):
    name = State()
    gift = State()

# Хэндлер на команду /start

@router.message(Command("start"))

async def cmd_start(message: types.Message):
    fn = message.from_user.first_name
    try:
        id = message.from_user.id
        print(id)
        await message.answer(f"{message.from_user.first_name},Привет, это бот для тайного санты!")
        data = (id, fn)
        curs.execute("""INSERT INTO public."Userdata"(id, first_name) VALUES(%s, %s);""",(id, fn))
        connection.commit()
        
    except:
        print('Error')
# Запуск процесса поллинга новых апдейтов


@router.message(Command('Reg'))
async def reg_one(message: Message, state: FSMContext):
    await state.set_state(Reg.name)
    await message.answer('Введите Ваше имя')

@router.message(Reg.name)
async def reg_two(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(Reg.gift)
    await message.answer('Введите подарок')

@router.message(Reg.gift)
async def two_three(message: Message, state: FSMContext):
    await state.update_data(gift=message.text)
    data = await state.get_data()
    await message.answer(f'{data["name"]} \t {data["gift"]}')
    await state.clear()

async def main():
    dp.include_routers(router)
    await dp.start_polling(bot)

if __name__ == "__main__":
   asyncio.run(main())