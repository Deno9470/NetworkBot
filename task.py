
from aiogram.dispatcher.filters.state import StatesGroup, State

class Task(StatesGroup):
  Small_IP = State()
  Small_Mask = State()
  IP = State()
  Mask = State() 
  PC = State()
  Submit = State()