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

    def line1(self):
        return self._lastname + ' ' + self._title

class Patients:
    def __init__(self, patient_id, firstname, lastname, birthdate):
        self._patient_id = patient_id
        self._firstname = firstname
        self._lastname = lastname
        self._birthdate = birthdate

    def line1(self):
        return self._lastname

    def line2(self):
        if self._birthdate and 'T' in str(self._birthdate):
            date_part = str(self._birthdate).split('T')[0]
            year, month, day = date_part.split('-')
            return f"{month}/{day}/{year}"
        return self._birthdate

class HealthAssessments:
    def __init__(self, assessment_id, patient_id, datetime, result, provider_id, reviewed):
        self._assessment_id = assessment_id
        self._result = result
        self._datetime = datetime

    def line1(self):
        return self._result

    def line2(self):
        if self._datetime and 'T' in str(self._datetime):
            date_part = str(self._datetime).split('T')[0]
            year, month, day = date_part.split('-')
            return f"{month}/{day}/{year}"
        return self._datetime