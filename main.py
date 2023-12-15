import _thread
from Core0 import Core0
from Core1 import Core1

core1 = Core1()
_thread.start_new_thread(core1.run, ())

core0 = Core0()
core0.run()