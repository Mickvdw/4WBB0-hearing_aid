import pyo                                                      #importing the library
from pyo import Tone                                            #importing the low frequency filter
from pyo import Atone                                           #importing the high frequency filter

s=pyo.Server().boot()                                           #declaring the server variable
s.start()                                                       #Starting the Pyo Server
i = pyo.Input()                                                 #declaring the input
low_filter = Tone(i, freq=280, mul=1, add=0)                    #setting the lowest frequency to 280 Hz
high_filter = Atone(low_filter, freq=4000, mul=1, add=0).out()  #setting the highest fre to 4000 Hz

#source: http://ajaxsoundstudio.com/pyodoc/api/classes/filters.html
