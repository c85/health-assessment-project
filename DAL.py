from Net import *
from modelclasses import *

from secrets import *
from Net import *
from modelclasses import *

BASEURL = 'https://oracleapex.com/ords/c85/pihealth/'
PROVIDER = f'{BASEURL}provider/'
PATIENTS = f'{BASEURL}patients/'
RFID = f'{BASEURL}rfidtag/'
ASSESSMENTS = f'{BASEURL}assessments'
REVIEWED = f'{BASEURL}provider_reviewed/'

class DAL:
    def __init__(self):
        self._net = Net()
        self._rfidtag = None
        self._provider = None
        self._patients = []
        self._assessments = []

    def postAssessments(self):
        status = self._net.isConnected()
        if status == False:
            self._net.connect(SSID, PASSWORD)

        newassessmentsendpoint = f"{ASSESSMENTS}"
        response = self._net.postJson(newassessmentsendpoint)
        return response

    def getRFIDTag(self, rfidtag):
        rfidendpoint = f'{RFID}{rfidtag}'
        response = self._net.getJson(rfidendpoint)
        self._rfidtag = RFIDTag(response['provider_id'],
                                    response['card_code'],
                                    response['card_status'])
        return self._rfidtag

    def getProvider(self, provider_id):
        providerendpoint = f'{PROVIDER}{provider_id}'
        response = self._net.getJson(providerendpoint)
        self._provider = Provider(response['provider_id'],
                                    response['first_name'],
                                    response['last_name'],
                                    response['title'],
                                    response['specialty'])
        return self._provider

    def getPatients(self, provider_id):
        patientsendpoint = f'{PATIENTS}{provider_id}'
        response = self._net.getJson(patientsendpoint)
        self._patients = []
        for item in response['items']:
            self._patients.append(
                Patients(item['patient_id'],
                            item['first_name'],
                            item['last_name'],
                            item['birth_date'])
            )
        return self._patients

    def getAssessments(self, patient_id):
        assessmentsendpoint = f'{ASSESSMENTS}/{patient_id}'
        response = self._net.getJson(assessmentsendpoint)
        self._assessments = []
        for item in response['items']:
            self._assessments.append(
                HealthAssessments(item['assessment_id'],
                                    item['patient_id'],
                                    item['assessment_dt'],
                                    item['assessment_result'],
                                    item['provider_id'],
                                    item['provider_reviewed'])
            )
        return self._assessments

    def putProviderReviewed(self, assessment_id):
        reviewedendpoint = f"{REVIEWED}{assessment_id}"
        response = self._net.putJson(reviewedendpoint)
        return response

if __name__=='__main__':
    d = DAL()
    post_new_assessments = d.postAssessments()
    provider_id = d.getRFIDTag('c908e41134').__dict__['_provider_id'] # using rfidtag for provider_id = 1
    provider = d.getProvider(provider_id).__dict__ # get provider info for provider_id = 1
    patients = [p.__dict__ for p in d.getPatients(provider_id)] # get all patients for provider_id = 1
    assessments = [a.__dict__ for a in d.getAssessments(patients[1]['_patient_id'])] # get all assessments for the second patient returned
    provider_reviewed = d.putProviderReviewed(1) # update assessment_id = 1 to PROVIDER_REVIEWED = 'Y'
    print(f"Assessment Result: {assessments[0]['_result']}\nAssessment Datetime: {assessments[0]['_datetime']}") # display assessment result and datetime
    