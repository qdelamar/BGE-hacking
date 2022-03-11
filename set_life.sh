#set jade's current life as a float, half heart=40 (eg 10 hearts=800)

sudo gdb -p $(pidof bge.exe) --batch-silent -ex "set *(float*)0x12a4120=(float)$1" -ex 'q'
