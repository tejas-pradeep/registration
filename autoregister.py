import sys
import re
import time
import argparse
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait

CHROMEDRIVER_PATH = 'chromedriver' # assumes driver is in current working directory
LOGIN_URL = 'https://login.gatech.edu/cas/login?service=https%3A%2F%2Fsso.sis.gatech.edu%3A443%2Fssomanager%2Fc%2FSSB'
REGISTRATION_URL = 'https://oscar.gatech.edu/bprod/bwskfreg.P_AltPin' # will redirect to term selection if needed
QUERY_URL = 'https://oscar.gatech.edu/bprod/bwckschd.p_disp_detail_sched?term_in={term:n}&crn_in={crn:n}' # use .format

term_dict = {'02': 'Spring', '05': 'Summer', '08': 'Fall'}
auth_dict = {'push': 0, 'call': 1, 'pass': 2} # i know there are better ways

# https://docs.python.org/3/library/argparse.html#the-add-argument-method
parser = argparse.ArgumentParser(description='Monitor course(s) status and register or waitlist when available.')
parser.add_argument('crns', metavar='C', type=str, nargs='+', help='a five-digit Course Registration Number')
parser.add_argument('--username', '--user', required=True, help='your GaTech username, e.g. gburdell0')
parser.add_argument('--password', '--pass', required=True, help='your GaTech password (don\'t worry, it won\'t be saved)')
parser.add_argument('--authentication', '--auth', choices=['push', 'call', 'pass'], default='push', help='type of two-factor authentication to use')
parser.add_argument('-w', '--waitlist', action='store_true', help='attempt to waitlist if possible')
parser.add_argument('-s', '--show', action='store_true', help='show browser session in new window')
parser.add_argument('-t', '--term', help='term code in the form YYYYSS with Spring=02, Summer=05, Fall=08 (e.g. Spring 2021 is 202102)')


def keepActive():
	if 'https://oscar.gatech.edu/bprod/bwskfreg.P_AltPin' in driver.current_url: # registration page
		driver.find_element_by_xpath("//form/input[21]").click() # reset (clear CRN fields)
	else:
		print('WARNING: trying to keep unknown page active')

def register(driver, crn, waitlist=True, field_index=0):
	'''attempts to register for a specific course'''
	# for i, crn in enumerate(sys.argv[1:], 1): # enumerate from index 1
	
	# TODO error handling (if full and/or waitlistable)

def main():
	args = parser.parse_args(sys.argv[1:]) # omit program name (sys.argv[0]) from args

	options = webdriver.ChromeOptions()
	options.add_argument('start-maximized' if args.show else 'headless')
	anonDriver = webdriver.Chrome(CHROMEDRIVER_PATH, options=options)
	anonDriver.implicitly_wait(3)
	driver = webdriver.Chrome(CHROMEDRIVER_PATH, options=options)
	driver.implicitly_wait(3)
	
	driver.get(LOGIN_URL)
	driver.find_element_by_id('username').send_keys(args.username)
	driver.find_element_by_id('password').send_keys(args.password)
	driver.find_element_by_xpath('//*[@id="login"]/div[5]/input[4]').click()
	driver.switch_to.frame(driver.find_element_by_id('duo_iframe'))
	div_auth = driver.find_element_by_id("auth_methods")
	div_auth.find_elements_by_xpath('//button[@type=\'submit\']')[auth_dict[args.authentication]].click()
	driver.switch_to.default_content()
	print(args.authentication.capitalize(), 'authentication requested. Please verify login attempt.')
	WebDriverWait(driver, timeout=30).until(lambda d: d.find_elements_by_name('StuWeb-MainMenuLink'))
	print('Logged in.')
	
	if term_code := args.term: # if a term code was included as an argument from command line
		driver.get(REGISTRATION_URL + '?term_in=' + term_code) # go straight to semester registration
	else:
		driver.get(REGISTRATION_URL)
		combobox = driver.find_element_by_id('term_id')
		for option in combobox.find_elements_by_tag_name('option'): # traverse dropdown
			if not ('View only' in option.text or 'Language' in option.text):
				option.click() # select latest valid semester
				driver.find_element_by_xpath('//form/input').click() # submit
				term_code = option.get_attribute('value')
	print('Assuming term', term_dict[term_code[4:]], term_code[:4], '.')

	driver.execute_script("window.open('');") # open new tab for querying
	while True:
		driver.switch_to_window(driver.window_handles[1]) # switch to second tab
		if driver.title is not '':
			
		for crn in args.crns:
			# TODO handle when 2 crns must be reigstered simultaneously
			driver.get(QUERY_URL.format(term_code, crn))
			# read seats available

			if seats_rem > 0 or waitlist_rem > 0: # todo check this is how it's displayed
				# TODO attempt to register
				# switch tabs
				driver.find_element_by_id('crn_id' + str(field_index + 1)).send_keys(crn) # add CRN
				driver.find_element_by_xpath("//form/input[19]").click() # submit changes
				# TODO check if registration worked, handle accordingly

		time.sleep(2)

	driver.quit()


if __name__ == '__main__':
	main()
