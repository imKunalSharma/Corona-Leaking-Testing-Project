import subprocess # for user (root) GPIO Permission 
command = "sudo usermod -a -G gpio root; sudo chown root.gpio /dev/gpiomem; sudo chmod g+rw /dev/gpiomem"
subprocess.run(command, shell=True, capture_output=True, text=True, check=True)

import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QAction, QToolBar, QLabel, QPushButton, QStackedWidget, \
     QWidget,QGridLayout, QVBoxLayout, QLineEdit, QPushButton, QComboBox, QTableWidget, QStatusBar
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QStatusBar, QLabel, QVBoxLayout, QWidget
from PyQt5.QtCore import QSize,Qt
from PyQt5.QtGui import QCloseEvent, QFont, QPixmap, QPainter, QPen, QColor, QImage, QPalette, QBrush, QPolygon
from PyQt5.QtCore import QRegExp,pyqtSignal
from PyQt5.QtGui import QRegExpValidator
from PyQt5.QtCore import QTimer, QTime, Qt
from PyQt5 import QtCore
import sqlite3
from PyQt5.QtWidgets import *
import RPi.GPIO as GPIO
import os
import re
from PyQt5.QtCore import QDate


adc_available = False

try:
    import board
    import busio
    import adafruit_ads1x15.ads1115 as ADS
    from adafruit_ads1x15.analog_in import AnalogIn
    import subprocess

    i2c = busio.I2C(board.SCL, board.SDA)
    # Create an ADS1115 object
    ads = ADS.ADS1115(i2c)
    # Define the analog input channels
    channel0 = AnalogIn(ads, ADS.P0)
    channel1 = AnalogIn(ads, ADS.P1)
    channel2 = AnalogIn(ads, ADS.P2)
    channel3 = AnalogIn(ads, ADS.P3)
    
    adc_available = True
    
except Exception as e:
    adc_available = False
    print(adc_available)
action_home = ""

# Set up GPIO input pin
GPIO.setmode(GPIO.BCM)  # Use BCM pin numbering
RELAY_PIN1 =22  # GPIO pin where relay is connected
RELAY_PIN2 =27  # GPIO pin where relay is connected
RELAY_PIN3 =17  # GPIO pin where relay is connected
RELAY_PIN4 =4  # GPIO pin where relay is connected
GPIO.setup(RELAY_PIN1, GPIO.OUT)  # Set the relay pin as an output
GPIO.setup(RELAY_PIN2, GPIO.OUT)  # Set the relay pin as an output
GPIO.setup(RELAY_PIN3, GPIO.OUT)  # Set the relay pin as an output
GPIO.setup(RELAY_PIN4, GPIO.OUT)  # Set the relay pin as an output

#Mosfet
RELAY_PIN5 =12  # GPIO pin where relay is connected
RELAY_PIN6 =16  # GPIO pin where relay is connected
RELAY_PIN7 =20  # GPIO pin where relay is connected
RELAY_PIN8 =21 # GPIO pin where relay is connected
GPIO.setup(RELAY_PIN5, GPIO.OUT)  # Set the relay pin as an output
GPIO.setup(RELAY_PIN6, GPIO.OUT)  # Set the relay pin as an output
GPIO.setup(RELAY_PIN7, GPIO.OUT)  # Set the relay pin as an output
GPIO.setup(RELAY_PIN8, GPIO.OUT)  # Set the relay pin as an output
#LED
RELAY_PIN9 =24  # GPIO pin where relay is connected
RELAY_PIN10 =25  # GPIO pin where relay is connected
RELAY_PIN11 =8  # GPIO pin where relay is connected
RELAY_PIN12 =7 # GPIO pin where relay is connected
GPIO.setup(RELAY_PIN9, GPIO.OUT)  # Set the relay pin as an output
GPIO.setup(RELAY_PIN10, GPIO.OUT)  # Set the relay pin as an output
GPIO.setup(RELAY_PIN11, GPIO.OUT)  # Set the relay pin as an output
GPIO.setup(RELAY_PIN12, GPIO.OUT)  # Set the relay pin as an output

GPIO.output(RELAY_PIN1, GPIO.LOW)
GPIO.output(RELAY_PIN2, GPIO.LOW)
GPIO.output(RELAY_PIN3, GPIO.LOW)
GPIO.output(RELAY_PIN4, GPIO.LOW)
GPIO.output(RELAY_PIN5, GPIO.HIGH)
GPIO.output(RELAY_PIN6, GPIO.HIGH)
GPIO.output(RELAY_PIN7, GPIO.HIGH)
GPIO.output(RELAY_PIN8, GPIO.HIGH)
# GPIO.output(RELAY_PIN9, GPIO.HIGH)
# GPIO.output(RELAY_PIN10, GPIO.HIGH)
# GPIO.output(RELAY_PIN11, GPIO.HIGH)
# GPIO.output(RELAY_PIN12, GPIO.HIGH)


# Set up GPIO
pins = [19, 13, 6, 5, 9, 10]  # Example GPIO pin numbers output pin
#Start pin 9  Stop pin 10
GPIO.setmode(GPIO.BCM)  # Use BCM pin numbering
for pin in pins:
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)  # Set pins as input with pull-down resistors
        

PS = 0

TS = 0
TE = 0

#program selection pin 19, 13, 6. 5
INPUT_PINS = [19, 13, 6, 5] # Example pins for an 8-bit input
NUM_BITS = 4

def read_gpio_as_int():
    """Reads the state of all configured GPIO pins and converts to a single integer."""
    value = 0
    # Read pins from most significant bit to least significant bit
    for i, pin in enumerate(INPUT_PINS):
        if GPIO.input(pin) == GPIO.HIGH:
            # Set the corresponding bit in the integer
            # The left-most pin corresponds to the most significant bit
            value |= (1 << (NUM_BITS - 1 - i))
    return value

def reverse_bits(n, width):
    """Reverses the bits of an integer for a given width."""
    # Convert integer to a zero-padded binary string, reverse the string, and convert back to int
    binary_str = format(n, '0%db' % width)
    reversed_str = binary_str[::-1]
    reversed_int = int(reversed_str, 2)
    return reversed_int


#DataBase Connection string
connstring = "/home/admin/LeakageTesting/LeakageTesting.db"

def MyNonQuery(Query):
    conn = sqlite3.connect(connstring)
    cur = conn.cursor()
    cur.execute(Query)
    print("Record Insert - " + Query)
    conn.commit() 
    conn.close()
    

def getdata(Query):
    try:
        conn = sqlite3.connect(connstring)
        cursor = conn.cursor()
        cursor.execute(Query)
        #print(Query)
        users = cursor.fetchall()
        return users
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return []
    finally:
        if conn:
            conn.close()


            


def get_UNIT():  #A = V/R  and A*1000 = mA
    #resistance = 200 ohm and 4 to 20 mA
    # 200 * 4 = 800 and 200 * 20 = 4000 and 4000 - 800 = 3200
    SMin = 0
    SMax = 0
    MF = 0
    u = 0
    rows = getdata('Select * From Calibration Where "S1_Unit" = "Mbar"')
    for row in rows:
        SMin = row[0]
        SMax = row[1]
        MF = float(row[3])
        #print("Min " + str(SMin))
        #print("SMax " + str(SMax))
        #print("MF " + str(MF))
    if adc_available:
        MSG = 0
        V = round((channel0.voltage), 6)
        u = round(((V)*1000000), 3)
        #print("u"+str(u))
        MV = round(((V)*1000), 3)
        if MV > 800:
            MV = MV-800
            #print("Vlaue1 " + str(MV))
        else:
            MV = MV
            #print("Vlaue " + str(MV))
        if MF != 0 :
            MBar = round((((((float(SMin)) + (float(SMax)))/3200) * MV) - (float(SMin))), 3)
            MBar = round(((MBar) * (MF)), 3)
        else:
            MBar = round((((((float(SMin)) + (float(SMax)))/3200) * MV) - (float(SMin))), 3)
            
        
        #print(MBar)
        Bar = round(MBar * 0.001, 3)
        PSI = round((MBar * 0.0145), 3)
        
        return MSG, V, MV, MBar, Bar, PSI, u, SMin, SMax
        
    else:
        MSG = 1
        return MSG, 0, 0, 0, 0, 0, u, SMin, SMax
    

def get_UNIT2():  #A = V/R  and A*1000 = mA
    #resistance = 200 ohm and 4 to 20 mA
    # 200 * 4 = 800 and 200 * 20 = 4000 and 4000 - 800 = 3200
    SMin = 0
    SMax = 0
    MF = 0
    u = 0
    rows = getdata('Select * From Calibration Where "S2_Unit" = "PA"')
    for row in rows:
        SMin = row[4]
        SMax = row[5]
        MF = float(row[7])
        #print("Min 2" + str(SMin))
        #print("SMax " + str(SMax))
        #print("MF 2  " + str(MF))
    if adc_available:
        MSG = 0
        V = round((channel1.voltage), 6)
        u = round(((V)*1000000), 3)
        #print("u"+str(u))
        MV = round(((V)*1000), 3)
        
        #print(MV)
        if MV > 800:
            
            MV = MV-800
            #print("Vlaue1 " + str(MV))
        else:
            MV = MV
            
            #print("Vlaue " + str(MV))
        if MF != 0 :
            MBar = round(((((float(SMin) + float(SMax))/3200) * MV) - float(SMin)), 3)
            #print(MBar)
            MBar = round((MBar * MF), 3)
            #print("MBar 2" + str(MBar))
        else:
            MBar = round((((((float(SMin)) + abs(float(SMax)))/3200) * MV) - abs(float(SMin))), 3)
            #MBar = round((7000/3520) * (MV), 3)  #for 7000 bar sensor
            #print(MBar)
        #print(MBar)
        Bar = round(MBar * 0.001, 3)
        PSI = round((MBar * 0.0145), 3)
        
        return MSG, V, MV, MBar, Bar, PSI, u, SMin, SMax
        
    else:
        MSG = 1
        return MSG, 0, 0, 0, 0, 0, u, SMin, SMax
            
           
def get_Convert(value, Unit, time, vol): #"PA", "PA/Sec", "CC/Min"
    #print("" + str(value) + " " + str(Unit))
    if Unit == "PA": # 1 milebar to 100 PA
        return round(value * 100, 3)
    elif Unit == "PA/Sec":
        return round(((value * 100)/time), 3)
    elif Unit == "CC/Min":
        f = 0.0006 * vol * ((value * 100)/time)
        return round(f, 3)
    else:
        return 0
    

def check_textbox_value(val):
    try:
        # Attempt to convert the string to a float
        float_val = float(val)
        return "Float"
    except ValueError:
        # If a ValueError is raised, it is a non-numeric string
        return "String"


import csv
from datetime import datetime


def SaveReport(program_no, test_datetime, pressure, pressure_unit,
               leak, leak_unit, result):

    folder_path = "Reports/"

    # Create folder if it does not exist
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    # Today's CSV file
    current_date = datetime.now().strftime('%d-%m-%Y')
    filename = current_date + ".csv"
    full_file_path = os.path.join(folder_path, filename)

    # Default production count
    production_count = 1

    # Check existing file and get last ProductionCount
    if os.path.exists(full_file_path):

        try:
            with open(full_file_path, mode='r',
                      newline='', encoding='utf-8') as file:

                reader = csv.reader(file)
                rows = list(reader)

                if len(rows) > 1:
                    last_row = rows[-1]

                    if len(last_row) >= 8:
                        production_count = int(last_row[7]) + 1

        except Exception as ex:
            print("Error reading CSV:", ex)

    # Create new row
    new_row = [
        program_no,
        test_datetime,
        pressure,
        pressure_unit,
        leak,
        leak_unit,
        result,
        production_count
    ]

    # Check whether file already exists
    file_exists = os.path.exists(full_file_path)

    # Append data
    with open(full_file_path, mode='a',
              newline='', encoding='utf-8') as file:

        writer = csv.writer(file)

        # Write header for new file
        if not file_exists:
            writer.writerow([
                "ProgramNo",
                "TestDateTime",
                "Pressure",
                "PressureUnit",
                "Leak",
                "LeakUnit",
                "Result",
                "ProductionCount"
            ])

        # Write data
        writer.writerow(new_row)

    print("Data inserted into:", full_file_path)
    print("Production Count:", production_count)

    return production_count

    
    
    
file_path = "/home/admin/LeakageTesting/DB.txt"
if not os.path.exists(file_path):
    with open(file_path, 'x') as file:
        file.write("-1000\n")
        file.write("1000")

S1 = 0
E1 = 0
with open(file_path, 'r') as f:
    x = f.read().splitlines()
    
S1 = re.sub(r'[^a-zA-Z0-9]', '', x[0])
E1 = re.sub(r'[^a-zA-Z0-9]', '', x[1])

class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Dashboard Example")
        self.setGeometry(-5, 0, 1020, 600)

        # Main stacked widget
        self.stacked_widget = QStackedWidget()
        self.stacked_widget.setFixedHeight(560)
        self.setCentralWidget(self.stacked_widget)
        
        
        
        # Pages
        self.home_page = HomePage()
        self.home2_page = Home2Page()
        self.settings_page = SettingsPage()
        self.Calibration_page = CalibrationPage()
        self.Report_page = ReportPage()
        self.setup_page = LoginPage()
        self.about_page = AboutPage()
       # self.login_page = LoginPage()
        self.login_form_page = LoginFormPage()

        self.stacked_widget.addWidget(self.home2_page)
        self.stacked_widget.addWidget(self.home_page)
        
        self.stacked_widget.addWidget(self.settings_page)
        self.stacked_widget.addWidget(self.setup_page)
        self.stacked_widget.addWidget(self.Calibration_page)
        self.stacked_widget.addWidget(self.about_page)
        self.stacked_widget.addWidget(self.Report_page)
        self.stacked_widget.addWidget(self.login_form_page)
        
        
        
        self.login_form_page.login_successful.connect(self.on_login_success)

        # Toolbar
        self.toolbar = QToolBar("Main Toolbar")
        self.addToolBar(Qt.BottomToolBarArea, self.toolbar)
        
        

        # Toolbar actions
        self.action_home = QAction("Home", self)
        self.action_home.triggered.connect(self.show_home)
        
        self.action_home2 = QAction("Home2", self)
        self.action_home2.triggered.connect(self.show_home2)

        self.action_login = QAction("Login", self)
        self.action_login.triggered.connect(self.handle_login)

        self.action_logout = QAction("Logout", self)
        self.action_logout.triggered.connect(self.handle_logout)

        self.action_back = QAction("Back", self)
        self.action_back.triggered.connect(self.go_back_to_home)
        
        self.action_setup = QAction("Setup", self)
        self.action_setup.triggered.connect(self.show_setup)

        self.action_settings = QAction("Settings", self)
        self.action_settings.triggered.connect(self.show_settings)
        
        self.action_Calibration = QAction("Calibration", self)
        self.action_Calibration.triggered.connect(self.show_Calibration)
        

        self.action_about = QAction("About", self)
        self.action_about.triggered.connect(self.show_about)
        
        
        self.action_Report = QAction("Report", self)
        self.action_Report.triggered.connect(self.show_Report)
        
        

        self.action_exit = QAction("Exit", self)
        self.action_exit.triggered.connect(self.close)
        
        self.action_exit = QAction("Exit", self)
        self.action_exit.triggered.connect(self.close)

        # Initial toolbar setup
        self.setup_toolbar(home2=True, login=True)
        
        self.setup_page.switch_to_home.connect(self.show_home2)

        # Optional signal connection
        self.settings_page.select_clicked.connect(self.show_home2)

        # Show home page first
        self.show_home2()

    def setup_toolbar(self, home=False, home2=False, login=False,setup=False, logout=False,
                      back=False, settings=False, Calibration=False, Report=False, about=False, exit_app=False):
        self.toolbar.clear()
        

        if home:
            self.toolbar.addAction(self.action_home)
        
        if home2:
            self.toolbar.addAction(self.action_home2)

        if settings:
            self.toolbar.addAction(self.action_settings)
            
        if Calibration:
            self.toolbar.addAction(self.action_Calibration)
            
        if setup:
            self.toolbar.addAction(self.action_setup)
            
        if Report:
            self.toolbar.addAction(self.action_Report)
            
        if about:
            self.toolbar.addAction(self.action_about)
        if exit_app:
            self.toolbar.addAction(self.action_exit)
        

        # Spacer to push actions to the right
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.toolbar.addWidget(spacer)
        
        if back:
            self.toolbar.addAction(self.action_back)
        
        if login:
            self.toolbar.addAction(self.action_login)
        if logout:
            self.toolbar.addAction(self.action_logout)

    def show_home(self):
        self.stacked_widget.setCurrentWidget(self.home_page)
        
    def show_home2(self):
        self.stacked_widget.setCurrentWidget(self.home2_page)

    def show_settings(self):
        self.stacked_widget.setCurrentWidget(self.settings_page)
    
    def show_Calibration(self):
        self.stacked_widget.setCurrentWidget(self.Calibration_page)
        
    def show_Report(self):
        self.stacked_widget.setCurrentWidget(self.Report_page)

    def show_about(self):
        self.stacked_widget.setCurrentWidget(self.about_page)

    def handle_login(self):
        self.stacked_widget.setCurrentWidget(self.login_form_page)
        self.setup_toolbar(home2=True, back=True)

    def on_login_success(self):
        #self.stacked_widget.setCurrentWidget(self.login_page)
        self.stacked_widget.setCurrentWidget(self.setup_page)
        self.setup_toolbar(home=True, home2=True, settings=True, Calibration=True, Report=True, about=False, exit_app=False, logout=True, setup=True,)

    def handle_logout(self):
        self.stacked_widget.setCurrentWidget(self.home2_page)
        self.setup_toolbar(home2=True, login=True)

    def go_back_to_home(self):
        self.stacked_widget.setCurrentWidget(self.home2_page)
        self.setup_toolbar(home2=True, login=True)
        
    def show_setup(self):
        self.stacked_widget.setCurrentWidget(self.setup_page)
        
class LoginFormPage(QWidget):
    login_successful = pyqtSignal()

    def __init__(self):
        super().__init__()
        
        
        
        self.piclabel=QLabel("",self)
        self.piclabel.resize(200,60)
        self.piclabel.move(10,10)
        self.image = QImage("/home/admin/LeakageTesting/LOGO2.png")
        self.imagepix = QPixmap.fromImage(self.image)
        self.piclabel.setScaledContents(True)
        self.piclabel.setPixmap(self.imagepix)
        
        
        self.Live_LB = QLabel("LEAK TESTING SYSTEM", self)
        self.Live_LB.resize(1020,40)
        self.Live_LB.setAlignment(Qt.AlignCenter)
        self.Live_LB.setFont(QFont('Times', 30))
        self.Live_LB.setStyleSheet("color: Black; font-weight: bold;  ") # border: 1px solid black;")
        self.Live_LB.move(0, 20)
        
        self.style = "color: Black; font-weight: bold; " #  border: 1px solid black;"
        
        self.Program_lb = QLabel("Logn Page", self)
        self.Program_lb.resize(1020,180)
        self.Program_lb.setAlignment(Qt.AlignCenter)
        self.Program_lb.setFont(QFont('Times', 25))
        self.Program_lb.setStyleSheet(self.style)
        self.Program_lb.move(0, 80)
        
        
        #Timer for DateTime
        self.timer1 = QtCore.QTimer(self)
        self.timer1.setInterval(1000)
        self.timer1.timeout.connect(self.update_label1)
        self.timer1.start()
        
        self.Live_D = QLabel("", self)
        self.Live_D.setAlignment(Qt.AlignRight)
        self.Live_D.setFont(QFont('DS-Digital', 25))
        self.Live_D.setStyleSheet("color: Black; font-weight: bold;   ")# border: 1px solid black;")
        self.Live_D.move(830, 5)
        self.Live_D.resize(180,30)
        
        self.Live_T = QLabel(" ", self)
        self.Live_T.setAlignment(Qt.AlignRight)
        self.Live_T.setFont(QFont('DS-Digital', 25))
        self.Live_T.setStyleSheet("color: Black; font-weight: bold;  ")#  border: 1px solid black;")
        self.Live_T.move(830, 40)
        self.Live_T.resize(180,30)
        
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        

        self.username_input = QLineEdit("admin")
        self.username_input.setPlaceholderText("Username")
        self.username_input.setFixedWidth(300)

        self.password_input = QLineEdit("1234")
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setFixedWidth(300)

        self.submit_button = QPushButton("Submit")
        self.submit_button.setFixedWidth(140)
        self.submit_button.clicked.connect(self.check_login)

        layout.addSpacing(0)
        layout.addWidget(self.username_input)
        layout.addWidget(self.password_input)
        layout.addSpacing(20)
        layout.addWidget(self.submit_button)
        
        self.setLayout(layout)
        
        self.Key_btn = QPushButton('Open Keyword',self)
        self.Key_btn.resize(150,30)
        self.Key_btn.clicked.connect(self.Keybtn)
        self.Key_btn.setFont(QFont('Times', 12))
        #self.Key_btn.setStyleSheet("background-color : Green");
        self.Key_btn.move(520,312)

        
        
        
    def Keybtn(self) -> None:
        subprocess.Popen(["onboard"])
        
    def paintEvent(self, event):
        QMainWindow.paintEvent(self, event)
        
        painter = QPainter(self)
        #Top Header
        painter.setPen(QColor(255, 215, 0))
        painter.setBrush(QColor(255, 215, 0))
        painter.drawRect(0, 0, 1020, 80)  
        # TOP 1
        painter.setBrush(QColor(241, 249, 185))
        painter.setPen(QPen(Qt.black, 0.1, Qt.SolidLine))
        painter.drawRect(0, 80, 1020, 370)
        # TOP 2 
        painter.setPen(QPen(Qt.black, 0.1, Qt.SolidLine))
        painter.setPen(QColor(255, 215, 0))
        painter.setBrush(QColor(255, 215, 0))
        painter.drawRect(0, 420, 1020, 140)
        
    def update_label1(self):
        label_time = QtCore.QDateTime.currentDateTime().toString("hh:mm:ss") 
        label_Date = QtCore.QDateTime.currentDateTime().toString("dd-MM-yyyy")
        self.Live_D.setText(label_Date)
        self.Live_T.setText(label_time)

    def check_login(self):
        username = self.username_input.text()
        password = self.password_input.text()

        # Simple hardcoded validation (replace with real DB check as needed)
        if username == "admin" and password == "1234":
            print("Login successful!")
            self.login_successful.emit()
        else:
            QMessageBox.warning(self, "Login Failed", "Invalid username or password")
         
         
        self.username_input.clear()
        self.password_input.clear()
        
class LoginPage(QWidget):
    login_successful = pyqtSignal()
    switch_to_home = pyqtSignal()
    def __init__(self):
        super().__init__()
        
        self.piclabel=QLabel("",self)
        self.piclabel.resize(200,60)
        self.piclabel.move(20,10)
        self.image = QImage("/home/admin/LeakageTesting/LOGO2.png")
        self.imagepix = QPixmap.fromImage(self.image)
        self.piclabel.setScaledContents(True)
        self.piclabel.setPixmap(self.imagepix)
        
        
        self.Live_LB = QLabel("PROGRAMS", self)
        self.Live_LB.resize(1020,40)
        self.Live_LB.setAlignment(Qt.AlignCenter)
        self.Live_LB.setFont(QFont('Times', 30))
        self.Live_LB.setStyleSheet("color: Black; font-weight: bold;  ") # border: 1px solid black;")
        self.Live_LB.move(0, 5)
        
        
        self.checkbox = QCheckBox("Selector Swtich Bypass", self)
        self.checkbox.resize(400,30)
        self.checkbox.setFont(QFont('Times', 20))
        self.checkbox.setStyleSheet("color: Black; font-weight: bold;  ") # border: 1px solid black;")
        self.checkbox.move(350, 50)
        self.checkbox.stateChanged.connect(self.on_checkbox_change)
        
        self.style = "color: Black; font-weight: bold; " #  border: 1px solid black;"
        
        self.Live_D = QLabel("", self)
        self.Live_D.setAlignment(Qt.AlignRight)
        self.Live_D.setFont(QFont('DS-Digital', 25))
        self.Live_D.setStyleSheet("color: Black; font-weight: bold;   ")# border: 1px solid black;")
        self.Live_D.move(830, 5)
        self.Live_D.resize(180,30)
        
        self.Live_T = QLabel(" ", self)
        self.Live_T.setAlignment(Qt.AlignRight)
        self.Live_T.setFont(QFont('DS-Digital', 25))
        self.Live_T.setStyleSheet("color: Black; font-weight: bold;  ")#  border: 1px solid black;")
        self.Live_T.move(830, 40)
        self.Live_T.resize(180,30)
        
        
        # Main vertical layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 78, 0, 0)
        main_layout.setAlignment(Qt.AlignTop)
        
        

        # ---------- Group Box: Program Buttons ----------
        program_group = QGroupBox("")
        program_group.setFont(QFont('Times', 15, QFont.Bold))
        program_grid = QGridLayout()
        program_grid.setSpacing(15)

        self.buttons = []
        for i in range(16):
            btn = QPushButton(f"Program {i+1}")
            btn.setFixedSize(150, 60)
            btn.setFont(QFont('Times', 12, QFont.Bold))
            btn.clicked.connect(lambda _, b=i+1: self.on_button_click(b))
            self.buttons.append(btn)
            program_grid.addWidget(btn, i // 4, i % 4)

        program_group.setLayout(program_grid)
        main_layout.addWidget(program_group)

        # ---------- Group Box: Relay Control ----------
        
        relay_layout = QHBoxLayout()
        #relay_layout.setContentsMargins(0, 78, 0, 0)
        relay_layout.setAlignment(Qt.AlignTop)
        
        relay_group = QGroupBox("")
        relay_group.setFont(QFont('Times', 16, QFont.Bold))
        

        # Relay label
        #relay_label = QLabel("Relay Control- R1 - R4 \nMosfet - R5 - R8 \nLED - R9 - R12")
        relay_label = QLabel("Relay Control- R1 - R4 \nMosfet - R5 - R8")
        relay_label.setFont(QFont('Times', 12))
        relay_label.setAlignment(Qt.AlignLeft)
        relay_layout.addWidget(relay_label)
        
        
        self.relay_buttons = []
        for i in range(1, 9):
            relay_btn = QPushButton(f"R{i}")
            relay_btn.setFixedSize(55, 30)
            relay_btn.setFont(QFont('Times', 11, QFont.Bold))
            relay_btn.clicked.connect(lambda _, r=i: self.on_relay_click(r))
            self.relay_buttons.append(relay_btn)
            
            #self.relay_buttons[i - 1].setStyleSheet("background-color : Red");
            
            relay_layout.addWidget(relay_btn)
        
        
        if GPIO.input(RELAY_PIN1) == 1:
            self.relay_buttons[0].setStyleSheet("background-color : Red");
        elif GPIO.input(RELAY_PIN1) == 0:
            self.relay_buttons[0].setStyleSheet("background-color : Gray");
            
        if GPIO.input(RELAY_PIN2) == 1:
            self.relay_buttons[1].setStyleSheet("background-color : Red");
        elif GPIO.input(RELAY_PIN2) == 0:
            self.relay_buttons[1].setStyleSheet("background-color : Gray");
            
        if GPIO.input(RELAY_PIN3) == 1:
            self.relay_buttons[2].setStyleSheet("background-color : Red");
        elif GPIO.input(RELAY_PIN3) == 0:
            self.relay_buttons[2].setStyleSheet("background-color : Gray");
            
        if GPIO.input(RELAY_PIN4) == 1:
            self.relay_buttons[3].setStyleSheet("background-color : Red");
        elif GPIO.input(RELAY_PIN4) == 0:
            self.relay_buttons[3].setStyleSheet("background-color : Gray");
            
        if GPIO.input(RELAY_PIN5) == 0:
            self.relay_buttons[4].setStyleSheet("background-color : Red");
        elif GPIO.input(RELAY_PIN5) == 1:
            self.relay_buttons[4].setStyleSheet("background-color : Gray");
            
        if GPIO.input(RELAY_PIN6) == 0:
            self.relay_buttons[5].setStyleSheet("background-color : Red");
        elif GPIO.input(RELAY_PIN6) == 1:
            self.relay_buttons[5].setStyleSheet("background-color : Gray");
            
        if GPIO.input(RELAY_PIN7) == 0:
            self.relay_buttons[6].setStyleSheet("background-color : Red");
        elif GPIO.input(RELAY_PIN7) == 1:
            self.relay_buttons[6].setStyleSheet("background-color : Gray");
            
        if GPIO.input(RELAY_PIN8) == 0:
            self.relay_buttons[7].setStyleSheet("background-color : Red");
        elif GPIO.input(RELAY_PIN8) == 1:
            self.relay_buttons[7].setStyleSheet("background-color : Gray");
#             
#         if GPIO.input(RELAY_PIN9) == 0:
#             self.relay_buttons[8].setStyleSheet("background-color : Red");
#         elif GPIO.input(RELAY_PIN9) == 1:
#             self.relay_buttons[8].setStyleSheet("background-color : Gray");
#         
#         if GPIO.input(RELAY_PIN10) == 0:
#             self.relay_buttons[9].setStyleSheet("background-color : Red");
#         elif GPIO.input(RELAY_PIN10) == 1:
#             self.relay_buttons[9].setStyleSheet("background-color : Gray");
# 
#         if GPIO.input(RELAY_PIN11) == 0:
#             self.relay_buttons[10].setStyleSheet("background-color : Red");
#         elif GPIO.input(RELAY_PIN11) == 1:
#             self.relay_buttons[10].setStyleSheet("background-color : Gray");
# 
#         if GPIO.input(RELAY_PIN12) == 0:
#             self.relay_buttons[11].setStyleSheet("background-color : Red");
#         elif GPIO.input(RELAY_PIN12) == 1:
#             self.relay_buttons[11].setStyleSheet("background-color : Gray");
        relay_group.setLayout(relay_layout)
        main_layout.addWidget(relay_group)
        
        adc_group = QGroupBox("")
        adc_group.setFont(QFont('Times', 16, QFont.Bold))
        adc_layout = QHBoxLayout()

        adc_label = QLabel("ADS Status")
        adc_label.setFont(QFont('Times', 14))
        adc_label.setAlignment(Qt.AlignLeft)

        self.ADS_LB = QLabel("")
        self.ADS_LB.setFont(QFont('Times', 12))
        self.ADS_LB.setAlignment(Qt.AlignLeft)
        
        adc_layout.addWidget(adc_label)
        adc_layout.addWidget(self.ADS_LB)

        adc_group.setLayout(adc_layout)
        main_layout.addWidget(adc_group)

        self.setLayout(main_layout)
        
        
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000) # Update every 1000 ms (1 second)
        self.update_time()
        
        
        
    def paintEvent(self, event):
        QMainWindow.paintEvent(self, event)
        
        painter = QPainter(self)
        #Top Header
        painter.setPen(QColor(255, 215, 0))
        painter.setBrush(QColor(255, 215, 0))
        painter.drawRect(0, 0, 1020, 80)  
        # TOP 1
        painter.setBrush(QColor(241, 249, 185))
        painter.setPen(QPen(Qt.black, 0.1, Qt.SolidLine))
        painter.drawRect(0, 80, 1020, 315)
        # TOP 2 
        painter.setPen(QPen(Qt.black, 0.1, Qt.SolidLine))
        painter.setPen(QColor(255, 215, 0))
        painter.setBrush(QColor(255, 215, 0))
        painter.drawRect(0, 395, 1020, 165)
        
    def update_time(self):
        label_time = QtCore.QDateTime.currentDateTime().toString("hh:mm:ss") 
        label_Date = QtCore.QDateTime.currentDateTime().toString("dd-MM-yyyy")
        self.Live_D.setText(label_Date)
        self.Live_T.setText(label_time)
        if adc_available:
            v1 = "AV 0: " +  str(channel0.value) + "  V 0: " + str(channel0.voltage) + "   "
            v2 = "AV 1: " +  str( channel1.value) +  "  V 1: "+ str(channel1.voltage)+ "\n"
            v3 = "AV 2: " +  str( channel2.value) + "  V 2: " + str(channel2.voltage)+ "   "
            v4 = "AV 3: " +  str( channel3.value) + "  V 3: " + str(channel3.voltage)
            
            #self.ADS_LB.setText(str(v1) + str(v2) + str(v3) + str(v4))
            self.ADS_LB.setText(str(v1) + "\n" + str(v2))
        else:
            self.ADS_LB.setText("Error : ADC Harware not detected.")
            
        
        
        t1 = str(GPIO.input(19)) +  str(GPIO.input(13)) + str(GPIO.input(6))  + str(GPIO.input(5))
        #print(str(int(t1, 2)))
        global PS
        if PS == 1:
            self.checkbox.setStyleSheet("color: Green; font-weight: bold;  ")
            self.checkbox.setText("Selector Swtich Bypass Active")
            self.checkbox.setChecked(True)
        else:
            self.checkbox.setStyleSheet("color: Black; font-weight: bold;  ")
            self.checkbox.setText("Selector Swtich Bypass Disable")
            self.checkbox.setChecked(False)
        
    def on_checkbox_change(self, state):
        global PS
        if state == Qt.Checked:
            self.checkbox.setStyleSheet("color: Green; font-weight: bold;  ")
            self.checkbox.setText("Selector Swtich Bypass Active")
            PS = 1
        else:
            self.checkbox.setStyleSheet("color: Black; font-weight: bold;  ")
            self.checkbox.setText("Selector Swtich Bypass Disable")
            PS = 0
    
    def on_button_click(self, button_number):
        global PS
        if PS == 1:
            print("ByPass Active")
            #self.select1_clicked.emit()
            conn = sqlite3.connect(connstring)
            cur = conn.cursor()
            cur.execute('SELECT count(*) from Programs where ProgramNo = "' + str(button_number) + '"')
            result = cur.fetchone()
            row_count = result[0]
            #print("Number of rows in the table:", row_count)
            conn.commit()
            conn.close()
            if row_count == 1:
                
                for i in range(1, 16):
                    Query = 'UPDATE Programs SET "Set" = 0 Where "ProgramNo" =  "' + str(i) + '"'
                    MyNonQuery(Query)
                
                
                Query = 'UPDATE Programs SET "Set" = 1 Where "ProgramNo" =  "' + str(button_number) + '"'
                MyNonQuery(Query)
                
                self.switch_to_home.emit()
                
            else:
                #self.Status("Please Choice Program No")
                print("Please Choice Program No")
            
           
        if PS == 0:
            print("ByPass UNActive")
        
        
        
            
        
        
        

    def on_relay_click(self, relay_number):
        print(relay_number)
        if relay_number == 1:
            if GPIO.input(RELAY_PIN1) == 0:
                GPIO.output(RELAY_PIN1, GPIO.HIGH)
                self.relay_buttons[0].setStyleSheet("background-color : Red");
            elif GPIO.input(RELAY_PIN1) == 1:
                GPIO.output(RELAY_PIN1, GPIO.LOW)
                self.relay_buttons[0].setStyleSheet("background-color : Gray");
                
        if relay_number == 2:
            if GPIO.input(RELAY_PIN2) == 0:
                GPIO.output(RELAY_PIN2, GPIO.HIGH)
                self.relay_buttons[1].setStyleSheet("background-color : Red");
            elif GPIO.input(RELAY_PIN2) == 1:
                GPIO.output(RELAY_PIN2, GPIO.LOW)
                self.relay_buttons[1].setStyleSheet("background-color : Gray");
                
        if relay_number == 3:
            if GPIO.input(RELAY_PIN3) == 0:
                GPIO.output(RELAY_PIN3, GPIO.HIGH)
                self.relay_buttons[2].setStyleSheet("background-color : Red");
            elif GPIO.input(RELAY_PIN3) == 1:
                GPIO.output(RELAY_PIN3, GPIO.LOW)
                self.relay_buttons[2].setStyleSheet("background-color : Gray");
        if relay_number == 4:
            if GPIO.input(RELAY_PIN4) == 0:
                GPIO.output(RELAY_PIN4, GPIO.HIGH)
                self.relay_buttons[3].setStyleSheet("background-color : Red");
            elif GPIO.input(RELAY_PIN4) == 1:
                GPIO.output(RELAY_PIN4, GPIO.LOW)
                self.relay_buttons[3].setStyleSheet("background-color : Gray");
                
        if relay_number == 5:
            if GPIO.input(RELAY_PIN5) == 0:
                GPIO.output(RELAY_PIN5, GPIO.HIGH)
                self.relay_buttons[4].setStyleSheet("background-color : Gray");
            elif GPIO.input(RELAY_PIN5) == 1:
                GPIO.output(RELAY_PIN5, GPIO.LOW)
                self.relay_buttons[4].setStyleSheet("background-color : Red");
                
        if relay_number == 6:
            if GPIO.input(RELAY_PIN6) == 0:
                GPIO.output(RELAY_PIN6, GPIO.HIGH)
                self.relay_buttons[5].setStyleSheet("background-color : Gray");
            elif GPIO.input(RELAY_PIN6) == 1:
                GPIO.output(RELAY_PIN6, GPIO.LOW)
                self.relay_buttons[5].setStyleSheet("background-color : Red");
                
        if relay_number == 7:
            if GPIO.input(RELAY_PIN7) == 0:
                GPIO.output(RELAY_PIN7, GPIO.HIGH)
                self.relay_buttons[6].setStyleSheet("background-color : Gray");
            elif GPIO.input(RELAY_PIN7) == 1:
                GPIO.output(RELAY_PIN7, GPIO.LOW)
                self.relay_buttons[6].setStyleSheet("background-color : Red");
                
        if relay_number == 8:
            if GPIO.input(RELAY_PIN8) == 0:
                GPIO.output(RELAY_PIN8, GPIO.HIGH)
                self.relay_buttons[7].setStyleSheet("background-color : Gray");
            elif GPIO.input(RELAY_PIN8) == 1:
                GPIO.output(RELAY_PIN8, GPIO.LOW)
                self.relay_buttons[7].setStyleSheet("background-color : Red");
                
        if relay_number == 9:
            if GPIO.input(RELAY_PIN9) == 0:
                GPIO.output(RELAY_PIN9, GPIO.HIGH)
                self.relay_buttons[8].setStyleSheet("background-color : Gray");
            elif GPIO.input(RELAY_PIN9) == 1:
                GPIO.output(RELAY_PIN9, GPIO.LOW)
                self.relay_buttons[8].setStyleSheet("background-color : Red");
        if relay_number == 10:
            if GPIO.input(RELAY_PIN10) == 0:
                GPIO.output(RELAY_PIN10, GPIO.HIGH)
                self.relay_buttons[9].setStyleSheet("background-color : Gray");
            elif GPIO.input(RELAY_PIN10) == 1:
                GPIO.output(RELAY_PIN10, GPIO.LOW)
                self.relay_buttons[9].setStyleSheet("background-color : Yellow");
        if relay_number == 11:
            if GPIO.input(RELAY_PIN11) == 0:
                GPIO.output(RELAY_PIN11, GPIO.HIGH)
                self.relay_buttons[10].setStyleSheet("background-color : Gray");
            elif GPIO.input(RELAY_PIN11) == 1:
                GPIO.output(RELAY_PIN11, GPIO.LOW)
                self.relay_buttons[10].setStyleSheet("background-color : Green");
        if relay_number == 12:
            if GPIO.input(RELAY_PIN12) == 0:
                GPIO.output(RELAY_PIN12, GPIO.HIGH)
                self.relay_buttons[11].setStyleSheet("background-color : Gray");
            elif GPIO.input(RELAY_PIN12) == 1:
                GPIO.output(RELAY_PIN12, GPIO.LOW)
                self.relay_buttons[11].setStyleSheet("background-color : Blue");
class HomePage(QWidget):
    def __init__(self):
        super().__init__()
        
        self.piclabel=QLabel("",self)
        self.piclabel.resize(200,60)
        self.piclabel.move(20,10)
        self.image = QImage("/home/admin/LeakageTesting/LOGO2.png")
        self.imagepix = QPixmap.fromImage(self.image)
        self.piclabel.setScaledContents(True)
        self.piclabel.setPixmap(self.imagepix)
        
        
        self.Live_LB = QLabel("LEAK TESTING SYSTEM", self)
        self.Live_LB.resize(1020,40)
        self.Live_LB.setAlignment(Qt.AlignCenter)
        self.Live_LB.setFont(QFont('Times', 30))
        self.Live_LB.setStyleSheet("color: Black; font-weight: bold;  ") # border: 1px solid black;")
        self.Live_LB.move(0, 20)
        
        self.style = "color: Black; font-weight: bold; " #  border: 1px solid black;"
        
        self.Program_lb = QLabel("Program Name : ", self)
        self.Program_lb.resize(1020,35)
        self.Program_lb.setAlignment(Qt.AlignCenter)
        self.Program_lb.setFont(QFont('Times', 20))
        self.Program_lb.setStyleSheet(self.style)
        self.Program_lb.move(0, 80)
        
        self.Program_MSg = QLabel("", self)
        self.Program_MSg.resize(1020,35)
        self.Program_MSg.setAlignment(Qt.AlignCenter)
        self.Program_MSg.setFont(QFont('Times', 20))
        self.Program_MSg.setStyleSheet(self.style)
        self.Program_MSg.move(0, 120)
        
       
        
        self.Mode_lb = QLabel("Test Mode :", self)
        self.Mode_lb.resize(510,25)
        self.Mode_lb.setAlignment(Qt.AlignCenter)
        self.Mode_lb.setFont(QFont('Times', 15))
        self.Mode_lb.setStyleSheet(self.style)
        self.Mode_lb.move(0, 440)
        
        self.FillPressure_lb = QLabel('Fill Pressure :', self)
        self.FillPressure_lb.setStyleSheet(self.style)
        self.FillPressure_lb.setAlignment(Qt.AlignCenter)
        self.FillPressure_lb.setFont(QFont('Times', 15))
        self.FillPressure_lb.move(0, 470)
        self.FillPressure_lb.resize(510, 25)
        
        self.Leak_lb = QLabel('Leak :', self)
        self.Leak_lb.setStyleSheet(self.style)
        self.Leak_lb.setAlignment(Qt.AlignCenter)
        self.Leak_lb.setFont(QFont('Times', 15))
        self.Leak_lb.move(0, 500)
        self.Leak_lb.resize(510,25)
        
        self.PU_lb = QLabel('Pressure Unit :', self)
        self.PU_lb.setStyleSheet(self.style)
        self.PU_lb.setAlignment(Qt.AlignCenter)
        self.PU_lb.setFont(QFont('Times', 15))
        self.PU_lb.move(0, 530)
        self.PU_lb.resize(510,25)
        
        
        self.binary_str = ""
        
        self.flagstart = 0
        self.timer = QTimer(self)
        self.timer.start(1000)
        self.timer.timeout.connect(self.update_timer)
        
        self.remaining_time = 0
        self.totaltime = 0
        
        self.P1 = "Initialization"
        self.P2 = "Filling"
        self.P3 = "Stabilization"
        self.P4 = "Testing"
        self.P5 = "Release"
        
        self.P1_Ini = 0
        self.P2_Fill = 0
        self.P3_Stab = 0
        self.P4_Test = 0
        self.P5_Rel = 0
        self.delay = 0
        self.SetPressure = 0
        self.PressureMin = 0
        self.PressureMax = 0
        self.totaltime = 0
        self.TS = 0
        self.TE = 0
        
        self.SetTesting()
        
        self.ProcesLB2=QLabel("Process Total Time1 : " + str(self.totaltime/10) + " Sec ", self)
        #self.ProcesLB=QLabel("", self)
        self.ProcesLB2.setAlignment(Qt.AlignCenter)
        self.ProcesLB2.resize(510,30)
        self.ProcesLB2.setFont(QFont('Times', 15))
        self.ProcesLB2.setStyleSheet(self.style)
        self.ProcesLB2.move(510, 440)
        
        
        
        self.StartTime=QLabel("Time remaining: 0 SEC",self)
        self.StartTime.setAlignment(Qt.AlignRight)
        self.StartTime.resize(410,40)
        self.StartTime.setFont(QFont('Times', 20))
        self.StartTime.setStyleSheet(self.style)
        self.StartTime.move(510, 180)
        
        self.ProcesLB=QLabel("Process Name ",self)
        self.ProcesLB.setAlignment(Qt.AlignLeft)
        self.ProcesLB.resize(510,40)
        self.ProcesLB.setFont(QFont('Times', 20))
        self.ProcesLB.setStyleSheet(self.style)
        self.ProcesLB.move(100, 180)
        
        self.ProcesLB1=QLabel("",self)
        self.ProcesLB1.setAlignment(Qt.AlignCenter)
        self.ProcesLB1.resize(820,30)
        self.ProcesLB1.setFont(QFont('Times', 18))
        self.ProcesLB1.setStyleSheet(self.style)
        self.ProcesLB1.move(100, 220)
        
        self.label_B = QLabel('Part Number : ', self)
        self.label_B.setAlignment(Qt.AlignCenter)
        self.label_B.setFont(QFont('Times', 15))
        self.label_B.setStyleSheet(self.style)
        self.label_B.move(510,470)
        self.label_B.resize(510,30)
        
        self.label_B = QLabel('Production Count : ', self)
        self.label_B.setAlignment(Qt.AlignCenter)
        self.label_B.setFont(QFont('Times', 15))
        self.label_B.setStyleSheet(self.style)
        self.label_B.move(510, 500)
        self.label_B.resize(510,30)
        
        
        # Set up a timer for auto-refresh
        self.timer1 = QTimer(self)
        self.timer1.timeout.connect(self.update_gpio_states)
        self.timer1.start(1000)  # Refresh every 1000 milliseconds (1 second)
        
        self.Status1=QLabel("",self) #status gpio pin
        self.Status1.setAlignment(Qt.AlignCenter)
        self.Status1.resize(510,130)
        self.Status1.setFont(QFont('Times', 12))
        self.Status1.setStyleSheet(self.style)
        self.Status1.move(250, 425)
        
        #button#00cc66
        
        self.Start_btn = QPushButton('START',self)
        self.Start_btn.resize(150,50)
        self.Start_btn.clicked.connect(self.start_timer)
        self.Start_btn.setFont(QFont('Times', 20, QFont.Bold))
        self.Start_btn.setStyleSheet("background-color : #00331a;");
        self.Start_btn.move(320,340)


        self.Stop_btn = QPushButton('STOP',self)
        self.Stop_btn.resize(150,50)
        self.Stop_btn.clicked.connect(self.Stop)
        self.Stop_btn.setFont(QFont('Times', 20, QFont.Bold))
        self.Stop_btn.setStyleSheet("background-color : #330000");
        self.Stop_btn.move(560,340)
        
#         self.Login_btn = QPushButton('Login',self)
#         self.Login_btn.resize(120,40)
#         self.Login_btn.clicked.connect(self.Loginbtn)
#         self.Login_btn.setFont(QFont('Times', 15, QFont.Bold))
#         self.Login_btn.setStyleSheet("background-color : Gray;");
#         self.Login_btn.move(30,465)
        
        
        #print(self.totaltime)
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(int(self.totaltime))
        self.progress_bar.move(100, 250)
        self.progress_bar.resize(820,30)
        
        self.style1 = "background-color:black; color: white; font-weight: bold;   border: 1px solid black;"
        
        
        
        
        self.P1_LB=QLabel(self.P1 + str("\n") + str(self.P1_Ini * 1000),self)
        self.P1_LB.setAlignment(Qt.AlignCenter)
        self.P1_LB.setFont(QFont('Times', 12))
        self.P1_LB.setStyleSheet(self.style1)
        self.P1_LB.move(100, 280)
        self.P1_LB.resize(164, 40)
        
        
        
        self.P2_LB=QLabel(self.P2 + str("\n") + str(self.P2_Fill * 1000),self)
        self.P2_LB.setAlignment(Qt.AlignCenter)
        self.P2_LB.setFont(QFont('Times', 12))
        self.P2_LB.setStyleSheet(self.style1)
        self.P2_LB.move(264, 280)
        self.P2_LB.resize(164, 40)
        
        self.P3_LB=QLabel(self.P3 + str("\n") + str(self.P3_Stab * 1000),self)
        self.P3_LB.setAlignment(Qt.AlignCenter)
        self.P3_LB.setFont(QFont('Times', 12))
        self.P3_LB.setStyleSheet(self.style1)
        self.P3_LB.move(428, 280)
        self.P3_LB.resize(164, 40)
        
        self.P4_LB=QLabel(self.P4 + str("\n") + str(self.P4_Test * 1000),self)
        self.P4_LB.setAlignment(Qt.AlignCenter)
        self.P4_LB.setFont(QFont('Times', 12))
        self.P4_LB.setStyleSheet(self.style1)
        self.P4_LB.move(592, 280)
        self.P4_LB.resize(164, 40)
        
        self.P5_LB=QLabel(self.P5 + str("\n") + str(self.P5_Rel * 100),self)
        self.P5_LB.setAlignment(Qt.AlignCenter)
        self.P5_LB.setFont(QFont('Times', 12))
        self.P5_LB.setStyleSheet(self.style1)
        self.P5_LB.move(756, 280)
        self.P5_LB.resize(164, 40)
        
        
        
        #Timer for DateTime
        self.timer1 = QtCore.QTimer(self)
        self.timer1.setInterval(1000)
        self.timer1.timeout.connect(self.update_label1)
        self.timer1.start()
        
#         self.T1 = QtCore.QTimer(self)
#         self.T1.timeout.connect(self.T1_Start)
#         self.T2 = QtCore.QTimer(self)
#         self.T2.timeout.connect(self.T2_Start)
#         self.T3 = QtCore.QTimer(self)
#         self.T3.timeout.connect(self.T3_Start)
#         self.T4 = QtCore.QTimer(self)
#         self.T4.timeout.connect(self.T4_Start)
#         self.T5 = QtCore.QTimer(self)
#         self.T5.timeout.connect(self.T5_Start)
        
        self.Live_D = QLabel("", self)
        self.Live_D.setAlignment(Qt.AlignRight)
        self.Live_D.setFont(QFont('DS-Digital', 25))
        self.Live_D.setStyleSheet("color: Black; font-weight: bold;   ")# border: 1px solid black;")
        self.Live_D.move(830, 5)
        self.Live_D.resize(180,30)
        
        self.Live_T = QLabel(" ", self)
        self.Live_T.setAlignment(Qt.AlignRight)
        self.Live_T.setFont(QFont('DS-Digital', 25))
        self.Live_T.setStyleSheet("color: Black; font-weight: bold;  ")#  border: 1px solid black;")
        self.Live_T.move(830, 40)
        self.Live_T.resize(180,30)
        
        self.ADS_LB = QLabel("", self)
        self.ADS_LB.setAlignment(Qt.AlignLeft)
        self.ADS_LB.setFont(QFont('Times', 11))
        self.ADS_LB.setStyleSheet("color: Black; font-weight: bold;  ")#  border: 1px solid black;")
        self.ADS_LB.move(5, 400)
        self.ADS_LB.resize(200,200)
        
        self.ADS_LB2 = QLabel("", self)
        self.ADS_LB2.setAlignment(Qt.AlignRight)
        self.ADS_LB2.setFont(QFont('Times', 14))
        self.ADS_LB2.setStyleSheet("color: Black; font-weight: bold;  ")#  border: 1px solid black;")
        self.ADS_LB2.move(810, 400)
        self.ADS_LB2.resize(200,200)
        
        self.P_LB = QLabel("", self)
        self.P_LB.setAlignment(Qt.AlignLeft)
        self.P_LB.setFont(QFont('Times', 12))
        self.P_LB.setStyleSheet("color: Black; font-weight: bold;  ")#  border: 1px solid black;")
        self.P_LB.move(980, 80)
        self.P_LB.resize(200,200)
        
        self.TS_LB = QLabel("1", self)
        self.TS_LB.setAlignment(Qt.AlignLeft)
        self.TS_LB.setFont(QFont('Times', 12))
        self.TS_LB.setStyleSheet("color: Black; font-weight: bold;  ")#  border: 1px solid black;")
        self.TS_LB.move(950, 320)
        self.TS_LB.resize(200,200)
        
        self.TE_LB = QLabel("2", self)
        self.TE_LB.setAlignment(Qt.AlignLeft)
        self.TE_LB.setFont(QFont('Times', 12))
        self.TE_LB.setStyleSheet("color: Black; font-weight: bold;  ")#  border: 1px solid black;")
        self.TE_LB.move(950, 350)
        self.TE_LB.resize(200,200)
        
        
        store = get_UNIT() #value store
        store2 = get_UNIT2() #value store
        
        self.PMin_LB = QLabel(str(store[6]), self)
        self.PMin_LB.setAlignment(Qt.AlignLeft)
        self.PMin_LB.setFont(QFont('Times', 12))
        self.PMin_LB.setStyleSheet("color: white;font-weight: bold;")#  border: 1px solid black;")
        self.PMin_LB.move(5, 370)
        self.PMin_LB.resize(100,50)
        
        self.PMax_LB = QLabel(str(store[7]), self)
        self.PMax_LB.setAlignment(Qt.AlignRight)
        self.PMax_LB.setFont(QFont('Times', 12))
        self.PMax_LB.setStyleSheet("color: white; font-weight: bold;")#  border: 1px solid black;")
        self.PMax_LB.move(105, 370)
        self.PMax_LB.resize(100,50)
        
        
        self.P_progressBar = QProgressBar(self)
        self.P_progressBar.setMinimum(float(store[6]))  # Negative minimum
        self.P_progressBar.setMaximum(float(store[7]))   # Positive maximum
        self.P_progressBar.setValue(0)     # Start at 0
        self.P_progressBar.setFont(QFont('Times', 10))
        self.P_progressBar.setStyleSheet("color: black; font-weight: bold;")
        self.P_progressBar.setFormat('%v mbar')  # Shows e.g., "12 mA"
        self.P_progressBar.move(5, 390)
        self.P_progressBar.resize(200,20)
        #self.P_progressBar.setAlignment(Qt.AlignVCenter | Qt.AlignHCenter)
        #self.P_progressBar.setOrientation(QtCore.Qt.Vertical)
        
        
        self.Ptimer = QTimer()
        self.Ptimer.timeout.connect(self.updateProgress)
        self.Ptimer.start(100)  # Update every 100ms
        self.PcurrentValue = 0
        
        
        
        self.data1 = []
        self.setupEvents1()
        
        #self.ViewResult()
        
        self.DP_LB = QLabel("DP : ", self)
        self.DP_LB.setAlignment(Qt.AlignCenter)
        self.DP_LB.setFont(QFont('Times', 15))
        self.DP_LB.setStyleSheet("color: white; font-weight: bold;")#  border: 1px solid black;")
        self.DP_LB.move(400, 385)
        self.DP_LB.resize(300,50)
        
        self.DPtimer = QTimer()
        self.DPtimer.setInterval(100)
        self.DPtimer.timeout.connect(self.updateDP)
        
        self.DPC = 0
        self.TotalA = 0
        
        self.ProgramNo = "";
        self.PressureUnit = "";
        self.Pressure = ""
        self.Leak = ""
        self.LeakUnit = ""
        self.Result1 = ""
        self.ProductionCount  = 0
        self.ADS_AV = 0
        self.checkPro = 0
        self.volumn = 0
        self.TestDateTime = ""
        
        
        #self.Result()
        
        self.AllowLeakTest = 0
        self.AllowReffLeak = 0
        
        
        
        
        
        
    def paintEvent(self, event):
        QMainWindow.paintEvent(self, event)
        
        painter = QPainter(self)
        #Top Header
        painter.setPen(QColor(13, 152, 186))
        painter.setBrush(QColor(13, 152, 186))
        painter.drawRect(0, 0, 1020, 80)  
        #TOP 1
        painter.setBrush(QColor(0, 0, 208))
        painter.setPen(QPen(Qt.black, 0.1, Qt.SolidLine))
        painter.drawRect(0, 80, 1020, 370)
        #TOP 2 
        painter.setPen(QPen(Qt.black, 0.1, Qt.SolidLine))
        #painter.setPen(QColor(255, 215, 0))
        painter.setBrush(QColor(13, 152, 186))
        painter.drawRect(0, 420, 1020, 140)
        
        
       
        
        
    
        
    def updateProgress(self):
        
        
        store = get_UNIT()
        if get_UNIT()[0] == 1:
            self.ADS_LB.setText("Error : ADC Harware not detected.")
        else:
            self.PcurrentValue = get_UNIT()[3]
            self.P_progressBar.setValue(int(self.PcurrentValue))
            
            self.ADS_LB.setText(str("\n V : ") + str(get_UNIT()[1])
                                + str("\n MV : ") + str(get_UNIT()[2])
                                + str("\n MBAR : "+ str(get_UNIT()[3]))
                                + str("\n BAR : "+ str(get_UNIT()[4])
                                + str("\n PSI : "+ str(get_UNIT()[5]))
                                + str("\n Microvolt : ") + str(get_UNIT()[6])))
            
            self.ADS_LB2.setText(str("\n V : ") + str(get_UNIT2()[1])
                                + str("\n MV : ") + str(get_UNIT2()[2])
                                + str("\n MBAR : "+ str(get_UNIT2()[3]))
                                + str("\n BAR : "+ str(get_UNIT2()[4])
                                + str("\n PSI : "+ str(get_UNIT2()[5]))
                                + str("\n Microvolt : ") + str(get_UNIT2()[6])))
        
        
    def update_gpio_states(self):
        #4GPIO PIN USER FOR PROGRAM SELECTION
        global PS
        
        if PS == 0:
            
            input_value = read_gpio_as_int()
            reversed_value = reverse_bits(input_value, NUM_BITS)

            #print(f"Original Value (Dec): {input_value} (Bin: {format(input_value, '08b')})")
            #print(f"Reversed Value (Dec): {reversed_value} (Bin: {format(reversed_value, '08b')})")
            
            self.P_LB.setText(str(reversed_value))
            
        else:
            self.P_LB.setText("No Selection")
        
        
        
        #2 GPIO PIN FOR START AND STOP
        text = ""
        for i, pin in enumerate(pins):
            state = GPIO.input(pin)
            
            #self.labels[i].setText(f'GPIO Pin {pin}: {"HIGH" if state else "LOW"}')
            text += f'GPIO Pin {pin}: {"HIGH" if state else "LOW"}' + "\n"
            #print(text)
            if pin == 9:
                if state == 0:
                    self.flagstart = 1
                    
            if pin == 10:
                if state == 0:
                    self.flagstart = 2
            
              
            #decimal_output = binary_to_decimal()
        
        #self.Status1.setText(f'GPIO Pin {pin}: {"HIGH" if state else "LOW"}')
        #self.Status1.setText(text)
        
        #Process Start
        if self.flagstart == 1:
            print("Start flag 1 " + str(self.flagstart))
            self.Stop_btn.setStyleSheet("background-color : #330000");
            self.Start_btn.setStyleSheet("background-color : #00cc00");
            self.remaining_time = int(self.totaltime)
            self.timer.start(1000) #testing dealy
            self.flagstart = 0
            
            
        #Process Stop
        if self.flagstart == 2:
            self.Start_btn.setStyleSheet("background-color : #004d00");
            self.Stop_btn.setStyleSheet("background-color : #ff0000");
            self.timer.stop()
            self.remaining_time = 0
            self.StartTime.setText(f'Time remaining: {self.remaining_time} SEC')
            self.ProcesLB.setText("Process : ")
            self.progress_bar.setValue(0)
            self.flagstart = 0
            
        
        
        
            
    def closeEvent(self, event):
        GPIO.cleanup()  # Clean up GPIO on exit
        event.accept()
   
    def update_label1(self):
        label_time = QtCore.QDateTime.currentDateTime().toString("hh:mm:ss") 
        label_Date = QtCore.QDateTime.currentDateTime().toString("dd-MM-yyyy")
        self.Live_D.setText(label_Date)
        self.Live_T.setText(label_time)
        self.SetTesting()
        
        self.P1_LB.setText(self.P1 + str("\n") + str(self.P1_Ini * 100))
        self.P2_LB.setText(self.P2 + str("\n") + str(self.P2_Fill * 100))
        self.P3_LB.setText(self.P3 + str("\n") + str(self.P3_Stab * 100))
        self.P4_LB.setText(self.P4 + str("\n") + str(self.P4_Test * 100))
        self.P5_LB.setText(self.P5 + str("\n") + str(self.P5_Rel * 100))
        
        #self.ProcesLB.setText("Process Total Time - " + str(self.totaltime) + " Sec ")
        self.ProcesLB2.setText("Process Total Time : " + str(self.totaltime/10) + " Sec ")
        
            
            
           
        
            
        
        
        
        
   
        
        
    def SetTesting(self):
        
        Srows = getdata('Select * From Conversion')
        
        conn = sqlite3.connect(connstring)
        cur = conn.cursor()
        cur.execute('SELECT * from Programs where "Set" = "1"')
        rows = cur.fetchall()
        #print("row " + str(len(rows)))
        self.checkPro = len(rows)
        if len(rows) == 0 :
            self.Program_MSg.setText("Program not selected..")
            
        else:
            count = 0
            for row in rows:
                self.ProgramNo = str(row[1])
                self.Mode_lb.setText("Test Mode : Leak")
                self.Program_lb.setText("Program Name : " + str(row[0]))
                #self.PartNo_TB.setText("" + str(row[0]))
                #self.ProdCount_lb.setText(str(row[0]))
                self.FillPressure_lb.setText("Fill Pressure : " +str(row[2]))
                self.Leak_lb.setText("Leak : " +str(row[0]))
                #self.Result_lb.setText(str(row[0]))
                
                self.P1_Ini = row[6]/100
                self.P2_Fill = row[2]/100
                self.P3_Stab = row[3]/100
                self.P4_Test = row[4]/100
                self.P5_Rel = row[5]/100
                #self.delay = int(row[6])
                self.SetPressure = round(row[7], 3)  #convert to mbar
                self.PressureMin = round(row[9], 3)
                self.PressureMax = round(row[10], 3)
                self.PressureUnit = str(row[8])
                
                self.PU_lb.setText("Pressure Unit : " + str(self.PressureUnit))
                #print(self.PressureUnit)
                
#                 for r1 in Srows:
#                     if r1[2] == self.PressureUnit:
#                         
#                         self.SetPressure = round((abs(float(r1[0])) + abs(float(r1[1]))/3200) * row[7], 3)  #convert to mbar
#                         self.PressureMin = round((abs(float(r1[0])) + abs(float(r1[1]))/3200) * row[9], 3)
#                         self.PressureMax = round((abs(float(r1[0])) + abs(float(r1[1]))/3200) * row[10], 3)
                
                self.AllowLeakTest = row[11]	#Positive
                #print(self.AllowLeakTest)
                self.AllowReffLeak = -row[12]   #Negitve
                self.LeakUnit = str(row[13])
                #print(self.LeakUnit)
                self.volumn = round(row[15], 3)
                #print(self.volumn)
                
                #print(self.AllowLeakTest)
                #print(str(self.SetPressure) + str("\n") + str(self.PressureMin) + str("\n") + str(self.PressureMax))
                
                
                
                self.totaltime =  self.P1_Ini + self.P2_Fill + self.P3_Stab + self.P4_Test + self.P5_Rel 
                self.totaltime = self.totaltime #Msec conver second
                #print(self.totaltime)
                
        conn.commit()
        conn.close()
        
        
        
    def Result_Store(self):
        
        
        
        conn = sqlite3.connect(connstring)
        cur = conn.cursor()
        cur.execute('SELECT * from Results ')
        row = cur.fetchone()
        self.ProductionCount = 1
        if row:
            print("Check 1 : " + str(row))
            self.ProductionCount = int(row[8]) +  1
        else:
            self.ProductionCount = 1
        
        #self.ProductionCount = cur.fetchone()[0]
        #print(self.ProductionCount)
        conn.close()
        
        self.TestDateTime = QtCore.QDateTime.currentDateTime().toString("dd-MM-yyyy") + " " + QtCore.QDateTime.currentDateTime().toString("hh:mm:ss")
        
        #if check_textbox_value(self.ProgramNo) == "Float":
        
        #else:
        
        count = SaveReport(str(self.ProgramNo) , str(self.TestDateTime) , str(self.SetPressure)  , str(self.PressureUnit) , str(self.Leak)  , self.LeakUnit , str(self.Result) )
        
        print(count)
        
        Query = 'INSERT INTO Results("ProgramNo", "TestDateTime", "Pressure", "PressureUnit", "Leak", "LeakUnit", "Result", "ProductionCount") VALUES ("' + str(self.ProgramNo) + '", "' + str(self.TestDateTime) + '","' + str(self.SetPressure) + '", "' + str(self.PressureUnit) + '", "' + str(self.Leak) + '", "' + self.LeakUnit + '", "' + str(self.Result) + '", "' + str(self.ProductionCount) + '")'
        
        #print(Query)
        MyNonQuery(Query)
            #self.updatetable()
        
        
    def ViewResult(self):
        #print("view")
        self.table = QTableWidget(self)
        self.table.setRowCount(40)
        self.table.setColumnCount(8)
        self.table.verticalHeader().setVisible(False)
        self.table.setFont(QFont('Times', 8))
        
        self.table.setHorizontalHeaderLabels(["ProgramNo", "TestDateTime", "Pressure", "PressureUnit", "Leak", \
                                        "LeakUnit", "Result", "ProductionCount"])
        for i in range(0, 8):
            self.table.horizontalHeaderItem(i).setFont(QFont('Times', 8))
            self.table.setRowHeight(i, 20)
            self.table.setColumnWidth(i, 80)
        
        #conn = sqlite3.connect('LeakageTesting.db')
        cur = conn.cursor()
        cur.execute('SELECT * from Results')
        rows = cur.fetchall()
        count = 0
        for row in rows:
            
            #print(str(count) + " " + str(column) + " " + str(item))
            self.table.setItem(count, 0, QTableWidgetItem(str(row[0])))
            self.table.setItem(count, 1, QTableWidgetItem(str(row[1])))
            self.table.setItem(count, 2, QTableWidgetItem(str(row[2])))
            self.table.setItem(count, 3, QTableWidgetItem(str(row[3])))
            self.table.setItem(count, 4, QTableWidgetItem(str(row[4])))
            self.table.setItem(count, 5, QTableWidgetItem(str(row[5])))
            self.table.setItem(count, 6, QTableWidgetItem(str(row[6])))
            self.table.setItem(count, 7, QTableWidgetItem(str(row[7])))
            self.table.setItem(count, 8, QTableWidgetItem(str(row[8])))
            #self.table.setItem(count, 9, QTableWidgetItem(str(row[9])))
            count = count +1
        conn.commit()
        conn.close()
        
        self.table.resize(660,70)
        self.table.move(350,415)
        # Show the table
        #self.table.show()
        
    def start_timer(self):
        
        self.TE_LB.setText("2")
        self.TS_LB.setText("1")
        self.DPC = 0
        self.DP_LB.setText("")
        self.Program_MSg.setText("")
        self.SetTesting()
        if self.checkPro == 0:
            self.Program_MSg.setText("Program not selected..")
        else:
            GPIO.output(RELAY_PIN1, GPIO.LOW)
            GPIO.output(RELAY_PIN2, GPIO.LOW)
            GPIO.output(RELAY_PIN3, GPIO.LOW)
            GPIO.output(RELAY_PIN4, GPIO.LOW)
            
            GPIO.output(RELAY_PIN5, GPIO.HIGH)
            GPIO.output(RELAY_PIN6, GPIO.HIGH)
            GPIO.output(RELAY_PIN7, GPIO.HIGH)
            GPIO.output(RELAY_PIN8, GPIO.HIGH)
           
            if PS == 0:
                
                input_value = read_gpio_as_int()
                reversed_value = reverse_bits(input_value, NUM_BITS)
                #print(f"Original Value (Dec): {input_value} (Bin: {format(input_value, '08b')})")
                #print(f"Reversed Value (Dec): {reversed_value} (Bin: {format(reversed_value, '08b')})")
                self.P_LB.setText(str(reversed_value))
                
                conn = sqlite3.connect(connstring)
                cur = conn.cursor()
                cur.execute('SELECT count(*) from Programs where ProgramNo = "' + str(reversed_value) + '"')
                result = cur.fetchone()
                row_count = result[0]
                print("Number of rows in the table:", row_count)
                conn.commit()
                conn.close()
                if row_count == 0:
                    self.Program_MSg.setText("Program Selection no available")
                    #print("Program Selection no available")
                elif row_count == 1:
                    
                    self.SetTesting()
                    
                    if(int(self.ProgramNo) == int(reversed_value)):
                        print("Program allready selected")
                    else:
                        self.setupEvents1()
                        #print(self.data1)
                        for i in range(0, len(self.data1)):
                            Query = 'UPDATE Programs SET "Set" = 0 Where "ProgramNo" =  "' + str(self.data1[i]) + '"'
                            MyNonQuery(Query)
                        
                        Query = 'UPDATE Programs SET "Set" = 1 Where "ProgramNo" =  "' + str(reversed_value) + '"'
                        #print(Query)
                        MyNonQuery(Query)
                        
                        self.SetTesting()
                        
                        self.Program_MSg.setText("Selected Program " + str(self.ProgramNo))
                        
                        
                        
            else:
                self.SetTesting()
                self.Program_MSg.setText("Selected Program " + str(self.ProgramNo))
                    
            self.progress_bar.setMinimum(0)
            self.progress_bar.setMaximum(int(self.totaltime))
            self.remaining_time = self.totaltime
            
            if self.remaining_time > 0:
                self.timer.start(100)  # Start timer for 1000 milliseconds (1 second)
                self.StartTime.setText(f'Time remaining: {self.remaining_time} SEC')
                self.Stop_btn.setStyleSheet("background-color : #330000");
                self.Start_btn.setStyleSheet("background-color : #00cc66")
            else:
                self.StartTime.setText('Please enter a positive number.')
                self.Start_btn.setStyleSheet("background-color : #00331a");
        
    def Stop(self):     #Stop_btn click event
        self.Start_btn.setStyleSheet("background-color : #00331a");
        self.Stop_btn.setStyleSheet("background-color : #e60000")
        self.timer.stop()
        self.DPtimer.stop()
        self.remaining_time = 0
        self.StartTime.setText(f'Time remaining: {self.remaining_time} SEC')
        self.ProcesLB.setText("Process : ")
        self.progress_bar.setValue(0)
        GPIO.output(RELAY_PIN1, GPIO.LOW)
        GPIO.output(RELAY_PIN2, GPIO.LOW)
        GPIO.output(RELAY_PIN3, GPIO.LOW)
        GPIO.output(RELAY_PIN4, GPIO.LOW)
        
    def Loginbtn(self):
        print("Hello")
        
    
    def updateDP(self):
        
        self.SetTesting()
        self.DPC = self.DPC + 1
        #print("Count : " + str(self.DPC))
        T1 = self.TS_LB.text()
        T2 = self.TE_LB.text()
        
        #print("ct "+ str(self.DPC) + " T1 " + str(T1) + " T2 " + str(T2) + " "  + str((float(T1) - float(T2))/self.DPC))
        #print("self.LeakUnit : " + str(self.LeakUnit))
        P = get_Convert((float(T1) - float(T2)), self.LeakUnit, (self.P4_Test/10), self.volumn)
         #P = get_Convert((float(T1) - float(T2)), self.LeakUnit, (self.P4_Test/10), self.volumn)
        
        self.TotalA = self.TotalA + round(P, 3)
        if(self.DPC == 9):
            print("Count " + str(self.DPC) + " " +str(self.LeakUnit) + " : "  + str(round(P, 3))  + " Total : " +  str(round(self.TotalA, 2)) + " A : "+ str(round(self.TotalA, 2)/self.DPC))
            #self.DP_LB.setText(str(self.LeakUnit) + " : "  + str(round(P, 3)) + " A : "+ str(round((self.TotalA/self.DPC), 2)))
          
            self.DPC = 0
            self.TotalA = 0
        else:
            print("Count " + str(self.DPC) + " " +str(self.LeakUnit) + " : "  + str(round(P, 3)))
        
        
        
        
        
        #    
        
        
        
    def update_timer(self):
        self.SetTesting()
        #print("P " + str(self.SetPressure))
        #print("PressureUnit " + str(self.PressureUnit))
        #print("check Start flag " + str(self.flagstart))
        
        if self.remaining_time > 0:
            self.TS = ""
            self.TE = ""
            self.ADS_AV = 0
            self.ADS_AV2 = 0
            self.Leak = 0
            self.Result = 0
            #print(self.PressureUnit)
            if self.PressureUnit == "mBar":
                self.ADS_AV = get_UNIT()[3]
                self.ADS_AV2 = get_UNIT2()[3]
                #
            elif self.PressureUnit == "Bar":
                self.ADS_AV = get_UNIT()[4]
                self.ADS_AV2 = get_UNIT2()[4]
            elif self.PressureUnit == "PSI":
                self.ADS_AV = get_UNIT()[5]
                self.ADS_AV2 = get_UNIT2()[5]
            #print("a01 " + str(self.ADS_AV))  
            if self.ADS_AV > self.PressureMax:
                self.timer.stop()
                self.DPtimer.stop()
                self.ProcesLB.setText("Process : High Pressure")
                self.StartTime.setText("Time remaining: 0 SEC")
                GPIO.output(RELAY_PIN5, GPIO.LOW)
                GPIO.output(RELAY_PIN6, GPIO.LOW)
                self.remaining_time=0
            else:
                #print(self.P1_Ini + self.P2_Fill + self.P3_Stab + self.P4_Test - 3)
                #print("rem " + str(self.remaining_time))
                
                if float(self.remaining_time) == float(self.totaltime - int(self.P1_Ini + self.P2_Fill + self.P3_Stab)):
                    
                    self.DPtimer.start()  # Update every 100ms
                    self.TS  = self.ADS_AV
                    self.TS_LB.setText(str(self.ADS_AV))
                    #print("TS ", self.TS)
                if self.remaining_time <= self.totaltime - int(self.P1_Ini + self.P2_Fill + self.P3_Stab) and self.remaining_time >= self.totaltime - int(self.P1_Ini + self.P2_Fill + self.P3_Stab + self.P4_Test- 20):
                    
                     #self.ADS_AV2
                    #P = get_Convert((float(self.ADS_AV2)), self.LeakUnit, (self.P4_Test/10), self.volumn)
                    #self.TE  = P
                    self.TE_LB.setText(str(self.ADS_AV2))
                    self.ProcesLB1.setText(str(self.ADS_AV2) + " " + str(self.LeakUnit))
                    
                    
                    #print("TE", self.TE)
                
                #if float(self.remaining_time) == float(self.totaltime - int(self.P1_Ini + self.P2_Fill + self.P3_Stab + self.P4_Test)):
                    
                #print("TS ", self.TS)
                #print("TE", self.TE)
                
                if float(self.remaining_time) <= float(self.totaltime - int(self.P1_Ini + self.P2_Fill + self.P3_Stab + self.P4_Test)) and float(self.remaining_time) >= float(self.totaltime - int(self.P1_Ini + self.P2_Fill + self.P3_Stab+ self.P4_Test + self.P5_Rel)):
                    self.DPtimer.stop()
                    self.ProcesLB.setText("Process : " + self.P5) #Result
                    
                    #print("remaining_time : " + str(self.remaining_time) + " e " + str((self.totaltime + 1) - int(self.P1_Ini + self.P2_Fill + self.P3_Stab+ self.P4_Test + self.P5_Rel)))
                    if float(self.remaining_time) == float(self.totaltime - int(self.P1_Ini + self.P2_Fill + self.P3_Stab + self.P4_Test + 10)):
                        GPIO.output(RELAY_PIN4, GPIO.HIGH)
                        
                    if float(self.remaining_time) == float(self.totaltime - int(self.P1_Ini + self.P2_Fill + self.P3_Stab + self.P4_Test )):
                        print("Relase Time")
                        GPIO.output(RELAY_PIN3, GPIO.LOW)
                        
                        
                    
                    if self.remaining_time <= self.totaltime - int(self.P1_Ini + self.P2_Fill + self.P3_Stab) and self.remaining_time >= self.totaltime - int(self.P1_Ini + self.P2_Fill + self.P3_Stab + self.P4_Test):
                        
                        T1 = self.TS_LB.text()
                        T2 = self.TE_LB.text()
                        #print(str(T1) + " " + str(T2))
                        
                        #print("Test time L " + str(self.LeakUnit))
                        #P = get_Convert((float(T2)), self.LeakUnit, (self.P4_Test/10), self.volumn)
                        #print("value " + str(P) + " AllowLeakTest " + str(self.AllowLeakTest))
                        
                        P = self.ADS_AV2
                        
                        print("value " + str(P) + " AllowReffLeak : " + str(self.AllowReffLeak) + " AllowLeakTest : " + str(self.AllowLeakTest))
                        
                        
                        #self.DP_LB.setText("Count " + str(self.DPC) + " " +str(self.LeakUnit) + " : "  + str(round(P, 3)) + " A :" + str(round(self.TotalA, 3)))
                    
                        if float(self.AllowReffLeak) >= float(P):
                            self.Result = "NG"
                            self.ProcesLB1.setText("Process : Reffernce Reject")
                            GPIO.output(RELAY_PIN5, GPIO.LOW)
                        elif float(self.AllowLeakTest) <= float(P):
                            self.Result = "NG"
                            self.ProcesLB1.setText("Process : Part Raject")
                            GPIO.output(RELAY_PIN6, GPIO.LOW)
                        else:
                            self.Result = "OK"
                            self.ProcesLB1.setText("Process : Part Ok")
                            
                            GPIO.output(RELAY_PIN7, GPIO.LOW)
                            #GPIO.output(RELAY_PIN1, GPIO.LOW)
                            #GPIO.output(RELAY_PIN3, GPIO.LOW)
                            
                            GPIO.output(RELAY_PIN1, GPIO.LOW)
                            GPIO.output(RELAY_PIN4, GPIO.LOW)
                        
                        
                        
                        self.Result_Store()
                        self.Pressure = T1
                        self.Leak = T2
                        self.PressureUnit = self.PressureUnit
                        
                        
                        
                    
                    #self.ProcesLB.setText("Process : Part Ok")
                    
                    
                    
                        
                elif self.remaining_time <= self.totaltime - int(self.P1_Ini + self.P2_Fill + self.P3_Stab) and self.remaining_time >= self.totaltime - int(self.P1_Ini + self.P2_Fill + self.P3_Stab + self.P4_Test):
                    self.ProcesLB.setText("Process : " + self.P4) #Testing
                    GPIO.output(RELAY_PIN3, GPIO.HIGH)
                    
                    
                    
                    
                        
                        
                        
                
                    
                        
                        
                elif self.remaining_time <= self.totaltime - int(self.P1_Ini + self.P2_Fill) and self.remaining_time >= self.totaltime - int(self.P1_Ini + self.P2_Fill + self.P3_Stab):
                    self.ProcesLB.setText("Process : " + self.P3) #Stab
                    GPIO.output(RELAY_PIN2, GPIO.LOW)
                    self.ProcesLB1.setText("Stab Air " + str(self.ADS_AV))
                    
                    if self.ADS_AV > self.PressureMax:
                        #print("High Pressure")
                        self.ProcesLB1.setText("High Pressure")
                        GPIO.output(RELAY_PIN5, GPIO.LOW)
                        GPIO.output(RELAY_PIN6, GPIO.LOW)
                    #else:
                        #print("OK")
                        #self.ProcesLB1.setText("Pressure OK")
                    
                    
                elif self.remaining_time <= int(int(self.totaltime) - int(self.P1_Ini)) and self.remaining_time >= self.totaltime - int(self.P1_Ini + self.P2_Fill):
                    self.ProcesLB.setText("Process : " + self.P2) #Filling
                    print("ADS_AV " + str(self.ADS_AV) + " PressureMin " + str(self.PressureMin) + " PressureMax " + str(self.PressureMax))
                    
                    GPIO.output(RELAY_PIN2, GPIO.HIGH)
                    #print("SetPressure " + str(self.SetPressure))
                    if self.ADS_AV == self.SetPressure :
                        #print("Air Relase")
                        self.ProcesLB1.setText("Air Relase")
                    else:
                        #print("Air Fill")
                        self.ProcesLB1.setText("Air Fill " + str(self.ADS_AV))
                        
                    if self.ADS_AV < self.PressureMin:
                        #print("Low Pressure")
                        GPIO.output(RELAY_PIN5, GPIO.LOW)
                        GPIO.output(RELAY_PIN6, GPIO.LOW)
                        
                        self.ProcesLB1.setText("Low Pressure")
                        
                        self.Start_btn.setStyleSheet("background-color : #00331a");
                        GPIO.output(RELAY_PIN1, GPIO.LOW)
                        GPIO.output(RELAY_PIN2, GPIO.LOW)
                        GPIO.output(RELAY_PIN3, GPIO.LOW)
                        GPIO.output(RELAY_PIN4, GPIO.LOW)
                        self.Stop_btn.setStyleSheet("background-color : #e60000");
                        self.DPtimer.stop()
                        self.timer.stop()
                        
                    #print("R :"+str(self.remaining_time)+ " IS : " + str(int(int(self.totaltime) - int(self.P1_Ini))) + " IE" + str(self.totaltime - int(self.P1_Ini + self.P2_Fill)))
                      
                
                
                elif self.remaining_time <= int(int(self.totaltime)) and self.remaining_time >= self.totaltime - int(self.P1_Ini):
                    
                    #print("R :"+str(self.remaining_time)+ " IS : " + str(self.totaltime) + " IE" + str(self.totaltime - int(self.P1_Ini)))
                    
                    self.ProcesLB.setText("Process : " + self.P1) #inI
                    GPIO.output(RELAY_PIN1, GPIO.HIGH)
                    self.ProcesLB1.setText("")
                    
                    
                    
                
                
                self.Start_btn.setStyleSheet("background-color : Green");
                self.remaining_time -= 1
                self.StartTime.setText(f'Time remaining: {round(self.remaining_time/10)} SEC')
                
                self.progress_bar.setValue(int(self.totaltime) - int(self.remaining_time))
            
            
            
        else:
            self.timer.stop()
            
            self.StartTime.setText('Process : Completed')
            
            
            #self.ProcesLB1.setText("")
            
            GPIO.output(RELAY_PIN1, GPIO.LOW)
            GPIO.output(RELAY_PIN2, GPIO.LOW)
            GPIO.output(RELAY_PIN3, GPIO.LOW)
            GPIO.output(RELAY_PIN4, GPIO.LOW)
            
            self.Start_btn.setStyleSheet("background-color : #00331a");
            self.Stop_btn.setStyleSheet("background-color : #e60000");
            
            
    def setupEvents1(self):
        self.data1.clear()
        conn = sqlite3.connect(connstring)
        cur = conn.cursor()
        cur.execute('SELECT ProgramNo from Programs')
        rows = cur.fetchall()
        for row in rows:
            self.data1.append(row[0])
            
    
            
            
            
    
class SettingsPage(QWidget):
    select_clicked = pyqtSignal()
    def __init__(self):
        super().__init__()
        
        self.piclabel=QLabel("",self)
        self.piclabel.resize(150,35)
        self.piclabel.move(10,4)
        self.image = QImage("/home/admin/LeakageTesting/LOGO.png")
        self.imagepix = QPixmap.fromImage(self.image)
        self.piclabel.setScaledContents(True)
        self.piclabel.setPixmap(self.imagepix)
        
    
        
        self.style = "color: Black; font-weight: bold; " #  border: 1px solid black;"
        
        self.Live_D = QLabel("", self)
        self.Live_D.setAlignment(Qt.AlignRight)
        self.Live_D.setFont(QFont('DS-Digital', 15))
        self.Live_D.setStyleSheet("color: Black; font-weight: bold;   ")# border: 1px solid black;")
        self.Live_D.move(690, 0)
        self.Live_D.resize(180,20)
        
        self.Live_T = QLabel(" ", self)
        self.Live_T.setAlignment(Qt.AlignRight)
        self.Live_T.setFont(QFont('DS-Digital', 15))
        self.Live_T.setStyleSheet("color: Black; font-weight: bold;  ")#  border: 1px solid black;")
        self.Live_T.move(690, 18)
        self.Live_T.resize(180,20)
        
        self.timer1 = QtCore.QTimer(self)
        self.timer1.setInterval(1000)
        self.timer1.timeout.connect(self.update_label1)
        self.timer1.start()
        
        self.Live_LB = QLabel("SETTING", self)
        self.Live_LB.resize(550,25)
        self.Live_LB.setAlignment(Qt.AlignCenter)
        self.Live_LB.setFont(QFont('Times', 18))
        self.Live_LB.setStyleSheet("color: Black; font-weight: bold;  ")#  border: 1px solid black;")
        self.Live_LB.move(160, 5)

        self.Font1 = QFont('Times', 13)
        self.LabelSizeX = 170
        self.LabelSizeY = 30
        self.Style1 = "color: Black; font-weight: bold;  border: 1px solid black;"
        self.Style = "color: Black; font-weight: bold; "
        
        self.Mode_LB = QLabel("Mode", self)
        self.Mode_LB.resize(self.LabelSizeX, self.LabelSizeY)
        self.Mode_LB.setAlignment(Qt.AlignLeft)
        self.Mode_LB.setFont(self.Font1)
        self.Mode_LB.setStyleSheet(self.Style)
        self.Mode_LB.move(15, 40)

        self.ProgramName_LB = QLabel("Program Name", self)
        self.ProgramName_LB.resize(self.LabelSizeX, self.LabelSizeY)
        self.ProgramName_LB.setAlignment(Qt.AlignLeft)
        self.ProgramName_LB.setFont(self.Font1)
        self.ProgramName_LB.setStyleSheet(self.Style)
        self.ProgramName_LB.move(15, 75)
        
        

        self.FillTime_LB = QLabel("Fill Time (mSec)", self)
        self.FillTime_LB.resize(self.LabelSizeX, self.LabelSizeY)
        self.FillTime_LB.setAlignment(Qt.AlignLeft)
        self.FillTime_LB.setFont(self.Font1)
        self.FillTime_LB.setStyleSheet(self.Style)
        self.FillTime_LB.move(15, 110)

        self.TestTime_LB = QLabel("Test Time (mSec)", self)
        self.TestTime_LB.resize(self.LabelSizeX, self.LabelSizeY)
        self.TestTime_LB.setAlignment(Qt.AlignLeft)
        self.TestTime_LB.setFont(self.Font1)
        self.TestTime_LB.setStyleSheet(self.Style)
        self.TestTime_LB.move(15, 145)


        self.ProgramNo_LB = QLabel("Program No.", self)
        self.ProgramNo_LB.resize(self.LabelSizeX, self.LabelSizeY)
        self.ProgramNo_LB.setAlignment(Qt.AlignLeft)
        self.ProgramNo_LB.setFont(self.Font1)
        self.ProgramNo_LB.setStyleSheet(self.Style)
        self.ProgramNo_LB.move(360, 40)

        self.DelayTime_LB = QLabel("Delay Time (mSec)", self)
        self.DelayTime_LB.resize(self.LabelSizeX, self.LabelSizeY)
        self.DelayTime_LB.setAlignment(Qt.AlignLeft)
        self.DelayTime_LB.setFont(self.Font1)
        self.DelayTime_LB.setStyleSheet(self.Style)
        self.DelayTime_LB.move(360, 75)

        self.StabTime_LB = QLabel("Stab Time (mSec)", self)
        self.StabTime_LB.resize(self.LabelSizeX, self.LabelSizeY)
        self.StabTime_LB.setAlignment(Qt.AlignLeft)
        self.StabTime_LB.setFont(self.Font1)
        self.StabTime_LB.setStyleSheet(self.Style)
        self.StabTime_LB.move(360, 110)

        self.ReleaseTime_LB = QLabel("Release Time (mSec)", self)
        self.ReleaseTime_LB.resize(self.LabelSizeX, self.LabelSizeY)
        self.ReleaseTime_LB.setAlignment(Qt.AlignLeft)
        self.ReleaseTime_LB.setFont(self.Font1)
        self.ReleaseTime_LB.setStyleSheet(self.Style)
        self.ReleaseTime_LB.move(360, 145)


        self.Mode_CB = QComboBox(self)
        geek_list = ["Leak Mode", "Leak Mode2"]
        self.Mode_CB.resize(self.LabelSizeX, self.LabelSizeY)
        self.Mode_CB.addItems(geek_list)
        self.Mode_CB.move(185, 40)
        
        self.ProName_TB = QLineEdit(self) 
        self.ProName_TB.resize(self.LabelSizeX, self.LabelSizeY)
        self.ProName_TB.setFont(self.Font1)
        self.ProName_TB.move(185, 75)
        
        self.FillTime_TB = QLineEdit(self) 
        self.FillTime_TB.resize(self.LabelSizeX, self.LabelSizeY)
        self.FillTime_TB.setFont(self.Font1)
        self.FillTime_TB.move(185, 110)
        reg_ex = QRegExp("[0-9]+.?[0-9]{,2}")
        input_validator = QRegExpValidator(reg_ex, self.FillTime_TB)
        self.FillTime_TB.setValidator(input_validator)

        self.TestTime_TB = QLineEdit(self) 
        self.TestTime_TB.resize(self.LabelSizeX, self.LabelSizeY)
        self.TestTime_TB.setFont(self.Font1)
        self.TestTime_TB.move(185, 145)
        reg_ex = QRegExp("[0-9]+.?[0-9]{,2}")
        input_validator = QRegExpValidator(reg_ex, self.TestTime_TB)
        self.TestTime_TB.setValidator(input_validator)
        
        
        self.ProNo_TB = QLineEdit(self) 
        self.ProNo_TB.resize(self.LabelSizeX, self.LabelSizeY)
        self.ProNo_TB.setFont(self.Font1)
        self.ProNo_TB.textEdited.connect(self.showCurrentText)
        self.ProNo_TB.move(525, 40)
        reg_ex = QRegExp("[0-9]+.?[0-9]{,2}")
        input_validator = QRegExpValidator(reg_ex, self.ProNo_TB)
        self.ProNo_TB.setValidator(input_validator)
        
        self.DealyTime_TB = QLineEdit(self) 
        self.DealyTime_TB.resize(self.LabelSizeX, self.LabelSizeY)
        self.DealyTime_TB.setFont(self.Font1)
        self.DealyTime_TB.move(525, 75)
        reg_ex = QRegExp("[0-9]+.?[0-9]{,2}")
        input_validator = QRegExpValidator(reg_ex, self.DealyTime_TB)
        self.DealyTime_TB.setValidator(input_validator)

        self.StabTime_TB = QLineEdit(self) 
        self.StabTime_TB.resize(self.LabelSizeX, self.LabelSizeY)
        self.StabTime_TB.setFont(self.Font1)
        self.StabTime_TB.move(525, 110)
        reg_ex = QRegExp("[0-9]+.?[0-9]{,2}")
        input_validator = QRegExpValidator(reg_ex, self.StabTime_TB)
        self.StabTime_TB.setValidator(input_validator)

        self.ReleaseTime_TB = QLineEdit(self) 
        self.ReleaseTime_TB.resize(self.LabelSizeX, self.LabelSizeY)
        self.ReleaseTime_TB.setFont(self.Font1)
        self.ReleaseTime_TB.move(525, 145)
        reg_ex = QRegExp("[0-9]+.?[0-9]{,2}")
        input_validator = QRegExpValidator(reg_ex, self.ReleaseTime_TB)
        self.ReleaseTime_TB.setValidator(input_validator)
        
        
        
        
        

        


        
        

        
        

        self.SetPressure_LB = QLabel("Set Pressure", self)
        self.SetPressure_LB.resize(self.LabelSizeX, self.LabelSizeY)
        self.SetPressure_LB.setAlignment(Qt.AlignLeft)
        self.SetPressure_LB.setFont(self.Font1)
        self.SetPressure_LB.setStyleSheet(self.Style)
        self.SetPressure_LB.move(15, 190)

        self.PressureMin_LB = QLabel("Pressure Min.", self)
        self.PressureMin_LB.resize(self.LabelSizeX, self.LabelSizeY)
        self.PressureMin_LB.setAlignment(Qt.AlignLeft)
        self.PressureMin_LB.setFont(self.Font1)
        self.PressureMin_LB.setStyleSheet(self.Style)
        self.PressureMin_LB.move(15, 225)

        self.PressureUnit_LB = QLabel("Pressure Unit", self)
        self.PressureUnit_LB.resize(self.LabelSizeX, self.LabelSizeY)
        self.PressureUnit_LB.setAlignment(Qt.AlignLeft)
        self.PressureUnit_LB.setFont(self.Font1)
        self.PressureUnit_LB.setStyleSheet(self.Style)
        self.PressureUnit_LB.move(360, 190)

        self.PressureMax_LB = QLabel("Pressure Max.", self)
        self.PressureMax_LB.resize(self.LabelSizeX, self.LabelSizeY)
        self.PressureMax_LB.setAlignment(Qt.AlignLeft)
        self.PressureMax_LB.setFont(self.Font1)
        self.PressureMax_LB.setStyleSheet(self.Style)
        self.PressureMax_LB.move(360, 225)

        self.SetPressure_TB = QLineEdit(self) 
        self.SetPressure_TB.resize(self.LabelSizeX, self.LabelSizeY)
        self.SetPressure_TB.setFont(self.Font1)
        self.SetPressure_TB.move(185, 190)
        reg_ex = QRegExp("[0-9]+.?[0-9]{,2}")
        input_validator = QRegExpValidator(reg_ex, self.SetPressure_TB)
        self.SetPressure_TB.setValidator(input_validator)

        self.PressureMin_TB = QLineEdit(self) 
        self.PressureMin_TB.resize(self.LabelSizeX, self.LabelSizeY)
        self.PressureMin_TB.setFont(self.Font1)
        self.PressureMin_TB.move(185, 225)
        reg_ex = QRegExp("[0-9]+.?[0-9]{,2}")
        input_validator = QRegExpValidator(reg_ex, self.PressureMin_TB)
        self.PressureMin_TB.setValidator(input_validator)
        
        self.data1 = []
        self.setupEvents1()
        
        self.data = []
        self.setupEvents()
        #print(self.data[0])
        self.PressureUnit_CB = QComboBox(self)
        self.PressureUnit_CB.resize(self.LabelSizeX, self.LabelSizeY)
        self.PressureUnit_CB.addItems(self.data)
        self.PressureUnit_CB.move(525, 190)
        
        self.PressureMax_TB = QLineEdit(self) 
        self.PressureMax_TB.resize(self.LabelSizeX, self.LabelSizeY)
        self.PressureMax_TB.setFont(self.Font1)
        self.PressureMax_TB.move(525, 225)
        reg_ex = QRegExp("[0-9]+.?[0-9]{,2}")
        input_validator = QRegExpValidator(reg_ex, self.PressureMax_TB)
        self.PressureMax_TB.setValidator(input_validator)

        self.AllowTestLeak_LB = QLabel("Allowable Test Leak", self)
        self.AllowTestLeak_LB.resize(self.LabelSizeX, self.LabelSizeY)
        self.AllowTestLeak_LB.setAlignment(Qt.AlignLeft)
        self.AllowTestLeak_LB.setFont(self.Font1)
        self.AllowTestLeak_LB.setStyleSheet(self.Style)
        self.AllowTestLeak_LB.move(15, 270)

        self.AllowReffLeak_LB = QLabel("Allowable Reff. Leak", self)
        self.AllowReffLeak_LB.resize(self.LabelSizeX, self.LabelSizeY)
        self.AllowReffLeak_LB.setAlignment(Qt.AlignLeft)
        self.AllowReffLeak_LB.setFont(self.Font1)
        self.AllowReffLeak_LB.setStyleSheet(self.Style)
        self.AllowReffLeak_LB.move(15, 305)

        self.Unit_LB = QLabel("Unit", self)
        self.Unit_LB.resize(self.LabelSizeX, self.LabelSizeY)
        self.Unit_LB.setAlignment(Qt.AlignLeft)
        self.Unit_LB.setFont(self.Font1)
        self.Unit_LB.setStyleSheet(self.Style)
        self.Unit_LB.move(15, 340)



        self.VaccPre_LB = QLabel("Vaccum/Preesure", self)
        self.VaccPre_LB.resize(self.LabelSizeX, self.LabelSizeY)
        self.VaccPre_LB.setAlignment(Qt.AlignLeft)
        self.VaccPre_LB.setFont(self.Font1)
        self.VaccPre_LB.setStyleSheet(self.Style)
        self.VaccPre_LB.move(360, 270)

        self.Volume_LB = QLabel("Volume", self)
        self.Volume_LB.resize(self.LabelSizeX, self.LabelSizeY)
        self.Volume_LB.setAlignment(Qt.AlignLeft)
        self.Volume_LB.setFont(self.Font1)
        self.Volume_LB.setStyleSheet(self.Style)
        self.Volume_LB.move(360, 305)

        self.InCC_LB = QLabel("In CC", self)
        self.InCC_LB.resize(50, self.LabelSizeY)
        self.InCC_LB.setAlignment(Qt.AlignLeft)
        self.InCC_LB.setFont(self.Font1)
        self.InCC_LB.setStyleSheet(self.Style)
        self.InCC_LB.move(650, 305)



        self.AllowTestLeak_TB = QLineEdit(self) 
        self.AllowTestLeak_TB.resize(self.LabelSizeX, self.LabelSizeY)
        self.AllowTestLeak_TB.setFont(self.Font1)
        self.AllowTestLeak_TB.move(185, 270)
        reg_ex = QRegExp("[0-9]+.?[0-9]{,2}")
        input_validator = QRegExpValidator(reg_ex, self.AllowTestLeak_TB)
        self.AllowTestLeak_TB.setValidator(input_validator)

        self.AllowReffLeak_TB = QLineEdit(self) 
        self.AllowReffLeak_TB.resize(self.LabelSizeX, self.LabelSizeY)
        self.AllowReffLeak_TB.setFont(self.Font1)
        self.AllowReffLeak_TB.move(185, 305)
        reg_ex = QRegExp("[0-9]+.?[0-9]{,2}")
        input_validator = QRegExpValidator(reg_ex, self.AllowReffLeak_TB)
        self.AllowReffLeak_TB.setValidator(input_validator)

        self.Unit_CB = QComboBox(self)
        Unit_list = ["PA", "PA/Sec", "CC/Min"]
        self.Unit_CB.resize(self.LabelSizeX, self.LabelSizeY)
        self.Unit_CB.addItems(Unit_list)
        self.Unit_CB.move(185, 340)

        self.VaccPre_TB = QLineEdit(self) 
        self.VaccPre_TB.resize(self.LabelSizeX, self.LabelSizeY)
        self.VaccPre_TB.setFont(self.Font1)
        self.VaccPre_TB.move(525, 270)
        reg_ex = QRegExp("[0-9]+.?[0-9]{,2}")
        input_validator = QRegExpValidator(reg_ex, self.VaccPre_TB)
        self.VaccPre_TB.setValidator(input_validator)
        
        self.Volume_TB = QLineEdit(self) 
        self.Volume_TB.resize(100, self.LabelSizeY)
        self.Volume_TB.setFont(self.Font1)
        self.Volume_TB.move(525, 305)
        reg_ex = QRegExp("[0-9]+.?[0-9]{,2}")
        input_validator = QRegExpValidator(reg_ex, self.Volume_TB)
        self.Volume_TB.setValidator(input_validator)
        

        
        self.Select_btn = QPushButton('Select',self)
        self.Select_btn.resize(150,50)
        self.Select_btn.clicked.connect(self.Select)
        self.Select_btn.setFont(QFont('Times', 15, QFont.Bold))
        #self.Select_btn.setStyleSheet("background-color : Green");
        self.Select_btn.move(720,50)

        self.Save_btn = QPushButton('Save',self)
        self.Save_btn.resize(150,50)
        self.Save_btn.clicked.connect(self.Save)
        self.Save_btn.setFont(QFont('Times', 15, QFont.Bold))
        #self.Save_btn.setStyleSheet("background-color : Green");
        self.Save_btn.move(720,115)

        #self.Exit_btn = QPushButton('Exit',self)
        #self.Exit_btn.resize(150,50)
        #self.Exit_btn.clicked.connect(self.Exit)
        #self.Exit_btn.setFont(QFont('Times', 15, QFont.Bold))
        #self.Exit_btn.setStyleSheet("background-color : Green");
        #self.Exit_btn.move(720,175)
        

#         self.statusBar().showMessage("Ready")
#         self.statusBar().setStyleSheet(" background-color : Black; color:white;");
#         
#         self.Status("Ready")

        self.Status1 = QLabel("", self)
        self.Status1.resize(350, self.LabelSizeY)
        self.Status1.setAlignment(Qt.AlignCenter)
        self.Status1.setFont(self.Font1)
        self.Status1.setStyleSheet("color:Green;")
        self.Status1.move(360, 340)
        
        self.updatetable()
        
        self.Key_btn = QPushButton('Open Keyword',self)
        self.Key_btn.resize(150,30)
        self.Key_btn.clicked.connect(self.Keybtn)
        self.Key_btn.setFont(QFont('Times', 12, QFont.Bold))
        self.Key_btn.setStyleSheet("background-color : Green");
        self.Key_btn.move(720,175)
        
        
        
        
    def paintEvent(self, event):
        QMainWindow.paintEvent(self, event)
        
        painter = QPainter(self)
        #Top Header
        painter.setPen(QColor(255, 215, 0))
        painter.setBrush(QColor(255, 215, 0))
        painter.drawRect(0, 0, 875, 35)  
        # TOP 1
        painter.setBrush(QColor(241, 249, 185))
        painter.setPen(QPen(Qt.black, 0.1, Qt.SolidLine))
        painter.drawRect(10, 40, 700, 140)
        # TOP 2 
        painter.setPen(QPen(Qt.black, 0.1, Qt.SolidLine))
        painter.drawRect(10, 185, 700, 75)
        #TOP 3
        painter.setPen(QPen(Qt.black, 0.1, Qt.SolidLine))
        painter.drawRect(10, 265, 700, 106)
        
        painter.setPen(QPen(Qt.black, 0.1, Qt.SolidLine))
        painter.drawRect(715, 40, 160, 328)
        
    #def Exit(self) -> None:
        #self.close()
    
        
    def Keybtn(self) -> None:
        subprocess.Popen(["onboard"])
        
    def update_label1(self):
        label_time = QtCore.QDateTime.currentDateTime().toString("hh:mm:ss") 
        label_Date = QtCore.QDateTime.currentDateTime().toString("dd-MM-yyyy")
        self.Live_D.setText(label_Date)
        self.Live_T.setText(label_time)
        
        
    def Select(self) -> None:
        self.select_clicked.emit()
        conn = sqlite3.connect(connstring)
        cur = conn.cursor()
        cur.execute('SELECT count(*) from Programs where ProgramNo = "' + self.ProNo_TB.text() + '"')
        result = cur.fetchone()
        row_count = result[0]
        #print("Number of rows in the table:", row_count)
        conn.commit()
        conn.close()
        if row_count == 1:
            self.setupEvents1()
            print(self.data1)
            for i in range(0, len(self.data1)):
                Query = 'UPDATE Programs SET "Set" = 0 Where "ProgramNo" =  "' + str(self.data1[i]) + '"'
                MyNonQuery(Query)
            
            
            Query = 'UPDATE Programs SET "Set" = 1 Where "ProgramNo" =  "' + self.ProNo_TB.text() + '"'
            MyNonQuery(Query)
            self.updatetable()
            #self.Status("Select Program no " + str(self.ProNo_TB.text()))
            
            self.ProName_TB.setText("")
            self.ProNo_TB.setText("")
            self.FillTime_TB.setText("")
            self.StabTime_TB.setText("")
            self.TestTime_TB.setText("")
            self.ReleaseTime_TB.setText("")
            self.DealyTime_TB.setText("")
            self.SetPressure_TB.setText("")
            #self.PressureUnit_CB.currentText(row[8])
            self.PressureMin_TB.setText("")
            self.PressureMax_TB.setText("")
            self.AllowTestLeak_TB.setText("")
            self.AllowReffLeak_TB.setText("")
            #self.Unit_CB.currentText(row[13])
            self.VaccPre_TB.setText("")
            self.Volume_TB.setText("")
            
            
            
        else:
            #self.Status("Please Choice Program No")
            print("Please Choice Program No")
            
#     def Status(self, Msg) -> None:
#         self.statusBar().showMessage(Msg)
#         self.statusBar().setStyleSheet(" background-color : Black; color:white;");
        
    def Save(self) -> None:     #Save
        if self.ProNo_TB.text() == "":
            #print("Program No is Empty")
            self.Status1.setText("Program No is Empty")
            
        else:
            if self.ProNo_TB.text() == "":
                self.Status1.setText("Program no is empty.. Please fill")
            elif self.ProName_TB.text() == "":
                self.Status1.setText("Program name is empty.. Please fill")
            elif self.FillTime_TB.text() == "":
                self.Status1.setText("Filling time is empty.. Please fill")
            elif self.StabTime_TB.text() == "":
                self.Status1.setText("Stab time is empty.. Please fill")
            elif self.TestTime_TB.text() == "":
                self.Status1.setText("Test time is empty.. Please fill")
            elif self.ReleaseTime_TB.text() == "":
                self.Status1.setText("Release Time is empty.. Please fill")
            elif self.DealyTime_TB.text() == "":
                self.Status1.setText("Dealy Time is empty.. Please fill")
            elif self.SetPressure_TB.text() == "":
                self.Status1.setText("Set Pressure is empty.. Please fill")
            elif self.PressureMin_TB.text() == "":
                self.Status1.setText("Pressure Min is empty.. Please fill")
            elif self.PressureMax_TB.text() == "":
                self.Status1.setText("Pressure Max is empty.. Please fill")
            elif self.AllowTestLeak_TB.text() == "":
                self.Status1.setText("Allow Test Leak is empty.. Please fill")
            elif self.AllowReffLeak_TB.text() == "":
                self.Status1.setText("Allow Reff Leak is empty.. Please fill")
            elif self.VaccPre_TB.text() == "":
                self.Status1.setText("Vacc Pre is empty.. Please fill")
            elif self.Volume_TB.text() == "":
                self.Status1.setText("Volume is empty.. Please fill")
            else:
                self.UpdateInsert()
                
            
            
            
                
            
        
    def UpdateInsert(self):
        conn = sqlite3.connect(connstring)
        cur = conn.cursor()
        cur.execute('SELECT count(*) from Programs where ProgramNo = "' + self.ProNo_TB.text() + '"')
        result = cur.fetchone()
        row_count = result[0]
        #print("Number of rows in the table:", row_count)
        conn.commit()
        conn.close()
        if row_count == 1:
            #update
            print("Update")
            Query= 'UPDATE Programs SET "ProgramName" = "' + self.ProName_TB.text() + '",\
                    "FillTime" = "' + self.FillTime_TB.text() + '", "StabTime"= "' + self.StabTime_TB.text() + '", \
                    "TestTime" = "' + self.TestTime_TB.text() + '", "ReleaseTime" = "' + self.ReleaseTime_TB.text() + '", \
                    "DelayTime" = "' + self.DealyTime_TB.text() + '", "SetPressure" = "' + self.SetPressure_TB.text() + '", \
                    "SetPressureUnit" = "' + self.PressureUnit_CB.currentText() + '", "SetPressureMin" = "' + self.PressureMin_TB.text() + '",\
                    "SetPressureMax" = "' + self.PressureMax_TB.text() + '","AllowableTestLeak" = "' + self.AllowTestLeak_TB.text() + '", \
                    "LeakUnit" = "' + self.Unit_CB.currentText() + '", "SignalTime" = "' + self.VaccPre_TB.text() + '", \
                    "AllowableRefLeak" = "' + self.AllowReffLeak_TB.text() + '", "Volume" = "' + self.Volume_TB.text() + '", "Set"= 0 Where "ProgramNo" =  "' + self.ProNo_TB.text() + '"'
            print(Query)
            MyNonQuery(Query)
            self.updatetable()
            self.Status1.setText("Update Data Successfully..")
            print("Update Data Successfully..")
            self.ProName_TB.setText("")
            self.ProNo_TB.setText("")
            self.FillTime_TB.setText("")
            self.StabTime_TB.setText("")
            self.TestTime_TB.setText("")
            self.ReleaseTime_TB.setText("")
            self.DealyTime_TB.setText("")
            self.SetPressure_TB.setText("")
            #self.PressureUnit_CB.currentText(row[8])
            self.PressureMin_TB.setText("")
            self.PressureMax_TB.setText("")
            self.AllowTestLeak_TB.setText("")
            self.AllowReffLeak_TB.setText("")
            #self.Unit_CB.currentText(row[13])
            self.VaccPre_TB.setText("")
            self.Volume_TB.setText("")
            
        else:
            #insert
            print("Insert")
            Query = 'INSERT INTO Programs("ProgramName", "ProgramNo", "FillTime", "StabTime", "TestTime", "ReleaseTime",\
                                        "DelayTime", "SetPressure", "SetPressureUnit", "SetPressureMin", "SetPressureMax",\
                                      "AllowableTestLeak", "AllowableRefLeak", "LeakUnit", "SignalTime", "Volume", "Set")\
                                        VALUES ("' + self.ProName_TB.text() + '", "' + self.ProNo_TB.text() + '",\
                                               "' + self.FillTime_TB.text() + '", "' + self.StabTime_TB.text() + '"\
                                        , "' + self.TestTime_TB.text() + '", "' + self.ReleaseTime_TB.text() + '"\
                                        , "' + self.DealyTime_TB.text() + '", "' + self.SetPressure_TB.text() + '"\
                                        , "' + self.PressureUnit_CB.currentText() + '", "' + self.PressureMin_TB.text() + '"\
                                        , "' + self.PressureMax_TB.text() + '", "' + self.AllowTestLeak_TB.text() + '"\
                                         , "' + self.AllowReffLeak_TB.text() + '", "' + self.Unit_CB.currentText() + '"\
                                      , "' + self.VaccPre_TB.text() + '", "' + self.Volume_TB.text() + '", 0)'
            print(Query)
            MyNonQuery(Query)
            self.updatetable()
            self.Status1.setText("Insert Data Successfully...") 
            
        
            
            self.ProName_TB.setText("")
            self.ProNo_TB.setText("")
            self.FillTime_TB.setText("")
            self.StabTime_TB.setText("")
            self.TestTime_TB.setText("")
            self.ReleaseTime_TB.setText("")
            self.DealyTime_TB.setText("")
            self.SetPressure_TB.setText("")
            #self.PressureUnit_CB.currentText(row[8])
            self.PressureMin_TB.setText("")
            self.PressureMax_TB.setText("")
            self.AllowTestLeak_TB.setText("")
            self.AllowReffLeak_TB.setText("")
            #self.Unit_CB.currentText(row[13])
            self.VaccPre_TB.setText("")
            self.Volume_TB.setText("")
        
        
    def setupEvents(self):
        
        conn = sqlite3.connect(connstring)
        cur = conn.cursor()
        cur.execute('SELECT * from Conversion')
        rows = cur.fetchall()
        for row in rows:
            self.data.append(row[0])
            #print(row[0])
        conn.commit()
        conn.close()
        
    def setupEvents1(self):
        self.data1.clear()
        conn = sqlite3.connect(connstring)
        cur = conn.cursor()
        cur.execute('SELECT ProgramNo from Programs')
        rows = cur.fetchall()
        for row in rows:
            self.data1.append(row[0])
            
        conn.commit()
        conn.close()
        
    def updatetable(self):
        self.table = QTableWidget(self)
        self.table.setRowCount(40)
        self.table.setColumnCount(17)
        self.table.verticalHeader().setVisible(False)
        self.table.setFont(QFont('Times', 8))
        
        self.table.setHorizontalHeaderLabels(["ProgramName", "ProgramNo", "FillTime", "StabTime", "TestTime", "ReleaseTime",\
                                        "DelayTime", "SetPressure", "SetPressureUnit", "SetPressureMin", "SetPressureMax",\
                                      "AllowableTestLeak", "AllowableRefLeak", "LeakUnit", "SignalTime", "Volume", "Set"])
        for i in range(0, 17):
            self.table.horizontalHeaderItem(i).setFont(QFont('Times', 8))
            self.table.setRowHeight(i, 20)
            self.table.setColumnWidth(i, 80)
        
        conn = sqlite3.connect(connstring)
        cur = conn.cursor()
        cur.execute('SELECT * from Programs')
        rows = cur.fetchall()
        count = 0
        for row in rows:
            
            #print(str(count) + " " + str(column) + " " + str(item))
            self.table.setItem(count, 0, QTableWidgetItem(str(row[0])))
            self.table.setItem(count, 1, QTableWidgetItem(str(row[1])))
            self.table.setItem(count, 2, QTableWidgetItem(str(row[2])))
            self.table.setItem(count, 3, QTableWidgetItem(str(row[3])))
            self.table.setItem(count, 4, QTableWidgetItem(str(row[4])))
            self.table.setItem(count, 5, QTableWidgetItem(str(row[5])))
            self.table.setItem(count, 6, QTableWidgetItem(str(row[6])))
            self.table.setItem(count, 7, QTableWidgetItem(str(row[7])))
            self.table.setItem(count, 8, QTableWidgetItem(str(row[8])))
            self.table.setItem(count, 9, QTableWidgetItem(str(row[9])))
            self.table.setItem(count, 10, QTableWidgetItem(str(row[10])))
            self.table.setItem(count, 11, QTableWidgetItem(str(row[11])))
            self.table.setItem(count, 12, QTableWidgetItem(str(row[12])))
            self.table.setItem(count, 13, QTableWidgetItem(str(row[13])))
            self.table.setItem(count, 14, QTableWidgetItem(str(row[14])))
            self.table.setItem(count, 15, QTableWidgetItem(str(row[15])))
            self.table.setItem(count, 16, QTableWidgetItem(str(row[16])))
            count = count +1
        conn.commit()
        conn.close()
        
        self.table.resize(150,150)
        self.table.move(720,230)
        # Show the table
        self.table.show()
        
    def showCurrentText(self, text):
        print('current-text:', text)
        
        conn = sqlite3.connect(connstring)
        cur = conn.cursor()
        cur.execute('SELECT count(*) from Programs where ProgramNo like "' + self.ProNo_TB.text() + '"')
        result = cur.fetchone()
        row_count = result[0]
        conn.commit()
        conn.close()
        
        if row_count == 0:
            self.ProName_TB.setText("")
            #self.ProNo_TB.setText(row[1])
            self.FillTime_TB.setText("")
            self.StabTime_TB.setText("")
            self.TestTime_TB.setText("")
            self.ReleaseTime_TB.setText("")
            self.DealyTime_TB.setText("")
            self.SetPressure_TB.setText("")
            #self.PressureUnit_CB.currentText(row[8])
            self.PressureMin_TB.setText("")
            self.PressureMax_TB.setText("")
            self.AllowTestLeak_TB.setText("")
            self.AllowReffLeak_TB.setText("")
            #self.Unit_CB.currentText(row[13])
            self.VaccPre_TB.setText("")
            self.Volume_TB.setText("")
            self.Status1.setText("No Record Found..")
            
        else:
            conn = sqlite3.connect(connstring)
            cur = conn.cursor()
            cur.execute('SELECT * from Programs where ProgramNo like "' + self.ProNo_TB.text() + '"')
            rows = cur.fetchall()
            count = 0
            for row in rows:
                self.ProName_TB.setText(row[0])
                #self.ProNo_TB.setText(row[1])
                self.FillTime_TB.setText(str(row[2]))
                self.StabTime_TB.setText(str(row[3]))
                self.TestTime_TB.setText(str(row[4]))
                self.ReleaseTime_TB.setText(str(row[5]))
                self.DealyTime_TB.setText(str(row[6]))
                self.SetPressure_TB.setText(str(row[7]))
                
                #print(row[8])
                index = self.PressureUnit_CB.findText(str(row[8]))
                self.PressureUnit_CB.setCurrentIndex(index)
                
                self.PressureMin_TB.setText(str(row[9]))
                
                self.PressureMax_TB.setText(str(row[10]))
                self.AllowTestLeak_TB.setText(str(row[11]))
                self.AllowReffLeak_TB.setText(str(row[12]))
                
                index = self.Unit_CB.findText(str(row[13]))
                self.Unit_CB.setCurrentIndex(index)
                                                     
                self.VaccPre_TB.setText(str(row[14]))
                self.Volume_TB.setText(str(row[15]))
                self.Status1.setText("Record View..") 
                
            conn.commit()
            conn.close()
        
        
class CalibrationPage(QWidget):
    select_clicked = pyqtSignal()
    def __init__(self):
        super().__init__()
        self.piclabel=QLabel("",self)
        self.piclabel.resize(200,60)
        self.piclabel.move(20,10)
        self.image = QImage("/home/admin/LeakageTesting/LOGO2.png")
        self.imagepix = QPixmap.fromImage(self.image)
        self.piclabel.setScaledContents(True)
        self.piclabel.setPixmap(self.imagepix)
        
        
        self.Live_LB = QLabel("SONSOR CALIBRATION", self)
        self.Live_LB.resize(1020,40)
        self.Live_LB.setAlignment(Qt.AlignCenter)
        self.Live_LB.setFont(QFont('Times', 25))
        self.Live_LB.setStyleSheet("color: Black; font-weight: bold;  ") # border: 1px solid black;")
        self.Live_LB.move(0, 20)
        
        
        
        
        self.style = "color: Black; font-weight: bold; " #  border: 1px solid black;"
        
        self.Live_D = QLabel("", self)
        self.Live_D.setAlignment(Qt.AlignRight)
        self.Live_D.setFont(QFont('DS-Digital', 25))
        self.Live_D.setStyleSheet("color: Black; font-weight: bold;   ")# border: 1px solid black;")
        self.Live_D.move(830, 5)
        self.Live_D.resize(180,30)
        
        self.Live_T = QLabel(" ", self)
        self.Live_T.setAlignment(Qt.AlignRight)
        self.Live_T.setFont(QFont('DS-Digital', 25))
        self.Live_T.setStyleSheet("color: Black; font-weight: bold;  ")#  border: 1px solid black;")
        self.Live_T.move(830, 40)
        self.Live_T.resize(180,30)
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000) # Update every 1000 ms (1 second)
        self.update_time()
        
        self.Font1 = QFont('Times', 13)
        
        self.Unit_LB = QLabel("Sonsor 1 Unit :                  MBAR", self)
        self.Unit_LB.resize(250, 40)
        self.Unit_LB.setAlignment(Qt.AlignLeft)
        self.Unit_LB.setFont(self.Font1)
        self.Unit_LB.setStyleSheet("color: Black; font-weight: bold;  ")
        self.Unit_LB.move(150, 100)
        
        self.SonsorMin_LB = QLabel("Sonsor 1 Min (4 MA) :", self)
        self.SonsorMin_LB.resize(200, 40)
        self.SonsorMin_LB.setAlignment(Qt.AlignLeft)
        self.SonsorMin_LB.setFont(self.Font1)
        self.SonsorMin_LB.setStyleSheet("color: Black; font-weight: bold;  ")
        self.SonsorMin_LB.move(150, 140)

        
        self.SonsorMin_TB = QLineEdit(self) 
        self.SonsorMin_TB.resize(130, 30)
        self.SonsorMin_TB.setFont(self.Font1)
        self.SonsorMin_TB.move(330, 138)
        
        
        
        self.SonsorMax_LB = QLabel("Sonsor 1 Max (20MA) :", self)
        self.SonsorMax_LB.resize(200, 40)
        self.SonsorMax_LB.setAlignment(Qt.AlignLeft)
        self.SonsorMax_LB.setFont(self.Font1)
        self.SonsorMax_LB.setStyleSheet("color: Black; font-weight: bold;  ")
        self.SonsorMax_LB.move(150, 180)
        
        self.SonsorMax_TB = QLineEdit(self) 
        self.SonsorMax_TB.resize(130, 30)
        self.SonsorMax_TB.setFont(self.Font1)
        self.SonsorMax_TB.move(330, 176)
        
        
        self.SonsorMF = QLabel("Sonsor 1 MF:", self)
        self.SonsorMF.resize(160, 40)
        self.SonsorMF.setAlignment(Qt.AlignLeft)
        self.SonsorMF.setFont(self.Font1)
        self.SonsorMF.setStyleSheet("color: Black; font-weight: bold;  ")
        self.SonsorMF.move(150, 220)
        
        self.SonsorMF_TB = QLineEdit(self) 
        self.SonsorMF_TB.resize(130, 30)
        self.SonsorMF_TB.setFont(self.Font1)
        self.SonsorMF_TB.move(330, 220)
        
        ###SonSOr2
        
        self.Unit_LB2= QLabel("Sonsor 2 Unit :                  ", self)
        self.Unit_LB2.resize(250, 40)
        self.Unit_LB2.setAlignment(Qt.AlignLeft)
        self.Unit_LB2.setFont(self.Font1)
        self.Unit_LB2.setStyleSheet("color: Black; font-weight: bold;  ")
        self.Unit_LB2.move(500, 100)
        
        self.SonsorMin_LB2 = QLabel("Sonsor 2 Min (4 MA) :", self)
        self.SonsorMin_LB2.resize(200, 40)
        self.SonsorMin_LB2.setAlignment(Qt.AlignLeft)
        self.SonsorMin_LB2.setFont(self.Font1)
        self.SonsorMin_LB2.setStyleSheet("color: Black; font-weight: bold;  ")
        self.SonsorMin_LB2.move(500, 140)

        
        self.SonsorMin_TB2 = QLineEdit(self) 
        self.SonsorMin_TB2.resize(130, 30)
        self.SonsorMin_TB2.setFont(self.Font1)
        self.SonsorMin_TB2.move(680, 138)
        
        
        
        self.SonsorMax_LB2 = QLabel("Sonsor 2 Max (20MA):", self)
        self.SonsorMax_LB2.resize(200, 40)
        self.SonsorMax_LB2.setAlignment(Qt.AlignLeft)
        self.SonsorMax_LB2.setFont(self.Font1)
        self.SonsorMax_LB2.setStyleSheet("color: Black; font-weight: bold;  ")
        self.SonsorMax_LB2.move(500, 180)
        
        self.SonsorMax_TB2 = QLineEdit(self) 
        self.SonsorMax_TB2.resize(130, 30)
        self.SonsorMax_TB2.setFont(self.Font1)
        self.SonsorMax_TB2.move(680, 176)
        
        
        self.SonsorMF2 = QLabel("Sonsor 2 MF:", self)
        self.SonsorMF2.resize(200, 40)
        self.SonsorMF2.setAlignment(Qt.AlignLeft)
        self.SonsorMF2.setFont(self.Font1)
        self.SonsorMF2.setStyleSheet("color: Black; font-weight: bold;  ")
        self.SonsorMF2.move(500, 220)
        
        self.SonsorMF_TB2 = QLineEdit(self) 
        self.SonsorMF_TB2.resize(130, 30)
        self.SonsorMF_TB2.setFont(self.Font1)
        self.SonsorMF_TB2.move(680, 220)
        
        
        self.Save_btn = QPushButton('Save',self)
        self.Save_btn.resize(100, 30)
        self.Save_btn.clicked.connect(self.Save)
        self.Save_btn.setFont(QFont('Times', 15, QFont.Bold))
        #self.Save_btn.setStyleSheet("background-color : Green");
        self.Save_btn.move(400,270)

        
        
        self.Key_btn = QPushButton('Open Keyword',self)
        self.Key_btn.resize(130,30)
        self.Key_btn.clicked.connect(self.Keybtn)
        self.Key_btn.setFont(QFont('Times', 12, QFont.Bold))
        #self.Key_btn.setStyleSheet("background-color : Green");
        self.Key_btn.move(520,270)
        
        self.Msg_LB = QLabel("", self)
        self.Msg_LB.resize(300, 40)
        self.Msg_LB.setAlignment(Qt.AlignCenter)
        self.Msg_LB.setFont(self.Font1)
        self.Msg_LB.setStyleSheet("color: Green; font-weight: bold;  ")
        self.Msg_LB.move(350, 300)
        
        
        self.getInfo()
        
    def paintEvent(self, event):
        QMainWindow.paintEvent(self, event)
        
        painter = QPainter(self)
        #Top Header
        painter.setPen(QColor(255, 215, 0))
        painter.setBrush(QColor(255, 215, 0))
        painter.drawRect(0, 0, 1020, 80)  
        # TOP 1
        painter.setBrush(QColor(241, 249, 185))
        painter.setPen(QPen(Qt.black, 0.1, Qt.SolidLine))
        painter.drawRect(0, 80, 1020, 315)
        # TOP 2 
        painter.setPen(QPen(Qt.black, 0.1, Qt.SolidLine))
        painter.setPen(QColor(255, 215, 0))
        painter.setBrush(QColor(255, 215, 0))
        painter.drawRect(0, 395, 1020, 165)
        
    def update_time(self):
        label_time = QtCore.QDateTime.currentDateTime().toString("hh:mm:ss") 
        label_Date = QtCore.QDateTime.currentDateTime().toString("dd-MM-yyyy")
        self.Live_D.setText(label_Date)
        self.Live_T.setText(label_time)
        
    def Keybtn(self) -> None:
        subprocess.Popen(["onboard"])
        
    def getInfo(self):
        self.Msg_LB .setText("")
        rows = getdata('Select * From Calibration Where "S1_Unit" = "Mbar"')
        for row in rows:
            print(row[3])
            #sssssssself.Unit_LB.setText("Unit :      " +str(row[2]))
            self.SonsorMin_TB.setText(row[0])
            self.SonsorMax_TB.setText(row[1])
            self.Unit_LB.setText("Sonsor 1 Unit :                  "+str(row[2]))
            self.SonsorMF_TB.setText(str(row[3]))
            self.SonsorMin_TB2.setText(row[4])
            self.SonsorMax_TB2.setText(row[5])
            self.Unit_LB2.setText("Sonsor 2 Unit :                  "+str(row[6]))
            self.SonsorMF_TB2.setText(str(row[7]))
    
    
    
         
        
    def Save(self) -> None:
        
        if check_textbox_value(self.SonsorMin_TB.text()) == "Float" and check_textbox_value(self.SonsorMax_TB.text()) == "Float" and check_textbox_value(self.SonsorMF_TB.text()) == "Float" and check_textbox_value(self.SonsorMin_TB2.text()) == "Float" and check_textbox_value(self.SonsorMax_TB2.text()) == "Float" and check_textbox_value(self.SonsorMF_TB2.text()) == "Float":
            Query = 'UPDATE Calibration SET "S1_Min" = "' + str(self.SonsorMin_TB.text()) + '","S1_Max" = "'+ str(self.SonsorMax_TB.text()) +'", "S1_MF" = "'+ str(self.SonsorMF_TB.text()) +'", "S2_Min" = "' + str(self.SonsorMin_TB2.text()) + '","S2_Max" = "'+ str(self.SonsorMax_TB2.text()) +'", "S2_MF" = "'+ str(self.SonsorMF_TB2.text()) +'" Where "S1_Unit" = "Mbar"'
            MyNonQuery(Query)
            self.Msg_LB.setText("Update Sucessfully..")

        else:
            self.Msg_LB.setText("Enter Textbox value in incorrect")
        
        
        
        
        #try:
            #SMIN = float(self.SonsorMin_TB.text())
            #SMAX = float(self.SonsorMax_TB.text())
            #SMF = float(self.SonsorMF_TB.text())
            
        #except ValueError:
            #self.Msg_LB.setText("Textbox value Invalid")
        
        
            
            
        
        

class AboutPage(QWidget):
    def __init__(self):
        super().__init__()
        
class ReportPage(QWidget):
    select_clicked = pyqtSignal()
    def __init__(self):
        super().__init__()
        
        self.piclabel=QLabel("",self)
        self.piclabel.resize(200,60)
        self.piclabel.move(20,10)
        self.image = QImage("/home/admin/LeakageTesting/LOGO2.png")
        self.imagepix = QPixmap.fromImage(self.image)
        self.piclabel.setScaledContents(True)
        self.piclabel.setPixmap(self.imagepix)
        
        
        self.Live_LB = QLabel("REPORT VIEW", self)
        self.Live_LB.resize(1020,40)
        self.Live_LB.setAlignment(Qt.AlignCenter)
        self.Live_LB.setFont(QFont('Times', 25))
        self.Live_LB.setStyleSheet("color: Black; font-weight: bold;  ") # border: 1px solid black;")
        self.Live_LB.move(0, 20)
        
        
        
        
        self.style = "color: Black; font-weight: bold; " #  border: 1px solid black;"
        
        self.Live_D = QLabel("", self)
        self.Live_D.setAlignment(Qt.AlignRight)
        self.Live_D.setFont(QFont('DS-Digital', 25))
        self.Live_D.setStyleSheet("color: Black; font-weight: bold;   ")# border: 1px solid black;")
        self.Live_D.move(830, 5)
        self.Live_D.resize(180,30)
        
        self.Live_T = QLabel(" ", self)
        self.Live_T.setAlignment(Qt.AlignRight)
        self.Live_T.setFont(QFont('DS-Digital', 25))
        self.Live_T.setStyleSheet("color: Black; font-weight: bold;  ")#  border: 1px solid black;")
        self.Live_T.move(830, 40)
        self.Live_T.resize(180,30)
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000) # Update every 1000 ms (1 second)
        self.update_time()
        
        self.From_LB = QLabel("From Date : ", self)
        self.From_LB.resize(150, 30)
        self.From_LB.setAlignment(Qt.AlignLeft)
        self.From_LB.setFont(QFont('Times', 12))
        self.From_LB.setStyleSheet("color: Black; font-weight: bold;  ")
        self.From_LB.move(50, 90)
        
        self.from_date = QDateEdit(self)
        self.from_date.setCalendarPopup(True)
        self.from_date.setDate(QDate.currentDate())
        self.from_date.resize(200, 30)
        self.from_date.move(150, 88)   # Moves to the X, Y coordinates
        
        
        self.To_LB = QLabel("To Date : ", self)
        self.To_LB.resize(150, 30)
        self.To_LB.setAlignment(Qt.AlignLeft)
        self.To_LB.setFont(QFont('Times', 12))
        self.To_LB.setStyleSheet("color: Black; font-weight: bold;  ")
        self.To_LB.move(400, 90)
        
        self.To_date = QDateEdit(self)
        self.To_date.setCalendarPopup(True)
        self.To_date.setDate(QDate.currentDate())
        self.To_date.resize(200, 30)
        self.To_date.move(500, 88)   # Moves to the X, Y coordinates
        
        self.Submit_btn = QPushButton('Submit',self)
        self.Submit_btn.resize(100, 30)
        self.Submit_btn.clicked.connect(self.load_data)
        self.Submit_btn.setFont(QFont('Times', 15, QFont.Bold))
        #self.Save_btn.setStyleSheet("background-color : Green");
        self.Submit_btn.move(750,88)
        
        self.table = QTableWidget(self)
        #self.table.setRowCount(40)
        self.table.setColumnCount(8)
        self.table.verticalHeader().setVisible(False)
        self.table.setFont(QFont('Times', 8))
        
        self.table.setHorizontalHeaderLabels(["ProgramNo", "TestDateTime", "Pressure", "PressureUnit", "Leak", \
                                        "LeakUnit", "Result", "ProductionCount"])
        
        self.table.resize(900,380)
        self.table.move(40,130)
        self.table.show()
        
        
    def load_data(self):
        from_date = self.from_date.date().toString("dd-MM-yyyy")
        to_date = self.To_date.date().toString("dd-MM-yyyy")
        
        self.table.removeRow(0)
        conn = sqlite3.connect(connstring)
        cur = conn.cursor()
        query = 'SELECT * from Results where TestDateTime Between "'+ from_date +' 00:00:01"  And "'+ to_date  +' 23:59:59"'
        print(query)
        cur.execute(query)
        rows = cur.fetchall()
        self.table.setRowCount(len(rows))
        count=0
        for row in rows:
            
            self.table.setItem(count, 0, QTableWidgetItem(str(row[1])))
            self.table.setItem(count, 1, QTableWidgetItem(str(row[2])))
            self.table.setItem(count, 2, QTableWidgetItem(str(row[3])))
            self.table.setItem(count, 3, QTableWidgetItem(str(row[4])))
            self.table.setItem(count, 4, QTableWidgetItem(str(row[5])))
            self.table.setItem(count, 5, QTableWidgetItem(str(row[6])))
            self.table.setItem(count, 6, QTableWidgetItem(str(row[7])))
            self.table.setItem(count, 7, QTableWidgetItem(str(row[8])))
            #self.table.setItem(count, 8, QTableWidgetItem(str(row[9])))
            #self.table.setItem(count, 0, QTableWidgetItem(str(row[0])))
            
            
            count = count +1
        conn.close()
        
        
        
        
    def paintEvent(self, event):
        QMainWindow.paintEvent(self, event)
        
        painter = QPainter(self)
        #Top Header
        painter.setPen(QColor(255, 215, 0))
        painter.setBrush(QColor(255, 215, 0))
        painter.drawRect(0, 0, 1020, 80)  
        # TOP 1
        painter.setBrush(QColor(241, 249, 185))
        painter.setPen(QPen(Qt.black, 0.1, Qt.SolidLine))
        painter.drawRect(0, 80, 1020, 440)
        # TOP 2 
        painter.setPen(QPen(Qt.black, 0.1, Qt.SolidLine))
        painter.setPen(QColor(255, 215, 0))
        painter.setBrush(QColor(255, 215, 0))
        painter.drawRect(0, 520, 1020, 50)
        
    def update_time(self):
        label_time = QtCore.QDateTime.currentDateTime().toString("hh:mm:ss") 
        label_Date = QtCore.QDateTime.currentDateTime().toString("dd-MM-yyyy")
        self.Live_D.setText(label_Date)
        self.Live_T.setText(label_time)
        
        
        
class Home2Page(QWidget):
    def __init__(self):
        super().__init__()
        
        
        self.Home2_style = "color: white; font-weight: bold;   "#border: 2px solid white;"
        
        ####Center Start ####################
        self.Result_LB = QLabel("OK", self)
        self.Result_LB.resize(400, 60)
        self.Result_LB.setAlignment(Qt.AlignCenter)
        self.Result_LB.setFont(QFont('Times', 40))
        self.Result_LB.setStyleSheet(self.Home2_style)
        self.Result_LB.move(310, 140)
                
        self.LiveValue_LB = QLabel("00.000", self)
        self.LiveValue_LB.resize(600, 200)
        self.LiveValue_LB.setAlignment(Qt.AlignCenter)
        self.LiveValue_LB.setFont(QFont('Times', 100))
        self.LiveValue_LB.setStyleSheet(self.Home2_style)
        self.LiveValue_LB.move(210, 200)
        
        self.LiveValueP_LB = QLabel("ml/min", self)
        self.LiveValueP_LB.resize(400, 50)
        self.LiveValueP_LB.setAlignment(Qt.AlignCenter)
        self.LiveValueP_LB.setFont(QFont('Times', 40))
        self.LiveValueP_LB.setStyleSheet(self.Home2_style)
        self.LiveValueP_LB.move(310, 400)
        
        ####Center End ####################
        
        
        
        ####left Start ####################
        
#         self.BarValue_LB = QLabel("00.00", self)
#         self.BarValue_LB.resize(150, 50)
#         self.BarValue_LB.setAlignment(Qt.AlignLeft)
#         self.BarValue_LB.setFont(QFont('Times', 30))
#         self.BarValue_LB.setStyleSheet(self.Home2_style)
#         self.BarValue_LB.move(130, 120)
#         
#         self.BarValueP_LB = QLabel("bar", self)
#         self.BarValueP_LB.resize(150, 50)
#         self.BarValueP_LB.setAlignment(Qt.AlignLeft)
#         self.BarValueP_LB.setFont(QFont('Times', 30))
#         self.BarValueP_LB.setStyleSheet(self.Home2_style)
#         self.BarValueP_LB.move(130, 170)
        
        self.Program_LB = QLabel("Pr", self)
        self.Program_LB.resize(500, 50)
        self.Program_LB.setAlignment(Qt.AlignLeft)
        self.Program_LB.setFont(QFont('Times', 30))
        self.Program_LB.setStyleSheet(self.Home2_style)
        self.Program_LB.move(130, 420)
        
        
        
        
         ####left end ####################
        
        
        
        ####right Start ####################
        
        self.RightValue_LB = QLabel("00.00", self)
        self.RightValue_LB.resize(150, 50)
        self.RightValue_LB.setAlignment(Qt.AlignRight)
        self.RightValue_LB.setFont(QFont('Times', 30))
        self.RightValue_LB.setStyleSheet(self.Home2_style)
        self.RightValue_LB.move(740, 120)
        
        self.RightValueP_LB = QLabel("bar", self)
        self.RightValueP_LB.resize(150, 50)
        self.RightValueP_LB.setAlignment(Qt.AlignRight)
        self.RightValueP_LB.setFont(QFont('Times', 30))
        self.RightValueP_LB.setStyleSheet(self.Home2_style)
        self.RightValueP_LB.move(740, 170)
        
        self.Right_LB = QLabel("READY", self)
        self.Right_LB.resize(150, 50)
        self.Right_LB.setAlignment(Qt.AlignRight)
        self.Right_LB.setFont(QFont('Times', 30))
        self.Right_LB.setStyleSheet(self.Home2_style)
        self.Right_LB.move(740, 420)
        
        
        
        
         ####right end ####################
        
        
        self.Start_btn = QPushButton('START',self)
        self.Start_btn.resize(150,40)
        self.Start_btn.clicked.connect(self.start_timer)
        self.Start_btn.setFont(QFont('Times', 20, QFont.Bold))
        self.Start_btn.setStyleSheet("background-color : #00331a;");
        self.Start_btn.move(320,490)


        self.Stop_btn = QPushButton('STOP',self)
        self.Stop_btn.resize(150,40)
        self.Stop_btn.clicked.connect(self.Stop)
        self.Stop_btn.setFont(QFont('Times', 20, QFont.Bold))
        self.Stop_btn.setStyleSheet("background-color : #330000");
        self.Stop_btn.move(560,490)
        
        self.TS_LB = QLabel("1", self)
        self.TS_LB.setAlignment(Qt.AlignLeft)
        self.TS_LB.setFont(QFont('Times', 12))
        self.TS_LB.setStyleSheet("color: Black; font-weight: bold;  ")#  border: 1px solid black;")
        self.TS_LB.move(950, 320)
        self.TS_LB.resize(200,200)
        
        self.TE_LB = QLabel("2", self)
        self.TE_LB.setAlignment(Qt.AlignLeft)
        self.TE_LB.setFont(QFont('Times', 12))
        self.TE_LB.setStyleSheet("color: Black; font-weight: bold;  ")#  border: 1px solid black;")
        self.TE_LB.move(950, 350)
        self.TE_LB.resize(200,200)
        
        self.DP_LB = QLabel("DP : ", self)
        self.DP_LB.setAlignment(Qt.AlignRight)
        self.DP_LB.setFont(QFont('Times', 12))
        self.DP_LB.setStyleSheet("color: white; font-weight: bold; ")#  border: 1px solid white;")
        self.DP_LB.move(720, 510)
        self.DP_LB.resize(180,20)
        
        
        
        
        
        self.binary_str = ""
        
        self.flagstart = 0
        self.timer = QTimer(self)
        self.timer.start(1000)
        self.timer.timeout.connect(self.update_timer)
        
        self.remaining_time = 0
        self.totaltime = 0
        
        self.P1 = "Initialization"
        self.P2 = "Filling"
        self.P3 = "Stabilization"
        self.P4 = "Testing"
        self.P5 = "Release"
        
        self.P1_Ini = 0
        self.P2_Fill = 0
        self.P3_Stab = 0
        self.P4_Test = 0
        self.P5_Rel = 0
        self.delay = 0
        self.SetPressure = 0
        self.PressureMin = 0
        self.PressureMax = 0
        self.totaltime = 0
        self.TS = 0
        self.TE = 0
        
        self.style = "color: white; font-weight: bold;  "#border: 1px solid white;"
        
        self.StartTime=QLabel("Time remaining: 0 SEC",self)
        self.StartTime.setAlignment(Qt.AlignRight)
        self.StartTime.resize(200, 20)
        self.StartTime.setFont(QFont('Times', 12))
        self.StartTime.setStyleSheet(self.style)
        self.StartTime.move(700, 530)
        
        self.ProcesLB=QLabel("Process Name ",self)
        self.ProcesLB.setAlignment(Qt.AlignLeft)
        self.ProcesLB.resize(150, 20)
        self.ProcesLB.setFont(QFont('Times', 12))
        self.ProcesLB.setStyleSheet(self.style)
        self.ProcesLB.move(120, 530)
        
        self.ProcesLB1=QLabel("",self)
        self.ProcesLB1.setAlignment(Qt.AlignCenter)
        self.ProcesLB1.resize(150,20)
        self.ProcesLB1.setFont(QFont('Times', 15))
        self.ProcesLB1.setStyleSheet(self.style)
        self.ProcesLB1.move(435, 530)
        
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(int(self.totaltime))
        self.progress_bar.setFont(QFont('Arial', 8)) 
        self.progress_bar.move(120, 550)
        self.progress_bar.resize(780,10)
        
        self.DPtimer = QTimer()
        self.DPtimer.timeout.connect(self.updateDP)
        
        self.DPtimer.start(100)
        
        self.DPC = 0
        self.TotalA = 0
        
        
        self.ProgramNo = "";
        self.PressureUnit = "";
        self.Pressure = ""
        self.Leak = ""
        self.LeakUnit = ""
        self.Result1 = ""
        self.ProductionCount  = 0
        self.ADS_AV = 0
        self.checkPro = 0
        self.volumn = 0
        self.TestDateTime = ""
        self.AllowLeakTest = 0
        self.AllowReffLeak = 0
        
        self.SetTesting()
        
        self.Backcolor1 = QColor(225, 225, 0)  #Yellow
        self.Backcolor2 = QColor(255, 0, 0)   #Red
        self.Backcolor3 = QColor(0, 128, 0)		#Green
        self.ChangeBack = QColor(225, 225, 0)
        
    def paintEvent(self, event):
        # Create a QPainter instance for the widget
        painter = QPainter(self)
        
        brush = QBrush(Qt.black)
        painter.setBrush(brush)
        
        painter.drawRect(0, 0, 1020, 720)
        
#         #brush = QBrush(Qt.self.Backcolor3, Qt.SolidPattern)
        #brush = QBrush(Qt.Yellow)
        #painter.setBrush(brush)
        painter.setBrush(self.ChangeBack)
        
        
        
        # Draw the rectangle (x, y, width, height)
        painter.drawRect(0, 0, 120, 720)
        painter.drawRect(900, 0, 120, 720)
        painter.drawRect(120, 100, 780, 5)
        painter.drawRect(120, 480, 780, 5)
        
    
    def SetTesting(self):
        
        Srows = getdata('Select * From Conversion')
        
        conn = sqlite3.connect(connstring)
        cur = conn.cursor()
        cur.execute('SELECT * from Programs where "Set" = "1"')
        rows = cur.fetchall()
        #print("row " + str(len(rows)))
        self.checkPro = len(rows)
        if len(rows) == 0 :
            #self.Program_MSg.setText("Program not selected..")
            self.Program_LB.setText("Program not selected..")
        else:
            count = 0
            for row in rows:
                self.ProgramNo = str(row[1])
                #self.Mode_lb.setText("Test Mode : Leak")
                self.Program_LB.setText("Pr " + str(row[1]))
                #self.PartNo_TB.setText("" + str(row[0]))
                #self.ProdCount_lb.setText(str(row[0]))
                #self.FillPressure_lb.setText("Fill Pressure : " +str(row[2]))
                #self.Leak_lb.setText("Leak : " +str(row[0]))
                #self.Result_lb.setText(str(row[0]))
                
                self.P1_Ini = row[6]/100
                self.P2_Fill = row[2]/100
                self.P3_Stab = row[3]/100
                self.P4_Test = row[4]/100
                self.P5_Rel = row[5]/100
                #self.delay = int(row[6])
                self.SetPressure = round(row[7], 3)  #convert to mbar
                self.PressureMin = round(row[9], 3)
                self.PressureMax = round(row[10], 3)
                self.PressureUnit = str(row[8])
                
                #self.LiveValueP_LB.setText()
                self.RightValueP_LB.setText(self.PressureUnit)
                
                #self.PU_lb.setText("Pressure Unit : " + str(self.PressureUnit))
                #print(self.PressureUnit)
                
#                 for r1 in Srows:
#                     if r1[2] == self.PressureUnit:
#                         
#                         self.SetPressure = round((abs(float(r1[0])) + abs(float(r1[1]))/3200) * row[7], 3)  #convert to mbar
#                         self.PressureMin = round((abs(float(r1[0])) + abs(float(r1[1]))/3200) * row[9], 3)
#                         self.PressureMax = round((abs(float(r1[0])) + abs(float(r1[1]))/3200) * row[10], 3)
                
                self.AllowLeakTest = row[11]	#Positive
                #print(self.AllowLeakTest)
                self.AllowReffLeak = -row[12]   #Negitve
                self.LeakUnit = str(row[13])
                #print(self.LeakUnit)
                self.volumn = round(row[15], 3)
                #print(self.volumn)
                
                #print(self.AllowLeakTest)
                #print(str(self.SetPressure) + str("\n") + str(self.PressureMin) + str("\n") + str(self.PressureMax))
                
                
                
                self.totaltime =  self.P1_Ini + self.P2_Fill + self.P3_Stab + self.P4_Test + self.P5_Rel 
                self.totaltime = self.totaltime #Msec conver second
                #print(self.totaltime)
                
        conn.commit()
        conn.close()
        
        
        
    def Result_Store(self):
        
        conn = sqlite3.connect(connstring)
        cur = conn.cursor()
        cur.execute('SELECT * from Results ')
        row = cur.fetchone()
        self.ProductionCount = 1
        if row:
            print("Check 1 : " + str(row))
            self.ProductionCount = int(row[8]) +  1
        else:
            self.ProductionCount = 1
        
        #self.ProductionCount = cur.fetchone()[0]
        #print(self.ProductionCount)
        conn.close()
        
        self.TestDateTime = QtCore.QDateTime.currentDateTime().toString("dd-MM-yyyy") + " " + QtCore.QDateTime.currentDateTime().toString("hh:mm:ss")
        
        count = SaveReport(str(self.ProgramNo) , str(self.TestDateTime) , str(self.SetPressure)  , str(self.PressureUnit) , str(self.Leak)  , self.LeakUnit , str(self.Result) )
        
        print(count)
        
        Query = 'INSERT INTO Results("ProgramNo", "TestDateTime", "Pressure", "PressureUnit", "Leak", "LeakUnit", "Result", "ProductionCount") VALUES ("' + str(self.ProgramNo) + '", "' + str(self.TestDateTime) + '","' + str(self.SetPressure) + '", "' + str(self.PressureUnit) + '", "' + str(self.Leak) + '", "' + self.LeakUnit + '", "' + str(self.Result) + '", "' + str(self.ProductionCount) + '")'
        
        #print(Query)
        MyNonQuery(Query)
            #self.updatetable()
        
    def start_timer(self):
        self.RightValue_LB.setText("0.00")
        self.TE_LB.setText("2")
        self.TS_LB.setText("1")
        self.DPC = 0
        self.DP_LB.setText("")
        #self.Program_MSg.setText("")
        self.SetTesting()
        if self.checkPro == 0:
            #self.Program_MSg.setText("Program not selected..")
            self.Program_LB.setText("Program not selected..")
        else:
            GPIO.output(RELAY_PIN1, GPIO.LOW)
            GPIO.output(RELAY_PIN2, GPIO.LOW)
            GPIO.output(RELAY_PIN3, GPIO.LOW)
            GPIO.output(RELAY_PIN4, GPIO.LOW)
            
            GPIO.output(RELAY_PIN5, GPIO.HIGH)
            GPIO.output(RELAY_PIN6, GPIO.HIGH)
            GPIO.output(RELAY_PIN7, GPIO.HIGH)
            GPIO.output(RELAY_PIN8, GPIO.HIGH)
           
            if PS == 0:
                
                input_value = read_gpio_as_int()
                reversed_value = reverse_bits(input_value, NUM_BITS)
                #print(f"Original Value (Dec): {input_value} (Bin: {format(input_value, '08b')})")
                #print(f"Reversed Value (Dec): {reversed_value} (Bin: {format(reversed_value, '08b')})")
                #self.P_LB.setText(str(reversed_value))
                
                conn = sqlite3.connect(connstring)
                cur = conn.cursor()
                cur.execute('SELECT count(*) from Programs where ProgramNo = "' + str(reversed_value) + '"')
                result = cur.fetchone()
                row_count = result[0]
                print("Number of rows in the table:", row_count)
                conn.commit()
                conn.close()
                if row_count == 0:
                    #self.Program_MSg.setText("Program Selection no available")
                    print("Program Selection no available")
                elif row_count == 1:
                    
                    self.SetTesting()
                    
                    if(int(self.ProgramNo) == int(reversed_value)):
                        print("Program allready selected")
                    else:
                        self.setupEvents1()
                        #print(self.data1)
                        for i in range(0, len(self.data1)):
                            Query = 'UPDATE Programs SET "Set" = 0 Where "ProgramNo" =  "' + str(self.data1[i]) + '"'
                            MyNonQuery(Query)
                        
                        Query = 'UPDATE Programs SET "Set" = 1 Where "ProgramNo" =  "' + str(reversed_value) + '"'
                        #print(Query)
                        MyNonQuery(Query)
                        
                        self.SetTesting()
                        
                        self.Program_MSg.setText("Selected Program " + str(self.ProgramNo))
                        
                        
                        
            else:
                self.SetTesting()
                self.Program_MSg.setText("Selected Program " + str(self.ProgramNo))
                    
            self.progress_bar.setMinimum(0)
            self.progress_bar.setMaximum(int(self.totaltime))
            self.remaining_time = self.totaltime
            
            if self.remaining_time > 0:
                self.timer.start(100)  # Start timer for 1000 milliseconds (1 second)
                self.StartTime.setText(f'Time remaining: {self.remaining_time} SEC')
                self.Stop_btn.setStyleSheet("background-color : #330000");
                self.Start_btn.setStyleSheet("background-color : #00cc66")
            else:
                self.StartTime.setText('Please enter a positive number.')
                self.Start_btn.setStyleSheet("background-color : #00331a");
        
    def Stop(self):     #Stop_btn click event
        self.Start_btn.setStyleSheet("background-color : #00331a");
        self.Stop_btn.setStyleSheet("background-color : #e60000")
        self.timer.stop()
        self.DPtimer.stop()
        self.remaining_time = 0
        self.StartTime.setText(f'Time remaining: {self.remaining_time} SEC')
        self.ProcesLB.setText("Process : ")
        self.progress_bar.setValue(0)
        GPIO.output(RELAY_PIN1, GPIO.LOW)
        GPIO.output(RELAY_PIN2, GPIO.LOW)
        GPIO.output(RELAY_PIN3, GPIO.LOW)
        GPIO.output(RELAY_PIN4, GPIO.LOW)
        
    def updateDP(self):
        #print("hello")
        self.SetTesting()
        self.DPC = self.DPC + 1
        #print("Count : " + str(self.DPC))
        T1 = self.TS_LB.text()
        T2 = self.TE_LB.text()
        
        #print("ct "+ str(self.DPC) + " T1 " + str(T1) + " T2 " + str(T2) + " "  + str((float(T1) - float(T2))/self.DPC))
        #print("self.LeakUnit : " + str(self.LeakUnit))
        P = get_Convert(float(T2), self.LeakUnit, (self.P4_Test/10), self.volumn)
         #P = get_Convert((float(T1) - float(T2)), self.LeakUnit, (self.P4_Test/10), self.volumn)
        
        self.TotalA = self.TotalA + round(P, 3)
        if(self.DPC == 9):
            #print("Count " + str(self.DPC) + " " +str(self.LeakUnit) + " : "  + str(round(P, 3))  + " Total : " +  str(round(self.TotalA, 2)) + " A : "+ str(round(self.TotalA, 2)/self.DPC))
            #self.DP_LB.setText(str(self.LeakUnit) + " : "  + str(round(P, 3)) + " A : "+ str(round((self.TotalA/self.DPC), 2)))
          
            self.DPC = 0
            self.TotalA = 0
        #else:
            #print("Count " + str(self.DPC) + " " +str(self.LeakUnit) + " : "  + str(round(P, 3)))
            
    def update_timer(self):
        self.SetTesting()
        #print("P " + str(self.SetPressure))
        #print("PressureUnit " + str(self.PressureUnit))
        #print("check Start flag " + str(self.flagstart))
        
        if self.remaining_time > 0:
            self.TS = ""
            self.TE = ""
            self.ADS_AV = 0
            self.ADS_AV2 = 0
            self.Leak = 0
            self.Result = 0
            #print(self.PressureUnit)
            self.LiveValueP_LB.setText(self.PressureUnit)
             
            self.RightValueP_LB.setText(self.PressureUnit)
            
            
            
            if self.PressureUnit == "mBar":
                self.ADS_AV = get_UNIT()[3]
                self.ADS_AV2 = get_UNIT2()[3]
                #
            elif self.PressureUnit == "Bar":
                self.ADS_AV = get_UNIT()[4]
                self.ADS_AV2 = get_UNIT2()[4]
            elif self.PressureUnit == "PSI":
                self.ADS_AV = get_UNIT()[5]
                self.ADS_AV2 = get_UNIT2()[5]
            #print("a01 " + str(self.ADS_AV))  
            if self.ADS_AV > self.PressureMax:
                self.timer.stop()
                self.DPtimer.stop()
                self.ProcesLB.setText("Process : High Pressure")
                self.StartTime.setText("Time remaining: 0 SEC")
                self.ChangeBack = self.Backcolor2
                self.update()
                self.Result_LB.setText("High Pressure")
                GPIO.output(RELAY_PIN5, GPIO.LOW)
                GPIO.output(RELAY_PIN6, GPIO.LOW)
                self.remaining_time=0
            else:
                #print(self.P1_Ini + self.P2_Fill + self.P3_Stab + self.P4_Test - 3)
                #print("rem " + str(self.remaining_time))
                
                if float(self.remaining_time) == float(self.totaltime - int(self.P1_Ini + self.P2_Fill + self.P3_Stab)):
                    
                    self.DPtimer.start()  # Update every 100ms
                    self.TS  = self.ADS_AV
                    self.TS_LB.setText(str(self.ADS_AV))
                    self.RightValue_LB.setText(str(self.ADS_AV))
                    
                    
                    #print("TS ", self.TS)
                if self.remaining_time <= self.totaltime - int(self.P1_Ini + self.P2_Fill + self.P3_Stab) and self.remaining_time >= self.totaltime - int(self.P1_Ini + self.P2_Fill + self.P3_Stab + self.P4_Test- 20):
                    
                    self.TE  = self.ADS_AV2
                    self.TE_LB.setText(str(self.ADS_AV2))
                    
                    #P = get_Convert(float(self.TE), self.LeakUnit, (self.P4_Test/10), self.volumn)
                    #print("value " + str(P) + " AllowReffLeak : " + str(self.AllowReffLeak) + " AllowLeakTest : " + str(self.AllowLeakTest))
                    self.LiveValue_LB.setText(str(self.ADS_AV2))
                    
                    #print("TE", self.TE)
                
                #if float(self.remaining_time) == float(self.totaltime - int(self.P1_Ini + self.P2_Fill + self.P3_Stab + self.P4_Test)):
                    
                #print("TS ", self.TS)
                #print("TE", self.TE)
                
                if float(self.remaining_time) <= float(self.totaltime - int(self.P1_Ini + self.P2_Fill + self.P3_Stab + self.P4_Test)) and float(self.remaining_time) >= float(self.totaltime - int(self.P1_Ini + self.P2_Fill + self.P3_Stab+ self.P4_Test + self.P5_Rel)):
                    self.DPtimer.stop()
                    self.ProcesLB.setText("Process : " + self.P5) #Result
                    self.LiveValueP_LB.setText(self.LeakUnit)
                    
                    
                    #print("remaining_time : " + str(self.remaining_time) + " e " + str((self.totaltime + 1) - int(self.P1_Ini + self.P2_Fill + self.P3_Stab+ self.P4_Test + self.P5_Rel)))
                    if float(self.remaining_time) == float(self.totaltime - int(self.P1_Ini + self.P2_Fill + self.P3_Stab + self.P4_Test + 10)):
                        GPIO.output(RELAY_PIN4, GPIO.HIGH)
                        self.Result_LB.setText(self.P5)
                        self.update()
                        
                    if float(self.remaining_time) == float(self.totaltime - int(self.P1_Ini + self.P2_Fill + self.P3_Stab + self.P4_Test )):
                        print("Relase Time")
                        
                        GPIO.output(RELAY_PIN3, GPIO.LOW)
                        
                        
                    
                    if self.remaining_time <= self.totaltime - int(self.P1_Ini + self.P2_Fill + self.P3_Stab) and self.remaining_time >= self.totaltime - int(self.P1_Ini + self.P2_Fill + self.P3_Stab + self.P4_Test):
                        
                        T1 = self.TS_LB.text()
                        T2 = self.TE_LB.text()
                        #print(str(T1) + " " + str(T2))
                        
                        #print("Test time L " + str(self.LeakUnit))
                        #P = get_Convert(float(T2), self.LeakUnit, (self.P4_Test/10), self.volumn)
                        #print("value " + str(P) + " AllowLeakTest " + str(self.AllowLeakTest))
                        
                        P = T2
                        
                        #print("value " + str(P) + " AllowReffLeak : " + str(self.AllowReffLeak) + " AllowLeakTest : " + str(self.AllowLeakTest))
                        
                        
                        #self.DP_LB.setText("Count " + str(self.DPC) + " " +str(self.LeakUnit) + " : "  + str(round(P, 3)) + " A :" + str(round(self.TotalA, 3)))
                    
                        if float(self.AllowReffLeak) >= float(P):
                            self.Result = "NG"
                            
                            self.ProcesLB1.setText("Process : Reffernce Reject")
                            self.Result_LB.setText(self.Result)
                            self.ChangeBack = self.Backcolor2
                            self.update()
                            GPIO.output(RELAY_PIN5, GPIO.LOW)
                        elif float(self.AllowLeakTest) <= float(P):
                            self.Result = "NG"
                            self.ProcesLB1.setText("Process : Part Raject")
                            self.Result_LB.setText(self.Result)
                            self.ChangeBack = self.Backcolor2
                            self.update()
                            GPIO.output(RELAY_PIN6, GPIO.LOW)
                        else:
                            self.Result = "OK"
                            self.ProcesLB1.setText("Process : Part Ok")
                            self.Result_LB.setText(self.Result)
                            self.ChangeBack = self.Backcolor3
                            self.update()
                            
                            
                            GPIO.output(RELAY_PIN7, GPIO.LOW)
                            #GPIO.output(RELAY_PIN1, GPIO.LOW)
                            #GPIO.output(RELAY_PIN3, GPIO.LOW)
                            
                            GPIO.output(RELAY_PIN1, GPIO.LOW)
                            GPIO.output(RELAY_PIN4, GPIO.LOW)
                        
                        self.Result_Store()
                        self.Pressure = T1
                        self.Leak = T2
                        self.PressureUnit = self.PressureUnit
                        
                        
                        
                    
                    #self.ProcesLB.setText("Process : Part Ok")
                    
                    
                    
                        
                elif self.remaining_time <= self.totaltime - int(self.P1_Ini + self.P2_Fill + self.P3_Stab) and self.remaining_time >= self.totaltime - int(self.P1_Ini + self.P2_Fill + self.P3_Stab + self.P4_Test):
                    self.ProcesLB.setText("Process : " + self.P4) #Testing
                    self.LiveValueP_LB.setText(self.LeakUnit)
                    self.Result_LB.setText(self.P4)
                    self.update()
                    GPIO.output(RELAY_PIN3, GPIO.HIGH)
                    
                    
                    
                    
                        
                        
                
                    
                    
                        #self.update()
                        
                        
                elif self.remaining_time <= self.totaltime - int(self.P1_Ini + self.P2_Fill) and self.remaining_time >= self.totaltime - int(self.P1_Ini + self.P2_Fill + self.P3_Stab):
                    self.ProcesLB.setText("Process : " + self.P3) #Stab
                    
                    
                    self.LiveValue_LB.setText(str(self.ADS_AV))
                    
                    
                    
                    self.Result_LB.setText(self.P3)
                    GPIO.output(RELAY_PIN2, GPIO.LOW)
                    
                    if self.ADS_AV > self.PressureMax:
                        #print("High Pressure")
                        self.ProcesLB1.setText("High Pressure")
                        self.Result_LB.setText("High Pressure")
                        self.ChangeBack = self.Backcolor2
                        self.update()
                        GPIO.output(RELAY_PIN5, GPIO.LOW)
                        GPIO.output(RELAY_PIN6, GPIO.LOW)
                        
                    else:
                        #print("OK")
                        self.ProcesLB1.setText("Pressure OK")
                        #self.Result_LB.setText("Pressure OK")
                        #self.ChangeBack = self.Backcolor3
                    
                    
                elif self.remaining_time <= int(int(self.totaltime) - int(self.P1_Ini)) and self.remaining_time >= self.totaltime - int(self.P1_Ini + self.P2_Fill):
                    self.ProcesLB.setText("Process : " + self.P2) #Filling
                    self.Result_LB.setText(self.P2)
                    print("ADS_AV " + str(self.ADS_AV) + " PressureMin " + str(self.PressureMin) + " PressureMax " + str(self.PressureMax))
                    
                    
                    
                    if self.ADS_AV < self.PressureMin:
                        #print("Low Pressure")
                        GPIO.output(RELAY_PIN5, GPIO.LOW)
                        GPIO.output(RELAY_PIN6, GPIO.LOW)
                        
                        self.ProcesLB1.setText("Low Pressure")
                        self.Result_LB.setText("Low Pressure")
                        self.ChangeBack = self.Backcolor2
                        self.update()
                        
                        self.Start_btn.setStyleSheet("background-color : #00331a");
                        GPIO.output(RELAY_PIN1, GPIO.LOW)
                        GPIO.output(RELAY_PIN2, GPIO.LOW)
                        GPIO.output(RELAY_PIN3, GPIO.LOW)
                        GPIO.output(RELAY_PIN4, GPIO.LOW)
                        self.Stop_btn.setStyleSheet("background-color : #e60000");
                        self.DPtimer.stop()
                        self.timer.stop()
                    
                    else:
                        #print("OK")
                        self.ProcesLB1.setText("Pressure OK")
                        #self.Result_LB.setText("Pressure OK")
                        #self.ChangeBack = self.Backcolor3
                        
                    
                    
                    GPIO.output(RELAY_PIN2, GPIO.HIGH)
                    #print("SetPressure " + str(self.SetPressure))
                    if self.ADS_AV == self.SetPressure :
                        #print("Air Relase")
                        self.ProcesLB1.setText("Air Relase")
                        self.Result_LB.setText("Air Relase")
                    else:
                        #print("Air Fill")
                        self.ProcesLB1.setText("Air Fill " + str(self.ADS_AV))
                        self.LiveValue_LB.setText(str(self.ADS_AV))
                        
                    #print("R :"+str(self.remaining_time)+ " IS : " + str(int(int(self.totaltime) - int(self.P1_Ini))) + " IE" + str(self.totaltime - int(self.P1_Ini + self.P2_Fill)))
                      
                
                
                elif self.remaining_time <= int(int(self.totaltime)) and self.remaining_time >= self.totaltime - int(self.P1_Ini):
                    
                    #print("R :"+str(self.remaining_time)+ " IS : " + str(self.totaltime) + " IE" + str(self.totaltime - int(self.P1_Ini)))
                    self.LiveValue_LB.setText("00.00")
                    self.ChangeBack = self.Backcolor1
                    self.update()
                    self.ProcesLB.setText("Process : " + self.P1) #inI
                    self.Result_LB.setText(self.P1)
                    GPIO.output(RELAY_PIN1, GPIO.HIGH)
                    #self.ProcesLB1.setText("")
                    
                    
                    
                
                
                self.Start_btn.setStyleSheet("background-color : Green");
                self.remaining_time -= 1
                self.StartTime.setText(f'Time remaining: {round(self.remaining_time/10)} SEC')
                
                self.progress_bar.setValue(int(self.totaltime) - int(self.remaining_time))
            
            
            
        else:
            self.timer.stop()
            
            #self.StartTime.setText('Process : Completed')
            
            
            #self.ProcesLB1.setText("")
            
            GPIO.output(RELAY_PIN1, GPIO.LOW)
            GPIO.output(RELAY_PIN2, GPIO.LOW)
            GPIO.output(RELAY_PIN3, GPIO.LOW)
            GPIO.output(RELAY_PIN4, GPIO.LOW)
            
            #self.Start_btn.setStyleSheet("background-color : #00331a");
            #self.Stop_btn.setStyleSheet("background-color : #e60000");
        
        
    
        

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec_())
