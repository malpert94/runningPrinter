# runningPrinter
Stores the current version of working code for the printer and sample code for use in final code


decArrayProd.py still needs some work to adjust the length for the distance dictated in the command. It contains the functions necassary for producing the decimal array for printing, only one function needs to be called though.

dAPtest.py calls decArrayProd.py and shift.py to create the decimal array for printing then prints the result one element at a time

shift.py contains the code to shift each decimal element into the 74HC595 shift register and the GPIO declarations for the shift register. It also contains the function for printing each element in a series of three quick droplets.
