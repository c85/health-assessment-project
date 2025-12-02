import time
time.sleep(0.1) # Wait for USB to become ready

from time import *
from Log import *
from Buzzer import *
from LightStrip import *
from Displays import *
from Button import *
from modelclasses import *
from DAL import *
from RFIDReader import *
from StateModel import *
from Counters import *

INITIAL_SCREEN = 0
WELCOME = 1
FAILED_AUTH = 2
PATIENT_SELECT = 3
DISPLAY_ASSESMENT = 4

class AssessmentController:

    def __init__(self):
        self._rfid = RFIDReader(mosi=5, miso=6, sck=4, sda=7)
        self._lightstrip = LightStrip(pin=2, name='Lights')
        self._buzzer = PassiveBuzzer(pin=14, name='Buzz')
        self._display = LCDDisplay(sda=0, scl=1)
        self._alarmon = False

        self._model = StateModel(5, self, debug=True)

        self._leftbutton = Button(pin=16, name='left', handler=self)
        self._rightbutton = Button(pin=17, name='right', handler=self)
        self._selectbutton = Button(pin=18, name='select', handler=self)
        self._backbutton = Button(pin=19, name='back', handler=self)
        self._model.addButton(self._leftbutton)
        self._model.addButton(self._rightbutton)
        self._model.addButton(self._selectbutton)
        self._model.addButton(self._backbutton)

        self._timer = SoftwareTimer(name="timer", handler=None)
        self._model.addTimer(self._timer)

        self._rfidtag = None
        self._provider = None
        self._patients = []
        self._assessments = []
        self._patindex = 0
        self._assessindex = 0
        self._dal = DAL()

        self._model.addCustomEvent('ok_card')
        self._model.addCustomEvent('failed_card')
        
        self._model.addTransition(INITIAL_SCREEN, ["ok_card"], WELCOME)
        self._model.addTransition(INITIAL_SCREEN, ["timer_timeout"], FAILED_AUTH)
        self._model.addTransition(INITIAL_SCREEN, ["failed_card"], FAILED_AUTH)
        self._model.addTransition(FAILED_AUTH, ["timer_timeout"], INITIAL_SCREEN)

        self._model.addTransition(WELCOME, ["timer_timeout"], PATIENT_SELECT)
        self._model.addTransition(PATIENT_SELECT, ["select_press"], DISPLAY_ASSESMENT)
        self._model.addTransition(PATIENT_SELECT, ["timer_timeout"], INITIAL_SCREEN)

        self._model.addTransition(DISPLAY_ASSESMENT, ["back_press"], PATIENT_SELECT)
        self._model.addTransition(DISPLAY_ASSESMENT, ["timer_timeout"], PATIENT_SELECT)

    def showInitialScreen(self):
        self._display.clear()
        self._display.showText('Please scan your', 0)
        self._display.showText('employee badge', 1)

    def showWelcome(self, provider):
        self._display.clear()
        self._display.showText("Welcome!", 0)
        self._display.showText(f"{provider['_lastname']}, {provider['_title']}", 1)
        self._buzzer.beep(tones['C5'], 200)
        time.sleep(0.1)
        self._buzzer.beep(tones['E5'], 200)
        time.sleep(0.1)
        self._buzzer.beep(tones['G5'], 200)

    def showFailedAuth(self):
        self._display.clear()
        self._display.showText("Access Denied:", 0)
        self._display.showText("User not found!", 1)
        self._buzzer.beep(tones['C3'], 300)
        time.sleep(0.2)
        self._buzzer.beep(tones['C3'], 300)
  
    def showPatientSelect(self):
        self._display.clear()
        self._lightstrip.off()
        if not self._patients:
            self._display.showText("No new", 0)
            self._display.showText("patients found!", 1)
            self._buzzer.beep(tones['C3'], 200)
            self._lightstrip.setColor(RED, 8)
            time.sleep(0.2)
            self._lightstrip.off()
        else:
            currentpatient = self._patients[self._patindex]
            self._display.showText(currentpatient.line1(), 0)
            self._display.showText(currentpatient.line2(), 1)

    def showAssessments(self):
        self._display.clear()
        self._lightstrip.off()
        if not self._assessments:
            self._display.showText("No new", 0)
            self._display.showText("assessments!", 1)
            self._buzzer.beep(tones['C3'], 200)
            self._lightstrip.setColor(RED, 8)
            time.sleep(0.2)
            self._lightstrip.off()
        else:
            currentassessment = self._assessments[self._assessindex]
            self._display.showText(currentassessment.line1(), 0)
            self._display.showText(currentassessment.line2(), 1)

            if currentassessment._result == 'UNHEALTHY':
                self._alarmon = True
            else:
                self._alarmon = False
                self._buzzer.stop()

    def stateEntered(self, state, event):
        Log.d(f'State {state} entered on event {event}')
        if state == INITIAL_SCREEN:
            self._dal.postAssessments()
            self.showInitialScreen()
            self._rfidtag = None
            self._lightstrip.setColor(YELLOW, 8)
            self._timer.start(30)
        elif state == WELCOME:
            self.showWelcome(self._provider)
            self._lightstrip.setColor(GREEN, 8)
            self._timer.start(5)
        elif state == FAILED_AUTH:
            self.showFailedAuth()
            self._lightstrip.setColor(RED, 8)
            self._timer.start(5)
        elif state == PATIENT_SELECT:
            try:
                provider_id = self._provider['_provider_id']
                self._patients = self._dal.getPatients(provider_id)
                self._patindex = 0 
            except:
                pass
            self.showPatientSelect()
        elif state == DISPLAY_ASSESMENT:
            if self._patients and self._patindex < len(self._patients):
                try:
                    selected_patient = self._patients[self._patindex]
                    patient_id = selected_patient._patient_id
                    self._assessments = self._dal.getAssessments(patient_id)
                    self._assessindex = 0
                except:
                    pass
            self.showAssessments()

    def stateLeft(self, state, event):
        if state == DISPLAY_ASSESMENT:
            if self._timer._started:
                self._timer.cancel()
            self._alarmon = False
            self._buzzer.stop()

    def stateEvent(self, state, event)->bool:
        if state == PATIENT_SELECT:
            if event == "left_press":
                if self._patients and self._patindex > 0:
                    self._patindex -= 1
                    self.showPatientSelect()
                    self._buzzer.beep(tones['C5'], 200)
                    self._lightstrip.setColor(GREEN, 8)
                    time.sleep(0.2)
                    self._lightstrip.off()
                else:
                    self._buzzer.beep(tones['C3'], 200)
                    self._lightstrip.setColor(RED, 8)
                    time.sleep(0.2)
                    self._lightstrip.off()
                return True
            elif event == "right_press":
                if self._patients and self._patindex < len(self._patients) - 1:
                    self._patindex += 1
                    self.showPatientSelect()
                    self._buzzer.beep(tones['C5'], 200)
                    self._lightstrip.setColor(GREEN, 8)
                    time.sleep(0.2)
                    self._lightstrip.off()
                else:
                    self._buzzer.beep(tones['C3'], 200)
                    self._lightstrip.setColor(RED, 8)
                    time.sleep(0.2)
                    self._lightstrip.off()
                return True
        if state == DISPLAY_ASSESMENT:
            if event == "left_press":
                if self._assessments and self._assessindex > 0:
                    self._assessindex -= 1
                    self.showAssessments()
                    self._lightstrip.setColor(GREEN, 8)
                    self._buzzer.beep(tones['C5'], 200)
                    time.sleep(0.2)
                    self._lightstrip.off()
                else:
                    self._lightstrip.setColor(RED, 8)
                    self._buzzer.beep(tones['C3'], 200)
                    time.sleep(0.2)
                    self._lightstrip.off()
                return True
            elif event == "right_press":
                if self._assessments and self._assessindex < len(self._assessments) - 1:
                    self._assessindex += 1
                    self.showAssessments()
                    self._lightstrip.setColor(GREEN, 8)
                    self._buzzer.beep(tones['C5'], 200)
                    time.sleep(0.2)
                    self._lightstrip.off()
                else:
                    self._lightstrip.setColor(RED, 8)
                    self._buzzer.beep(tones['C3'], 200)
                    time.sleep(0.2)
                    self._lightstrip.off()
                return True
            elif event == "select_press":
                if self._assessments and self._assessindex < len(self._assessments):
                    currentassessment = self._assessments[self._assessindex]
                    assessment_id = currentassessment._assessment_id
                    try:
                        self._dal.putProviderReviewed(assessment_id)
                        self._lightstrip.setColor(GREEN, 8)
                        self._buzzer.beep(tones['C5'], 200)
                        time.sleep(0.2)
                        self._lightstrip.off()
                        # Refresh assessments by re-entering the DISPLAY_ASSESMENT state
                        self._model.gotoState(DISPLAY_ASSESMENT, "select_press")
                    except:
                        self._lightstrip.setColor(RED, 8)
                        self._buzzer.beep(tones['C3'], 300)
                        time.sleep(0.2)
                        self._lightstrip.off()
                else:
                    self._lightstrip.setColor(RED, 8)
                    self._buzzer.beep(tones['C3'], 200)
                    time.sleep(0.2)
                    self._lightstrip.off()
                return True                
        return False

    def stateDo(self, state):
        if state == INITIAL_SCREEN:
            if self._rfidtag is None:
                self._rfidtag = self._rfid.getTagID()
                if self._rfidtag:
                    self._timer.cancel()
                    self._lightstrip.off()
                    try:
                        provider_id = self._dal.getRFIDTag(self._rfidtag).__dict__['_provider_id']
                        if provider_id:
                            self._provider = self._dal.getProvider(provider_id).__dict__
                            self._model.processEvent('ok_card')
                        else:
                            self._model.processEvent('failed_card')
                    except:
                        self._model.processEvent('failed_card')
        if state == PATIENT_SELECT:
            if not self._patients and not self._timer._started:
                self._timer.start(5)
        if state == DISPLAY_ASSESMENT:
            if not self._assessments and not self._timer._started:
                self._timer.start(5)
            if self._alarmon:
                self.playUnhealthyAlarm()

    def playUnhealthyAlarm(self):
        if not self._alarmon:
            self._buzzer.stop()
            return
        self._buzzer.play(1200)
        self._lightstrip.setColor(RED, 8)
        time.sleep(0.2)
        self._lightstrip.off()
        time.sleep(0.05)
        if not self._alarmon:
            self._buzzer.stop()
            return
        self._buzzer.play(900)
        self._lightstrip.setColor(RED, 8)
        time.sleep(0.2)
        self._lightstrip.off()
        time.sleep(0.05)
        if not self._alarmon:
            self._buzzer.stop()

    def run(self):
        self._model.run()

    def stop(self):
        self._model.stop()

if __name__ == '__main__':
    s = AssessmentController()
    try:
        s.run()
    except KeyboardInterrupt:
        s.stop()


