import time
time.sleep(0.1) # Wait for USB to become ready

from AssessmentController import *

f = AssessmentController()
f.run()