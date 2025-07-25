from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QDialog, QHBoxLayout, QLabel
from PyQt5.QtCore import pyqtProperty, QCoreApplication, QObject, QUrl
import sys
from AlbertaLoop_UI import Ui_MainWindow

# from Actions.Command import Launch
from Actions.Command import PrepareLaunch
from Actions.Command import EStop
from Actions.Command import Crawl
from Actions.Command import SafeToApproach
# from Actions.HealthCheck import HealthCheck

import threading

from CustomLora import *
from pySX127x.SX127x.board_config import BOARD
from config import *
from utils.formatPayload import PodMessage

import datetime
from zoneinfo import ZoneInfo

import signal # Make Ctrl+C work with PyQt5 Applications
signal.signal(signal.SIGINT, signal.SIG_DFL)

class MWindowWrapper(Ui_MainWindow):

    def __init__(self, window, lora_module):
        self.setupUi(window)

        self.command = None
        self.current_state = STATE_SAFE
        self.command_requested = ["none"]
        self.healthchk_requested = ["none"]
        self.estop_requested = ["none"]
        self.cmd_lock = threading.Lock()
        self.lora_module = lora_module

        # -----------------------------------------------------------------
        # Add functionality below!
        # User Added QML Widget for Speed Gauge
        # self.spedometerWidget = QQuickWidget()
        # self.spedometerWidget.setClearColor(QtCore.Qt.transparent)
        # self.spedometerWidget.setResizeMode(QQuickWidget.SizeRootObjectToView)
        # self.spedometerWidget.setSource(QUrl("assets/Guage.qml"))
        # self.speedGaugeLayout.addWidget(self.spedometerWidget)

        # Connect clicked functions
        # self.launchBtn.clicked.connect(self.launchBtn_clicked)
        self.safeBtn.clicked.connect(self.safeBtn_clicked)
        self.crawlBtn.clicked.connect(self.crawlBtn_clicked)
        self.prepLaunchBtn.clicked.connect(self.prepLaunchBtn_clicked)
        self.eStopBtn.clicked.connect(self.eStopBtn_clicked)

        # logo added
        pixmap = QtGui.QPixmap("img/Albertaloop_logo.png")
        self.albertaloopLogo.setPixmap(pixmap)


    # Clicked function definitions
    # def launchBtn_clicked(self):
    #     print("Launch button pressed")
    #     if self.command_requested == ["none"]:
    #         if self.current_state == STATE_READY :
    #             self.command_requested = ["launch"]
    #             self.executeCommand(Launch(self.lora_module), self.command_requested)
    #         else :
    #             print("Not ready to launch")
    #     else:
    #         print("Waiting for another command: ")
    #         print(self.command_requested)
    #         print("\n")


    # def healthChkBtn_clicked(self):
    #     print("Health check button pressed")
    #     if self.healthchk_requested == ["none"]:
    #         self.healthchk_requested = ["yes"]
    #         self.executeCommand(HealthCheck(self.lora_module), self.healthchk_requested)
    #         print("Health check requested")
    #     else :
    #         print("Health check already requested")

    def crawlBtn_clicked(self):
        print("Crawl button pressed")
        self.executeCommand(Crawl(self.lora_module), self.command_requested)
        print("Crawl requested")
        # Not required for kdays
        # if self.command_requested == ["none"]:
        #     if self.current_state == STATE_READY:
        #         self.command_requested = ["crawl"]
        #         self.executeCommand(Crawl(self.lora_module), self.command_requested)
        #         print("Crawl requested")
        #     else :
        #         print("Not ready to crawl, pod must be idle")
        # else:
        #     print("Waiting for another command: ")
        #     print(self.command_requested)
        #     print("\n")

    def prepLaunchBtn_clicked(self):
        print("Prepare Launch button pressed")
        self.executeCommand(PrepareLaunch(self.lora_module), self.command_requested)
        print("Prepare to launch requested")
        # Not required for kdays
        # if self.command_requested == ["none"]:
        #     if self.current_state == STATE_SAFE :
        #         self.command_requested = ["prep_launch"]
        #         self.executeCommand(PrepareLaunch(self.lora_module), self.command_requested)
        #         print("Prepare to launch requested")
        #     else :
        #         print("Not ready for prepare to launch, pod must be idle")
        # else:
        #     print("Waiting for another command: ")
        #     print(self.command_requested)
        #     print("\n")

    def eStopBtn_clicked(self):
        print("Estop button pressed")
        self.cmd_lock.acquire()
        if self.estop_requested == ["none"]:
            self.estop_requested = ["yes"]
            self.cmd_lock.release()
            self.executeCommand(EStop(self.lora_module), self.estop_requested)
            print("Emergency stop requested")
        else :
            print(self.estop_requested)
            self.cmd_lock.release()
            print("EStop already sending")

    def safeBtn_clicked(self):
        print("Safe to approach button pressed")
        self.executeCommand(SafeToApproach(self.lora_module), self.command_requested)
        print("Safe to approach requested")

    # Command Pattern definitions
    def executeCommand(self, command, cmd_state):
        self.command = command
        self.cmd_thread = threading.Thread(target=self.command.execute, args=[cmd_state, self.cmd_lock])
        self.cmd_thread.run()
        

    def command_input(self):
        text = self.command_line.text()
        # exits program TODO (remove later plz)
        if text.lower() == "exit":
            sys.exit()
        print("command >> ", text)
    
    def handleNewMessage(self, message: PodMessage):
        self.updateCurrentState(message.fsm_state)
        self.addMessageLabel(message)

    #updates label colors if state is not equal to current_state
    def updateCurrentState(self, state):
        if state == self.current_state:
            True
        elif state != self.current_state:
            self.current_state = state
            if state == STATE_FAULT:
                self.label_12.setStyleSheet("background-color: red")
                self.label_11.setStyleSheet("background-color: gray")
                self.label_10.setStyleSheet("background-color: gray")
                self.label_9.setStyleSheet("background-color: gray")
                self.label_8.setStyleSheet("background-color: gray")
                self.label_7.setStyleSheet("background-color: gray")
                self.label_6.setStyleSheet("background-color: gray")
            if state == STATE_SAFE:
                self.label_12.setStyleSheet("background-color: gray")
                self.label_11.setStyleSheet("background-color: #89CFF0")
                self.label_10.setStyleSheet("background-color: gray")
                self.label_9.setStyleSheet("background-color: gray")
                self.label_8.setStyleSheet("background-color: gray")
                self.label_7.setStyleSheet("background-color: gray")
                self.label_6.setStyleSheet("background-color: gray")
            if state == STATE_READY:
                self.label_12.setStyleSheet("background-color: gray")
                self.label_11.setStyleSheet("background-color: gray")
                self.label_10.setStyleSheet("background-color: green")
                self.label_9.setStyleSheet("background-color: gray")
                self.label_8.setStyleSheet("background-color: gray")
                self.label_7.setStyleSheet("background-color: gray")
                self.label_6.setStyleSheet("background-color: gray")
            # if state == ['launch']:
            #     self.label_12.setStyleSheet("background-color: #89CFF0")
            #     self.label_11.setStyleSheet("background-color: gray")
            #     self.label_10.setStyleSheet("background-color: gray")
            #     self.label_9.setStyleSheet("background-color: green")
            #     self.label_8.setStyleSheet("background-color: gray")
            #     self.label_7.setStyleSheet("background-color: gray")
            #     self.label_6.setStyleSheet("background-color: gray")
            # if state == ['coast']:
            #     self.label_12.setStyleSheet("background-color: gray")
            #     self.label_11.setStyleSheet("background-color: gray")
            #     self.label_10.setStyleSheet("background-color: gray")
            #     self.label_9.setStyleSheet("background-color: gray")
            #     self.label_8.setStyleSheet("background-color: green")
            #     self.label_7.setStyleSheet("background-color: gray")
            #     self.label_6.setStyleSheet("background-color: gray")
            if state == STATE_BRAKING:
                self.label_12.setStyleSheet("background-color: gray")
                self.label_11.setStyleSheet("background-color: gray")
                self.label_10.setStyleSheet("background-color: gray")
                self.label_9.setStyleSheet("background-color: gray")
                self.label_8.setStyleSheet("background-color: gray")
                self.label_7.setStyleSheet("background-color: gray")
                self.label_6.setStyleSheet("background-color: yellow")
            if state == STATE_CRAWLING:
                self.label_12.setStyleSheet("background-color: gray")
                self.label_11.setStyleSheet("background-color: gray")
                self.label_10.setStyleSheet("background-color: gray")
                self.label_9.setStyleSheet("background-color: gray")
                self.label_8.setStyleSheet("background-color: gray")
                self.label_7.setStyleSheet("background-color: yellow")
                self.label_6.setStyleSheet("background-color: gray")

    def addMessageLabel(self, message: str):
        label = QtWidgets.QLabel(self.scrollAreaWidgetContents)
        label.setText(f"{datetime.datetime.now(ZoneInfo("America/Edmonton")).strftime('%H:%M:%S')}: {message}")
        label.setStyleSheet("color: black; font: 10pt Arial; background: white; padding: 4px;")
        self.scrollLayout.addWidget(label)

    
        
if __name__ == "__main__":
    app = QApplication(sys.argv)

    # LoRa Setup
    BOARD.setup()
    lora = CustomLora()
    lora.set_freq(915)
    lora.set_pa_config(pa_select=1, max_power=21, output_power=15)
    lora.set_bw(BW.BW125)
    lora.set_coding_rate(CODING_RATE.CR4_8)
    lora.set_spreading_factor(12)
    lora.set_rx_crc(True)
    lora.set_low_data_rate_optim(True)

    assert(lora.get_agc_auto_on() == 1)

    try:
        lora.start()

        while (True):
            if (lora.connected):
                print("STARTING CLIENT")
                MainWindow = QMainWindow()
                mWindowWrapper = MWindowWrapper(MainWindow, lora)
                # Connect the LoRa signal to the GUI update function
                lora.state_updated.connect(mWindowWrapper.handleNewMessage)
                
                MainWindow.show()
                sys.exit(app.exec_())
                
    except KeyboardInterrupt:
        sys.stdout.flush()
        print("Exit")
        sys.stderr.write("KeyboardInterrupt\n")
    finally:
        sys.stdout.flush()
        print("Exit")
        lora.set_mode(MODE.SLEEP)
        BOARD.teardown()
