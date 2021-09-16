from twilio.rest import Client
import requests
import winsound
import re
import time

def notify_user(crn="0"):
    TWILIO_PHONE_NUMBER = "+12342319112"
    #replace with your number
    DIAL_NUMBERS = ["+15126650719"]
    TWIML_INSTRUCTIONS_URL = \
    "http://static.fullstackpython.com/phone-calls-python.xml"
    client = Client("AC1968e8b4bd0f20a2cc81822c724a097d", "78c4fb1a1300d376c22292196d155fd6")
    """Dials one or more phone numbers from a Twilio phone number."""
    for number in DIAL_NUMBERS:
        print("Dialing " + number)
        # set the method to "GET" from default POST because Amazon S3 only
        # serves GET requests on files. Typically POST would be used for apps
        client.calls.create(to=number, from_=TWILIO_PHONE_NUMBER,
                            url=TWIML_INSTRUCTIONS_URL, method="GET")
        client.messages.create(
            to=number,
            from_=TWILIO_PHONE_NUMBER,
            body=crn + " is open register now!!!!"
        )
def registration():
    starttime = time.time()

    term = ('term_in', '202108')
    # Replace with crns you want to track
    crns = ('91031', '91031')

    freq = 2500
    dur = 500
    flag = {i:False for i in crns}
    while True:
        print("Checking waitlist...")
        for crn in crns:

            response = requests.get('https://oscar.gatech.edu/bprod/bwckschd.p_disp_detail_sched', params=(term, ('crn_in', crn)))
            waitlist_section = response.text[response.text.index("Seats"):response.text.index("Waitlist Seats")]
            if list(map(lambda x: int(x), re.findall("ddefault\">(\d)", waitlist_section)))[2] > 0:
                print(crn, 'slot available')
                winsound.Beep(freq, dur)
                if not flag[crn]:
                    flag[crn] = True
                    notify_user(str(crn))
            else:
                print('fuck you')
                flag[crn] = False
            
        time.sleep(3.0 - ((time.time() - starttime) % 3.0))

if __name__ == "__main__":
    registration()