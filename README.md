# Corona-Leaking-Testing-Project
Air Testing Device Software 
#This Project Work on Python (PYQT5) also project run on raspberry pi 3B
#Corona Leaking Testing Project 2 ADS use one For AIR filling and second for Testing 

MODFET = RELAY5, RELAY6, RELAY7, RELAY8  ()

RELAY_PIN5 =12  # GPIO pin where relay is connected
RELAY_PIN6 =16  # GPIO pin where relay is connected
RELAY_PIN7 =20  # GPIO pin where relay is connected
RELAY_PIN8 =21


RELAY = RELAY1, RELAY2, RELAY3, RELAY4

RELAY_PIN1 =22  # GPIO pin where relay is connected
RELAY_PIN2 =27  # GPIO pin where relay is connected
RELAY_PIN3 =17  # GPIO pin where relay is connected
RELAY_PIN4 =4 


INPUT = 19, 13, 6, 5, 9, 10  B1 B2 B3 B4 START STOP 

#TESTING START - RELAY ON OFF CONDITIONS

INI = 		RELAY1 ON
FILLING =	RELAY2 ON - RELAY1 OFF
STAB = 		RELAY3 ON - RELAY2 OFF
TESTING =	RELAY4 ON - RELAY3 OFF
RESULT = 

#RESULT SHOW RELAY ON CONDITION

PART REJECT = RELAY7 ON
PART OK =	RELAY6 ON
PRESURE LOW = RELAY5 ON
PRESURE HIGH = RELAY8 ON



#ADS value calculation channel1 ADS 1 value , 3

MV1 = (channel1.voltage * 1000) - 800
PA = (2000/3200 * MV1)- 1000
#print("MV " + str(MV) + "  MV1 " + str(MV1) + "  PA " + str(1000/3200 * MV1))

self.Program_MSg.setText("MV " + str(MV) + "  MV1 " + str(MV1) + "  PA " + str(PA))


#calibration Part
MV = (channel1.voltage * 1000) - 800
#print("MileAmp "+ str(((MV/3200) * (int(S1)+int(E1))) -int(E1)))
