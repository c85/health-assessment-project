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
        """
        Initialize the AssessmentController with all hardware components and state machine.
        
        Sets up RFID reader, light strip, buzzer, LCD display, buttons, timer, and state model.
        Configures all state transitions and initializes data access layer. Sets up the
        state machine with transitions between INITIAL_SCREEN, WELCOME, FAILED_AUTH,
        PATIENT_SELECT, and DISPLAY_ASSESMENT states.
        """
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
        """
        Display the initial screen prompting the user to scan their employee badge.
        
        Clears the display and shows a two-line message instructing the user to
        scan their RFID employee badge for authentication.
        """
        self._display.clear()
        self._display.showText('Please scan your', 0)
        self._display.showText('employee badge', 1)

    def showWelcome(self, provider):
        """
        Display a welcome message for the authenticated provider.
        
        Shows a personalized welcome message with the provider's name and title.
        Plays a three-tone musical sequence (C5, E5, G5) to indicate successful authentication.
        
        Args:
            provider (dict): A dictionary containing provider information with keys
                           '_lastname', '_firstname', and '_title'.
        """
        self._display.clear()
        self._display.showText("Welcome!", 0)
        provider_text = f"{provider['_lastname']}, {provider['_firstname'][0]}., {provider['_title']}"
        self._display.showText(provider_text[:16], 1)
        self._buzzer.beep(tones['C5'], 200)
        time.sleep(0.1)
        self._buzzer.beep(tones['E5'], 200)
        time.sleep(0.1)
        self._buzzer.beep(tones['G5'], 200)

    def showFailedAuth(self):
        """
        Display an access denied message for failed authentication.
        
        Shows an error message indicating that the user was not found in the system.
        Plays two low-pitched beeps (C3) to indicate authentication failure.
        """
        self._display.clear()
        self._display.showText("Access Denied:", 0)
        self._display.showText("User not found!", 1)
        self._buzzer.beep(tones['C3'], 300)
        time.sleep(0.2)
        self._buzzer.beep(tones['C3'], 300)
  
    def showPatientSelect(self):
        """
        Display the patient selection screen.
        
        Shows the currently selected patient from the patient list. If no patients
        are available, displays a "No new patients found!" message with a red
        light indicator and error beep. Otherwise, displays the current patient's
        ID on line 1 and formatted name on line 2.
        """
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
        """
        Display the health assessment screen for the current patient.
        
        Shows the currently selected assessment from the assessment list. If no
        assessments are available, displays a "No new assessments!" message with
        a red light indicator and error beep. Otherwise, displays the assessment
        result on line 1 and formatted date/time on line 2. If the assessment
        result is 'UNHEALTHY', activates the alarm system.
        """
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
        """
        Handle actions when entering a new state in the state machine.
        
        Performs state-specific initialization tasks such as posting assessments,
        displaying appropriate screens, setting light colors, starting timers,
        and loading data from the data access layer.
        
        Args:
            state (int): The state constant representing the state being entered
                        (INITIAL_SCREEN, WELCOME, FAILED_AUTH, PATIENT_SELECT, or DISPLAY_ASSESMENT).
            event (str): The event that triggered the state transition.
        """
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
        """
        Handle cleanup actions when leaving a state in the state machine.
        
        Performs state-specific cleanup tasks such as canceling timers, stopping
        alarms, and resetting state variables when transitioning out of a state.
        
        Args:
            state (int): The state constant representing the state being left
                        (INITIAL_SCREEN, WELCOME, FAILED_AUTH, PATIENT_SELECT, or DISPLAY_ASSESMENT).
            event (str): The event that triggered the state transition.
        """
        if state == DISPLAY_ASSESMENT:
            if self._timer._started:
                self._timer.cancel()
            self._alarmon = False
            self._buzzer.stop()

    def stateEvent(self, state, event)->bool:
        """
        Handle events that occur within a specific state.
        
        Processes button press events (left_press, right_press, select_press) and
        performs appropriate actions such as navigating through patients/assessments
        or marking assessments as reviewed. Provides visual and audio feedback
        for user actions.
        
        Args:
            state (int): The current state constant (PATIENT_SELECT or DISPLAY_ASSESMENT).
            event (str): The event string representing the action (e.g., "left_press",
                        "right_press", "select_press").
        
        Returns:
            bool: True if the event was handled, False otherwise.
        """
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
        """
        Perform continuous actions while in a specific state.
        
        Executes state-specific continuous operations such as reading RFID tags,
        managing timers, and playing alarms. This method is called repeatedly
        while the state machine is in a particular state.
        
        Args:
            state (int): The current state constant (INITIAL_SCREEN, PATIENT_SELECT,
                       or DISPLAY_ASSESMENT).
        """
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
        """
        Play an alarm sequence for unhealthy health assessments.
        
        Plays an alternating two-tone alarm (1200Hz and 900Hz) with red light
        flashing to alert the provider of an unhealthy assessment result. The
        alarm can be stopped by setting _alarmon to False. This method is called
        repeatedly while _alarmon is True.
        """
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
        """
        Start the state machine and begin processing events.
        
        Initiates the main execution loop of the state machine, which will
        continuously process events, handle state transitions, and execute
        state-specific actions until stop() is called.
        """
        self._model.run()

    def stop(self):
        """
        Stop the state machine and halt all processing.
        
        Stops the state machine execution loop, effectively shutting down
        the controller. Should be called to gracefully terminate the application.
        """
        self._model.stop()

if __name__ == '__main__':
    s = AssessmentController()
    try:
        s.run()
    except KeyboardInterrupt:
        s.stop()


