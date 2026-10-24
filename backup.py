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
GPIO.output(RELAY_PIN9, GPIO.HIGH)
GPIO.output(RELAY_PIN10, GPIO.HIGH)
GPIO.output(RELAY_PIN11, GPIO.HIGH)
GPIO.output(RELAY_PIN12, GPIO.HIGH)


# Set up GPIO
pins = [19, 13, 6, 5, 9, 10]  # Example GPIO pin numbers output pin
GPIO.setmode(GPIO.BCM)  # Use BCM pin numbering
for pin in pins:
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)  # Set pins as input with pull-down resistors
        

PS = 0

#DataBase Connection string
connstring = "/home/admin/LeakageTesting/LeakageTesting.db"

def MyNonQuery(Query):
    conn = sqlite3.connect(connstring)
    cur = conn.cursor()
    cur.execute(Query)
    print("Record Insert - " + Query)
    conn.commit() 
    conn.close()



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
        self.settings_page = SettingsPage()
        self.setup_page = LoginPage()
        self.about_page = AboutPage()
       # self.login_page = LoginPage()
        self.login_form_page = LoginFormPage()

        self.stacked_widget.addWidget(self.home_page)
        self.stacked_widget.addWidget(self.settings_page)
        self.stacked_widget.addWidget(self.setup_page)
        self.stacked_widget.addWidget(self.about_page)
       # self.stacked_widget.addWidget(self.login_page)
        self.stacked_widget.addWidget(self.login_form_page)
        
        
        
        self.login_form_page.login_successful.connect(self.on_login_success)

        # Toolbar
        self.toolbar = QToolBar("Main Toolbar")
        self.addToolBar(Qt.BottomToolBarArea, self.toolbar)
        
        

        # Toolbar actions
        self.action_home = QAction("Home", self)
        self.action_home.triggered.connect(self.show_home)

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

        self.action_about = QAction("About", self)
        self.action_about.triggered.connect(self.show_about)

        self.action_exit = QAction("Exit", self)
        self.action_exit.triggered.connect(self.close)

        # Initial toolbar setup
        self.setup_toolbar(home=True, login=True)
        
        self.setup_page.switch_to_home.connect(self.show_home)

        # Optional signal connection
        self.settings_page.select_clicked.connect(self.show_home)

        # Show home page first
        self.show_home()

    def setup_toolbar(self, home=False, login=False,setup=False, logout=False,
                      back=False, settings=False, about=False, exit_app=False):
        self.toolbar.clear()
        

        if home:
            self.toolbar.addAction(self.action_home)

        if settings:
            self.toolbar.addAction(self.action_settings)
            
        if setup:
            self.toolbar.addAction(self.action_setup)
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

    def show_settings(self):
        self.stacked_widget.setCurrentWidget(self.settings_page)

    def show_about(self):
        self.stacked_widget.setCurrentWidget(self.about_page)

    def handle_login(self):
        self.stacked_widget.setCurrentWidget(self.login_form_page)
        self.setup_toolbar(home=True, back=True)

    def on_login_success(self):
        #self.stacked_widget.setCurrentWidget(self.login_page)
        self.stacked_widget.setCurrentWidget(self.setup_page)
        self.setup_toolbar(home=True, settings=True, about=False, exit_app=False, logout=True, setup=True,)

    def handle_logout(self):
        self.stacked_widget.setCurrentWidget(self.home_page)
        self.setup_toolbar(home=True, login=True)

    def go_back_to_home(self):
        self.stacked_widget.setCurrentWidget(self.home_page)
        self.setup_toolbar(home=True, login=True)
        
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
        relay_label = QLabel("Relay Control- R1 - R4 \nMosfet - R5 - R8 \nLED - R9 - R12")
        relay_label.setFont(QFont('Times', 12))
        relay_label.setAlignment(Qt.AlignLeft)
        relay_layout.addWidget(relay_label)
        
        
        self.relay_buttons = []
        for i in range(1, 13):
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
            
        if GPIO.input(RELAY_PIN9) == 0:
            self.relay_buttons[8].setStyleSheet("background-color : Red");
        elif GPIO.input(RELAY_PIN9) == 1:
            self.relay_buttons[8].setStyleSheet("background-color : Gray");
            
        if GPIO.input(RELAY_PIN10) == 0:
            self.relay_buttons[9].setStyleSheet("background-color : Red");
        elif GPIO.input(RELAY_PIN10) == 1:
            self.relay_buttons[9].setStyleSheet("background-color : Gray");

        if GPIO.input(RELAY_PIN11) == 0:
            self.relay_buttons[10].setStyleSheet("background-color : Red");
        elif GPIO.input(RELAY_PIN11) == 1:
            self.relay_buttons[10].setStyleSheet("background-color : Gray");

        if GPIO.input(RELAY_PIN12) == 0:
            self.relay_buttons[11].setStyleSheet("background-color : Red");
        elif GPIO.input(RELAY_PIN12) == 1:
            self.relay_buttons[11].setStyleSheet("background-color : Gray");
        relay_group.setLayout(relay_layout)
        main_layout.addWidget(relay_group)
        
        adc_group = QGroupBox("")
        adc_group.setFont(QFont('Times', 16, QFont.Bold))
        adc_layout = QHBoxLayout()

        adc_label = QLabel("ADS Status")
        adc_label.setFont(QFont('Times', 14))
        adc_label.setAlignment(Qt.AlignLeft)

        self.ADS_LB = QLabel("")
        self.ADS_LB.setFont(QFont('Times', 14))
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
            self.ADS_LB.setText(str(v2))
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
        
        
        self.binary_str = ""
        
        self.flagstart = 0
        self.timer = QTimer(self)
        #self.timer.start(1000)
        self.timer.timeout.connect(self.update_timer)
        
        self.remaining_time = 0
        self.totaltime = 0
        
        self.P1 = "Initialization"
        self.P2 = "Filling"
        self.P3 = "Stabilization"
        self.P4 = "Testing"
        self.P5 = "Result"
        
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
        
        self.SetTesting()
        
        self.ProcesLB2=QLabel("Process Total Time1 - " + str(self.totaltime) + " Sec ", self)
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
        
        self.P5_LB=QLabel(self.P5 + str("\n") + str(self.P5_Rel * 1000),self)
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
        self.ADS_LB.setFont(QFont('Times', 12))
        self.ADS_LB.setStyleSheet("color: Black; font-weight: bold;  ")#  border: 1px solid black;")
        self.ADS_LB.move(840, 320)
        self.ADS_LB.resize(200,200)
        
        self.P_LB = QLabel("", self)
        self.P_LB.setAlignment(Qt.AlignLeft)
        self.P_LB.setFont(QFont('Times', 12))
        self.P_LB.setStyleSheet("color: Black; font-weight: bold;  ")#  border: 1px solid black;")
        self.P_LB.move(840, 80)
        self.P_LB.resize(200,200)
        
        
        #self.ViewResult()
        
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
        
        self.ProgramNo = "";
        self.PressureUnit = "";
        self.Pressure = ""
        self.Leak = ""
        self.LeakUnit = ""
        self.Result = ""
        self.ProductionCount  = 0
        self.ADS_AV = 0
        self.PU = ""
        
        
        
        
    def update_gpio_states(self):
        #4GPIO PIN USER FOR PROGRAM SELECTION
        global PS
        
        if PS == 0:
            t1 = str(GPIO.input(19)) +  str(GPIO.input(13)) + str(GPIO.input(6))  + str(GPIO.input(5))
            self.P_LB.setText(str(int(t1, 2)))
            #print(int(t1, 2))
        else:
            self.P_LB.setText("No Selection")
        
        
        
        #2 GPIO PIN FOR START AND STOP
        text = ""
        for i, pin in enumerate(pins):
            state = GPIO.input(pin)
            #self.labels[i].setText(f'GPIO Pin {pin}: {"HIGH" if state else "LOW"}')
            text += f'GPIO Pin {pin}: {"HIGH" if state else "LOW"}' + "\n"
            if pin == 9:
                if state == 0:
                    self.flagstart = 1
                    
            if pin == 10:
                if state == 0:
                    self.flagstart = 2
            i
              
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
        
        self.P1_LB.setText(self.P1 + str("\n") + str(self.P1_Ini * 1000))
        self.P2_LB.setText(self.P2 + str("\n") + str(self.P2_Fill * 1000))
        self.P3_LB.setText(self.P3 + str("\n") + str(self.P3_Stab * 1000))
        self.P4_LB.setText(self.P4 + str("\n") + str(self.P4_Test * 1000))
        self.P5_LB.setText(self.P5 + str("\n") + str(self.P5_Rel * 1000))
        
        #self.ProcesLB.setText("Process Total Time - " + str(self.totaltime) + " Sec ")
        self.ProcesLB2.setText("Process Total Time - " + str(self.totaltime) + " Sec ")
        
        
        if adc_available:
            #v2 = "AV : " +  str( channel1.value) +  "\nV  : "+ str(round(channel1.voltage, 2))
            v2 = "AV : " +  str( channel1.value) +  "\nV  : "+ str(channel1.voltage)
            
            #self.ADS_LB.setText(str(v1) + str(v2) + str(v3) + str(v4))
            #self.ADS_AV = channel1.voltage * 1000 #milevolt
            self.ADS_AV = round((7000/3520) * (channel1.voltage * 1000), 3) # mbar
            
            
            self.ADS_LB.setText(str(v2) + str("\n MV : ")
                                + str(channel1.voltage * 1000)
                                + str("\n MBar : "+ str(self.ADS_AV)))
            
        else:
            self.ADS_LB.setText("Error : ADC Harware not detected.")
        
        
        
        
   
        
        
    def SetTesting(self):
        conn = sqlite3.connect(connstring)
        cur = conn.cursor()
        cur.execute('SELECT * from Programs where "Set" = "1"')
        rows = cur.fetchall()
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
            
            self.P1_Ini = row[6]/1000
            self.P2_Fill = row[2]/1000
            self.P3_Stab = row[3]/1000
            self.P4_Test = row[4]/1000
            self.P5_Rel = row[5]/1000
            #self.delay = int(row[6])
            self.SetPressure = round((7000/3520) * row[7], 3)  #convert to mbar
            self.PressureMin = round((7000/3520) * row[9], 3)
            self.PressureMax = round((7000/3520) * row[10], 3)
            
            #print(str(self.SetPressure) + str("\n") + str(self.PressureMin) + str("\n") + str(self.PressureMax))
            
            
            
            self.totaltime =  self.P1_Ini + self.P2_Fill + self.P3_Stab + self.P4_Test + self.P5_Rel 
            self.totaltime = self.totaltime #Msec conver second
            #print(self.totaltime)
            
            
            
            
        conn.commit()
        conn.close()
        
        
        
    def Result(self):
        conn = sqlite3.connect(connstring)
        cur = conn.cursor()
        cur.execute('SELECT * from Results')
        self.ProductionCount = cur.fetchone()[0]
        #print(self.ProductionCount)
        conn.close()
        
        self.TestDateTime = QtCore.QDateTime.currentDateTime().toString("dd-MM-yyyy") + " " + QtCore.QDateTime.currentDateTime().toString("hh:mm:ss")
        Query = 'INSERT INTO Results("ProgramName", "TestDateTime", "Pressure", "PressureUnit", "Leak", \
                                        "LeakUnit", "Result", "ProductionCount")\
                                        VALUES ("' + self.ProgramNo + '", "' + self.TestDateTime + '",\
                                               "' + self.Pressure + '", "' + self.PressureUnit + '"\
                                        , "' + self.Leak + '", "' + self.LeakUnit + '"\
                                        , "' + self.Result + '", "' + self.ProductionCount + '")'
            #MyNonQuery(Query)
            #self.updatetable()
        
        
    def ViewResult(self):
        print("view")
        self.table = QTableWidget(self)
        self.table.setRowCount(40)
        self.table.setColumnCount(8)
        self.table.verticalHeader().setVisible(False)
        self.table.setFont(QFont('Times', 8))
        
        self.table.setHorizontalHeaderLabels(["ProgramName", "TestDateTime", "Pressure", "PressureUnit", "Leak", \
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
        
       
       self.remaining_time = self.totaltime
       
       if self.remaining_time > 0:
           self.timer.start(1000)  # Start timer for 1000 milliseconds (1 second)
           self.StartTime.setText(f'Time remaining: {self.remaining_time} SEC')
           self.Stop_btn.setStyleSheet("background-color : #330000");
           self.Start_btn.setStyleSheet("background-color : #00cc66");
       else:
            self.StartTime.setText('Please enter a positive number.')
            self.Start_btn.setStyleSheet("background-color : #00331a");
        
    def Stop(self):     #Stop_btn click event
        self.Start_btn.setStyleSheet("background-color : #00331a");
        self.Stop_btn.setStyleSheet("background-color : #e60000")
        self.timer.stop()
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
        
        
        
    def update_timer(self):
        
        #print("check Start flag " + str(self.flagstart))
        if self.remaining_time > 0:
            
            self.ADS_AV = round((7000/3520) * (channel1.voltage * 1000), 3) # mbar
            if self.ADS_AV > self.PressureMax:
                self.timer.stop()
                self.ProcesLB.setText("Process : High Pressure")
                self.StartTime.setText("Time remaining: 0 SEC")
                self.remaining_time=0
            else:
                
                if self.remaining_time <= self.totaltime - int(self.P1_Ini + self.P2_Fill + self.P3_Stab + self.P4_Test) and self.remaining_time >= self.totaltime - int(self.P1_Ini + self.P2_Fill + self.P3_Stab+ self.P4_Test + self.P5_Rel):
                    #self.ProcesLB.setText("Process : " + self.P5) #Result
                    GPIO.output(RELAY_PIN4, GPIO.LOW)
                    GPIO.output(RELAY_PIN8, GPIO.HIGH)
                    self.ProcesLB.setText("Process : Part Ok")
                elif self.remaining_time <= self.totaltime - int(self.P1_Ini + self.P2_Fill + self.P3_Stab) and self.remaining_time >= self.totaltime - int(self.P1_Ini + self.P2_Fill + self.P3_Stab + self.P4_Test):
                    self.ProcesLB.setText("Process : " + self.P4) #Testing
                    GPIO.output(RELAY_PIN3, GPIO.LOW)
                    GPIO.output(RELAY_PIN4, GPIO.HIGH)
                    GPIO.output(RELAY_PIN7, GPIO.HIGH)
                    GPIO.output(RELAY_PIN8, GPIO.LOW)
                    
                    
                    print(str(self.ADS_AV) + " " + str(self.PressureMin) + " " + str(self.PressureMax))
                    if self.ADS_AV < self.PressureMin:
                        print("Low Pressure")
                        self.ProcesLB.setText("Process : Low Pressure")
                    elif self.ADS_AV > self.PressureMax:
                        print("High Pressure")
                    else:
                        print("OK")
                        
                        
                elif self.remaining_time <= self.totaltime - int(self.P1_Ini + self.P2_Fill) and self.remaining_time >= self.totaltime - int(self.P1_Ini + self.P2_Fill + self.P3_Stab):
                    self.ProcesLB.setText("Process : " + self.P3) #Stab
                    GPIO.output(RELAY_PIN2, GPIO.LOW)
                    GPIO.output(RELAY_PIN3, GPIO.HIGH)
                    GPIO.output(RELAY_PIN6, GPIO.HIGH)
                    GPIO.output(RELAY_PIN7, GPIO.LOW)
                elif self.remaining_time <= int(int(self.totaltime) - int(self.P1_Ini)) and self.remaining_time >= self.totaltime - int(self.P1_Ini + self.P2_Fill):
                    self.ProcesLB.setText("Process : " + self.P2) #Filling
                    GPIO.output(RELAY_PIN1, GPIO.LOW)
                    GPIO.output(RELAY_PIN2, GPIO.HIGH)
                    GPIO.output(RELAY_PIN5, GPIO.HIGH)
                    GPIO.output(RELAY_PIN6, GPIO.LOW)
                    if self.ADS_AV == self.SetPressure :
                        print("Air Relase")
                    else:
                        print("Air Fill")
                    
                    
                elif self.remaining_time > int(int(self.totaltime) - int(self.P1_Ini)) :
                    GPIO.output(RELAY_PIN1, GPIO.HIGH)
                    GPIO.output(RELAY_PIN5, GPIO.LOW)
                    self.ProcesLB.setText("Process : " + self.P1)
                else:
                    self.ProcesLB.setText("Process")
                    
                
                
                self.Start_btn.setStyleSheet("background-color : Green");
                self.remaining_time -= 1
                self.StartTime.setText(f'Time remaining: {round(self.remaining_time)} SEC')
                
                self.progress_bar.setValue(self.totaltime - int(self.remaining_time))
            
            
            
        else:
            self.timer.stop()
            self.StartTime.setText('Process : Completed')
            
            GPIO.output(RELAY_PIN1, GPIO.LOW)
            GPIO.output(RELAY_PIN2, GPIO.LOW)
            GPIO.output(RELAY_PIN3, GPIO.LOW)
            GPIO.output(RELAY_PIN4, GPIO.LOW)
            
            self.Start_btn.setStyleSheet("background-color : #00331a");
            self.Stop_btn.setStyleSheet("background-color : #e60000");
            
            GPIO.output(RELAY_PIN5, GPIO.HIGH)
            GPIO.output(RELAY_PIN6, GPIO.HIGH)
            GPIO.output(RELAY_PIN7, GPIO.HIGH)
            GPIO.output(RELAY_PIN8, GPIO.HIGH)
            
            
            
    
class SettingsPage(QWidget):
    select_clicked = pyqtSignal()
    def __init__(self):
        super().__init__()
        
        self.piclabel=QLabel("",self)
        self.piclabel.resize(150,35)
        self.piclabel.move(0,0)
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
        Unit_list = ["Bar", "Milbar", "PSI"]
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
        #self.Key_btn.setStyleSheet("background-color : Green");
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
                    "Volume" = "' + self.Volume_TB.text() + '", "Set"= 0 Where "ProgramNo" =  "' + self.ProNo_TB.text() + '"'
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
        #print('current-text:', text)
        
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
        
        

class AboutPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("About Page"))
        self.setLayout(layout)


        
    
        
    
        

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec_())
