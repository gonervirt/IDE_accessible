#hardware platform:FireBeetle-ESP32
f.write("HelloWord!!!")             #write "HelloWord!!!" to the file
f.close()                           #close file

f=open("sd/HelloWord.txt","r")      #open file 'HelloWord.txt' in sdcard 
f.close()