import os
import json

import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from task import Task 
from utils import is_IpMaskValid, networksIpCounter, smallIpInfo ,statCollector, consructLog

logging.basicConfig(level=logging.INFO)
bot = Bot(token=os.getenv("TOKEN"))
dp = Dispatcher(bot, storage=MemoryStorage())


@dp.message_handler(commands=["start"])
async def cmd_start(message: types.Message):
    await message.answer("Привет! Этот бот умеет решать задачи \n из упражнения главы Обзор стека TCP/IP.", reply_markup=types.ReplyKeyboardRemove())
    await message.answer("Всего доступно два вида задания. В первом указан только IP-адрес и битность маски, во втором еще указано количество компьютеров и прикреплен файл с текстовым описанием")
    with open("users.txt", "a") as fp:
      json.dump(str(message.date) + " " +str(message.from_user.username) , fp)
      fp.write("\n")
    kb = [
      [
        types.KeyboardButton(text="Первый тип"),
        types.KeyboardButton(text="Второй тип")
      ],
    ]
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        input_field_placeholder="Какое задание надо решить"
    )
    await message.answer("Выбери какое задание надо решить?", reply_markup=keyboard)


@dp.message_handler(commands=["solution"])
async def solution_handler(message: types.Message):
    await message.answer("Всего доступно два вида задания. В первом указан только IP-адрес и битность маски, во втором еще указано количество компьютеров и прикреплен файл с текстовым описанием")
    with open("users.txt", "a") as fp:
      json.dump(str(message.date) + " " +str(message.from_user.username) , fp)
      fp.write("\n")
    kb = [
      [
        types.KeyboardButton(text="Первый тип"),
        types.KeyboardButton(text="Второй тип")
      ],
    ]
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        input_field_placeholder="Какое задание надо решить"
    )
    await message.answer("Выбери какое задание надо решить?", reply_markup=keyboard)


@dp.message_handler(state='*', commands='cancel')
async def cancel_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    logging.info('Cancelling state %r', current_state)
    await state.finish()
    await message.answer('Ввод отменен', reply_markup=types.ReplyKeyboardRemove())


@dp.message_handler(text=["Первый тип"])
async def solution_small_start(message: types.Message):
    await message.answer("Итак условие состоит из 2 строк: IP-адрес, битность маски", reply_markup=types.ReplyKeyboardRemove())
    await Task.Small_IP.set()
    await message.answer("Для начала отдельной строкой введи <b><i>IP-адрес из сети</i></b>\n<i>Например:</i> <code>192.168.244.161</code>", parse_mode="HTML")


@dp.message_handler(lambda message: not is_IpMaskValid(ip = message.text), state=Task.Small_IP)
async def process_sm_ip_invalid(message: types.Message):
    return await message.answer("Ip-адрес должен быть в формате 4 чисел (0-255) разделенных точкой \n<i>Например:</i> <code>192.168.244.161</code>", parse_mode="HTML")


@dp.message_handler(state=Task.Small_IP)
async def process_sm_ip(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['Small_IP'] = message.text
    await message.answer("Скольки битная <b><i>Маска</i></b> указана в задании?\n<i>Например:</i> <code>28</code> ", parse_mode="HTML")
    await Task.next()


@dp.message_handler(lambda message: not is_IpMaskValid(mask = message.text), state=Task.Small_Mask)
async def process_sm_mask_invalid(message: types.Message):
    return await message.answer("Маска должна состоять из одного числа - количества единиц в маске", parse_mode="HTML")
  

@dp.message_handler(state=Task.Small_Mask)
async def process_sm_mask(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['Small_Mask'] = message.text
    #await message.answer("", parse_mode="HTML")
    info = smallIpInfo(data['Small_IP'], data['Small_Mask'])
    await message.answer("Маска в двоичном формате")
    await message.answer(info[0])
    await message.answer("IP адрес сети в десятичном формате")
    await message.answer(info[1].exploded)
    await message.answer("IP адрес широковещания в десятичном формате:")
    await message.answer(info[2].exploded)
    await message.answer("Начало диапазона IP-адресов для узлов в десятичном формате")
    await message.answer(info[3].exploded)
    await message.answer("Окончание диапазона IP-адресов для узлов в десятичном формате")
    await message.answer(info[4].exploded)  
    await message.answer("Максимальное количество узлов в данной сети")
    await message.answer(info[5]) 
    await state.finish()
    #await Task.next()
  

@dp.message_handler(text=["Второй тип"])
async def solution_start(message: types.Message):
    await message.answer("Итак условие состоит из 3 строк: IP-адрес, маска, количество компьютеров в сети", reply_markup=types.ReplyKeyboardRemove())
    await Task.IP.set()
    await message.answer("Для начала отдельной строкой введи <b><i>IP-адрес из сети</i></b>\n<i>Например:</i> <code>10.12.12.15</code>", parse_mode="HTML")


@dp.message_handler(lambda message: not is_IpMaskValid(ip = message.text), state=Task.IP)
async def process_ip_invalid(message: types.Message):
    return await message.answer("Ip-адрес должен быть в формате 4 чисел (0-255) разделенных точкой \n<i>Например:</i> <code>10.12.12.15</code>", parse_mode="HTML")


@dp.message_handler(state=Task.IP)
async def process_ip(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['IP'] = message.text
    await message.answer("Теперь введи <b><i>Маску</i></b>\n<i>Например:</i> <code>255.255.254.0</code> ", parse_mode="HTML")
    await Task.next()


@dp.message_handler(lambda message: not is_IpMaskValid(mask = message.text), state=Task.Mask)
async def process_mask_invalid(message: types.Message):
    return await message.answer("Маска должна быть в формате 4 чисел (0-255) разделенных точкой \n<i>Например:</i> <code>255.255.254.0</code>", parse_mode="HTML")
  

@dp.message_handler(state=Task.Mask)
async def process_mask(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['Mask'] = message.text
    await message.answer("Теперь введи <b><i>Количество компьютеров в сети</i></b> том же порядке что и в задании через пробел \n<i>Например:</i> <code>25 16 240 117 1</code> ", parse_mode="HTML")
    await Task.next()


@dp.message_handler(lambda message: len(list(message.text.split())) != 5  , state=Task.PC)
async def process_pc_invalid(message: types.Message):
    return await message.answer("Количество компьютеров это строка из 5 чисел, разделенных пробелом", parse_mode="HTML")
  
@dp.message_handler(state=Task.PC)
async def process_pc(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['PC'] = message.text
    try: 
      networks = networksIpCounter(data['IP'], data['Mask'], data['PC'])
    except Exception:
      await message.answer("При вычислении произошла ошибка, проверь введенные данные. Если ошибки нет, к сожалению, я не смогу решить такую задачу")
      async with state.proxy() as info:
        error_data = info.as_dict()
      error_data["Username"] = message.from_user.mention
      error_data["Time"] = str(message.date)
      with open("errors.txt", "a") as fp:
        json.dump(error_data , fp)
        fp.write("\n")
      await bot.send_message(os.getenv("Admin_id"), "ALARM {} Пользователь {} вызвал ошибку вычисления ".format(error_data["Time"], error_data["Username"]))
      await cancel_handler(message, state)
    for network in sorted(networks.items()):
      await message.answer(str(network[1][0].exploded)+" "+ str(network[1][1].exploded))
      
    await message.answer("Вводить ответ на сайте можно копируя строки целиком")
    kb = [
      [
        types.KeyboardButton(text="Все правильно"),
        types.KeyboardButton(text="Что-то не так...")
      ],
    ]
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        input_field_placeholder="Ответ полностью правильный"
    )
    await message.answer("Ответ полностью правильный?", reply_markup=keyboard)
    async with state.proxy() as info:
      incopml_data = info.as_dict()
    incopml_data["Username"] = message.from_user.mention
    incopml_data["Correct"] = "Unknown"
    incopml_data["Time"] = str(message.date)
    with open("midterm.txt", "a") as fp:
      json.dump(incopml_data , fp)
      fp.write("\n")
    await Task.next()

   
@dp.message_handler(text=["Все правильно"], state=Task.Submit)
async def process_correct(message: types.Message, state: FSMContext):
    await message.answer("Рад был помочь! Хорошего дня!", reply_markup=types.ReplyKeyboardRemove())
    async with state.proxy() as info:
      data = info.as_dict()
    data["Username"] = message.from_user.mention
    data["Correct"] = "True"
    data["Time"] = str(message.date)
    with open("storage.txt", "a") as fp:
      json.dump(data , fp)
      fp.write("\n")
    await state.finish()


@dp.message_handler(text=["Что-то не так..."], state=Task.Submit)
async def proccess_error(message: types.Message, state: FSMContext):
    await message.answer("Такого явно не должно быть, информация уже передана разработчику, приношу извинения за неудобства", reply_markup=types.ReplyKeyboardRemove())
    async with state.proxy() as info:
      data = info.as_dict()
    data["Username"] = message.from_user.mention
    data["Correct"] = "False"
    data["Time"] = str(message.date)
    with open("storage.txt", "a") as fp:
      json.dump(data , fp)
      fp.write("\n")
    await state.finish()
    await bot.send_message(os.getenv("Admin_id"), "ALARM {} Пользователь {} прожал кнопку 'Что-то не так..' ".format(data["Time"], data["Username"]))


@dp.message_handler(commands=["help"])
async def solution_help(message: types.Message):
    await message.answer("Бот умеет решать задачи главы Обзор стека TCP/IP курса Основы Сетевых Технологий")
    await message.answer("Для начала выбора задачи пропиши /solution")

@dp.message_handler(lambda message: message.from_user.id == int(os.getenv("Admin_id")) and message.text == "/status")
async def proccess_status(message: types.Message):
  stats = statCollector()
  await message.answer("Всего решено {} задач: {} успешно {} нет из них уникальных {} ".format(stats[2], stats[0], stats[1], stats[3]))


@dp.message_handler(lambda message: message.from_user.id == int(os.getenv("Admin_id")) and message.text == "/getlogs")
async def proccess_getlogs(message: types.Message):
  file_list = ["users.txt", "errors.txt","midterm.txt", "storage.txt"]
  for file in file_list:
    file_сontent = "Content of {}\n".format(file) + consructLog(file)
    await message.answer(file_сontent)

@dp.message_handler()
async def unknonw_command(message: types.Message):
    await message.answer("Команда не известна, справку можно получить прописав /help, чтобы перейти к решению пропиши /solution")
    
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())