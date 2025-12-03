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
        """
        Initialize the Data Access Layer (DAL) object.
        
        Creates a new Net instance for network operations and initializes
        instance variables to store RFID tag, provider, patients, and assessments.
        """
        self._net = Net()
        self._rfidtag = None
        self._provider = None
        self._patients = []
        self._assessments = []

    def postAssessments(self):
        """
        Post new health assessments to the remote API endpoint.
        
        Ensures network connectivity before posting. If not connected,
        attempts to connect using credentials from secrets module.
        
        Returns:
            tuple: A tuple containing (status_code, json_data) if successful,
                   or None if the request fails. The status_code is an HTTP
                   status code and json_data is the JSON response from the API.
        """
        status = self._net.isConnected()
        if status == False:
            self._net.connect(SSID, PASSWORD)

        newassessmentsendpoint = f"{ASSESSMENTS}"
        response = self._net.postJson(newassessmentsendpoint)
        return response

    def getRFIDTag(self, rfidtag):
        """
        Retrieve RFID tag information from the remote API.
        
        Fetches RFID tag data using the provided RFID tag code and creates
        an RFIDTag object with the retrieved information.
        
        Args:
            rfidtag (str): The RFID tag code to look up.
        
        Returns:
            RFIDTag: An RFIDTag object containing provider_id, card_code,
                    and card_status. Returns None if the request fails.
        """
        rfidendpoint = f'{RFID}{rfidtag}'
        response = self._net.getJson(rfidendpoint)
        self._rfidtag = RFIDTag(response['provider_id'],
                                    response['card_code'],
                                    response['card_status'])
        return self._rfidtag

    def getProvider(self, provider_id):
        """
        Retrieve provider information from the remote API.
        
        Fetches provider data using the provided provider ID and creates
        a Provider object with the retrieved information.
        
        Args:
            provider_id (int): The unique identifier of the provider.
        
        Returns:
            Provider: A Provider object containing provider_id, first_name,
                     last_name, title, and specialty. Returns None if the
                     request fails.
        """
        providerendpoint = f'{PROVIDER}{provider_id}'
        response = self._net.getJson(providerendpoint)
        self._provider = Provider(response['provider_id'],
                                    response['first_name'],
                                    response['last_name'],
                                    response['title'],
                                    response['specialty'])
        return self._provider

    def getPatients(self, provider_id):
        """
        Retrieve all patients associated with a specific provider.
        
        Fetches a list of patients from the remote API for the given provider ID
        and creates Patient objects for each patient in the response.
        
        Args:
            provider_id (int): The unique identifier of the provider whose
                             patients are to be retrieved.
        
        Returns:
            list: A list of Patients objects, each containing patient_id,
                  first_name, last_name, and birth_date. Returns an empty
                  list if no patients are found or if the request fails.
        """
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
        """
        Retrieve all health assessments for a specific patient.
        
        Fetches a list of health assessments from the remote API for the given
        patient ID and creates HealthAssessments objects for each assessment
        in the response.
        
        Args:
            patient_id (int): The unique identifier of the patient whose
                            assessments are to be retrieved.
        
        Returns:
            list: A list of HealthAssessments objects, each containing
                  assessment_id, patient_id, assessment_dt, assessment_result,
                  provider_id, and provider_reviewed. Returns an empty list
                  if no assessments are found or if the request fails.
        """
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
        """
        Update the provider_reviewed status for a specific assessment.
        
        Sends a PUT request to mark an assessment as reviewed by the provider.
        This updates the provider_reviewed flag to 'Y' for the specified assessment.
        
        Args:
            assessment_id (int): The unique identifier of the assessment to
                               mark as provider reviewed.
        
        Returns:
            tuple: A tuple containing (status_code, json_data) if successful,
                   or None if the request fails. The status_code is an HTTP
                   status code and json_data is the JSON response from the API.
        """
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
    