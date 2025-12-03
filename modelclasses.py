class RFIDTag:
    def __init__(self, provider_id, rfidtag, cardstatus):
        """
        Initialize an RFIDTag object with provider and card information.
        
        Args:
            provider_id (int): The unique identifier of the provider associated
                             with this RFID tag.
            rfidtag (str): The RFID tag code or card code.
            cardstatus (str): The status of the RFID card (e.g., 'ACTIVE', 'INACTIVE').
        """
        self._provider_id = provider_id
        self._rfidtag = rfidtag
        self._cardstatus = cardstatus

class Provider:
    def __init__(self, provider_id, firstname, lastname, title, specialty):
        """
        Initialize a Provider object with provider information.
        
        Args:
            provider_id (int): The unique identifier of the provider.
            firstname (str): The provider's first name.
            lastname (str): The provider's last name.
            title (str): The provider's professional title (e.g., 'Dr.', 'Nurse').
            specialty (str): The provider's medical specialty.
        """
        self._provider_id = provider_id
        self._firstname = firstname
        self._lastname = lastname
        self._title = title
        self._specialty = specialty

class Patients:
    def __init__(self, patient_id, firstname, lastname, birthdate):
        """
        Initialize a Patients object with patient information.
        
        Args:
            patient_id (int): The unique identifier of the patient.
            firstname (str): The patient's first name.
            lastname (str): The patient's last name.
            birthdate (str): The patient's date of birth.
        """
        self._patient_id = patient_id
        self._firstname = firstname
        self._lastname = lastname
        self._birthdate = birthdate

    def line1(self):
        """
        Generate the first line of text for display on the LCD screen.
        
        Returns:
            str: A formatted string displaying "Patient ID: {patient_id}".
        """
        return f"Patient ID: {self._patient_id}"

    def line2(self):
        """
        Generate the second line of text for display on the LCD screen.
        
        Formats the patient's name as "Lastname, F." where F is the first
        initial of the first name.
        
        Returns:
            str: A formatted string with the patient's last name, comma,
                 and first initial followed by a period (e.g., "Smith, J.").
        """
        return self._lastname + ', ' + self._firstname[0] + '.'

class HealthAssessments:
    def __init__(self, assessment_id, patient_id, datetime, result, provider_id, reviewed):
        """
        Initialize a HealthAssessments object with assessment information.
        
        Args:
            assessment_id (int): The unique identifier of the health assessment.
            patient_id (int): The unique identifier of the patient this assessment
                            belongs to.
            datetime (str): The date and time when the assessment was performed,
                          typically in ISO format (e.g., 'YYYY-MM-DDTHH:MM:SS').
            result (str): The result of the health assessment (e.g., 'HEALTHY', 'UNHEALTHY').
            provider_id (int): The unique identifier of the provider who performed
                             or will review this assessment.
            reviewed (str): Indicates whether the provider has reviewed this assessment
                          (e.g., 'Y' for yes, 'N' for no).
        """
        self._assessment_id = assessment_id
        self._result = result
        self._datetime = datetime

    def line1(self):
        """
        Generate the first line of text for display on the LCD screen.
        
        Returns:
            str: The assessment result (e.g., 'HEALTHY' or 'UNHEALTHY').
        """
        return self._result

    def line2(self):
        """
        Generate the second line of text for display on the LCD screen.
        
        Formats the assessment datetime into a readable format. If the datetime
        is in ISO format (contains 'T'), converts it to MM/DD/YY HH:MMAM/PM format.
        Otherwise, returns the datetime as-is.
        
        Returns:
            str: A formatted date and time string in MM/DD/YY HH:MMAM/PM format
                 if the datetime is in ISO format, otherwise returns the original
                 datetime string.
        """
        if self._datetime and 'T' in str(self._datetime):
            date_part, time_part = str(self._datetime).split('T')
            year, month, day = date_part.split('-')
            # Extract hour and minute from time (format: HH:MM:SS or HH:MM:SS.microseconds)
            time_components = time_part.split(':')
            hour = int(time_components[0])
            minute = time_components[1]
            # Convert to 12-hour format with AM/PM
            if hour == 0:
                hour_12 = 12
                am_pm = 'AM'
            elif hour < 12:
                hour_12 = hour
                am_pm = 'AM'
            elif hour == 12:
                hour_12 = 12
                am_pm = 'PM'
            else:
                hour_12 = hour - 12
                am_pm = 'PM'
            return f"{month}/{day}/{year[-2:]} {hour_12}:{minute}{am_pm}"
        return self._datetime