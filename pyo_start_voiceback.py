import pyo
from pyo import Tone
from pyo import Atone

s=pyo.Server().boot()
s.start()
i = pyo.Input()
low_filter = Tone(i, freq=280, mul=1, add=0)
high_filter = Atone(low_filter, freq=4000, mul=1, add=0).out()
