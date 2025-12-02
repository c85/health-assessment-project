class RFIDTag:
    def __init__(self, provider_id, rfidtag, cardstatus):
        self._provider_id = provider_id
        self._rfidtag = rfidtag
        self._cardstatus = cardstatus

class Provider:
    def __init__(self, provider_id, firstname, lastname, title, specialty):
        self._provider_id = provider_id
        self._firstname = firstname
        self._lastname = lastname
        self._title = title
        self._specialty = specialty

class Patients:
    def __init__(self, patient_id, firstname, lastname, birthdate):
        self._patient_id = patient_id
        self._firstname = firstname
        self._lastname = lastname
        self._birthdate = birthdate

    def line1(self):
        return f"Patient ID: {self._patient_id}"

    def line2(self):
        return self._lastname + ', ' + self._firstname[0] + '.'

class HealthAssessments:
    def __init__(self, assessment_id, patient_id, datetime, result, provider_id, reviewed):
        self._assessment_id = assessment_id
        self._result = result
        self._datetime = datetime

    def line1(self):
        return self._result

    def line2(self):
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