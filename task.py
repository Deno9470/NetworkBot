
from aiogram.dispatcher.filters.state import StatesGroup, State

class Task(StatesGroup):
  IP = State()
  Mask = State() 
  PC = State()
  Submit = State()