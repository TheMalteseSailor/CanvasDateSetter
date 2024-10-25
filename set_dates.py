
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys


import requests
import calendar
import argparse
import getpass

from datetime import date, datetime, timedelta

dates = []

def getMonthNumToText(month: int) -> str:
    return calendar.month_name[month][:3]

# May be able to remove
def getDayNumToText(day: int) -> str:
    return calendar.day_name[day][:3]

def addDateToDate(start_date: datetime, days: int) -> datetime:
    new_date = start_date + timedelta(days=days)
    return new_date

def formatDateForOutput(date: datetime, mode: bool) -> str:
    # mode: true=am, false=pm
    hour=min=mode_val=dat_str = ""
    if mode:
        hour = "12"
        min = "00"
        mode_val = "AM"        
        day_str = "Mon"
    else:
        hour = "11"
        min = "59"
        mode_val = "PM"
        day_str = "Sun"
    year = date.year
    month_int = date.month
    month_str = getMonthNumToText(date.month)
    day_int = date.day

    return f"{day_str}, {month_str} {day_int}, {year}, {hour}:{min} {mode_val}"
    

def storeDates(start_date: datetime) -> bool:
    global dates
    week_start_date_str = formatDateForOutput(start_date, True)
    week_start_date_obj = start_date
    
    mod_counter = 1
    while mod_counter < 8:
        #print(f" week_start_date_obj: {week_start_date_obj}")    
        #print(f" week_start_date_str: {week_start_date_str}")
        due_date = addDateToDate(week_start_date_obj, 6)
        stored_date_template = {
            "module":f"{mod_counter}",
            "available": week_start_date_str,
            "due":formatDateForOutput(due_date, False),
        }
    
        dates.append(stored_date_template)
    
        week_start_date_obj = due_date + timedelta(days=1)
        week_start_date_str = formatDateForOutput(week_start_date_obj, True)
        mod_counter += 1
        
    return True

def getToLoginScreen(url: str) -> webdriver.chrome.webdriver.WebDriver:
    driver = webdriver.Chrome()
    driver.set_window_size(1500,800)
    driver.get(url)
    return driver

def login(driver: webdriver.chrome.webdriver.WebDriver, email: str) -> bool:
    driver.find_element(By.ID, "userNameInput").click()
    driver.find_element(By.ID, "userNameInput").send_keys(email)
    # need to hit next button
    driver.find_element(By.ID, "nextButton").click()
    driver.find_element(By.ID, "passwordInput").click()
    password = getpass.getpass()
    driver.find_element(By.ID, "passwordInput").send_keys(password)
    driver.find_element(By.ID, "submitButton").click()
    password = ""
    
    return True

    
def locateAndEnterCourseContext(driver: webdriver.chrome.webdriver.WebDriver, course_sn: str, course_block: str) -> bool:
    while True:
        try:
            element = driver.find_element(By.XPATH, f"//*[contains(@aria-label,'({course_sn}.{course_block})')]")
            subdiv = element.find_element(By.XPATH, ".//a[@class='ic-DashboardCard__link']")
            subdiv.click()
            break
        except:
            sleep(.5)

    return True

def obtainCourseModuleDetails(driver: webdriver.chrome.webdriver.WebDriver) -> list:
    navigateToPage(driver, "modules")
    modules = []
    for module in driver.find_elements(By.XPATH, "//*[contains(@title,'Week ') and @class='name']"):
        module_template = {
            "title": "",
            "assignments": [],
            "open_date": "",
            "due_date": "",
        }
        if "Week " not in module.text:
            continue
        else:
            module_template['title'] = module.text
            
        modules.append(module_template)

    complete_assignment_list = driver.find_elements(By.XPATH, "//*[contains(@title,'Week ') and @class='name']")[0].find_elements(By.XPATH, "//*[@class='ig-title title item_link']")

    #for item in complete_assignment_list:
    #    print(item.text)

    #input("PAUSE")

    for module in modules:
        #print(module)
        in_scope = False
        while len(complete_assignment_list) > 0:
            assignment = complete_assignment_list.pop(0)
            #print(assignment.text)
            if (module['title'] in assignment.text) and (not in_scope): 
                in_scope = True
                #print(f"[*] {module['title']} is now in scope.")
            elif "Week "+str(int(module['title'].split(" ")[-1]) + 1) in assignment.text:
                in_scope = False
                #print(f"[*] {module['title']} is now out of scope.")
                #print(f"[*] Assignments for {module['title']} is {len(module['assignments'])}.")
                print(f"[*] Assignments stored for {module['title']}.")
                break
            elif in_scope:
                module["assignments"].append(assignment.text)
            else: 
                pass
        
        
    print(f"[*] Assignments stored for {module['title']}.")
    
    #for item in modules:
    #    print(item)

    return modules

def navigateToPage(driver, class_name: str) -> None:
    driver.find_element(By.CLASS_NAME, f"{class_name}").click()
    return

def modifyAssignmentDates(driver, modules: list) -> bool:
    navigateToPage(driver, "assignments")
    driver.find_element(By.ID, "course_assignment_settings_link").click()
    driver.find_element(By.ID, "requestBulkEditMenuItem").click()

    driver.find_elements(By.CLASS_NAME, "ellipsis")
    
    
    
    # table starts at element /tr[1]
    # the /td is the horizontal movement.
    #   1/default = click button; 2 = the name of the assignment; 3,4,5 = due, avail from, avail to 
    #driver.find_element(By.XPATH, "//table/tbody/tr[1]/td[2]").click()
    
    count = 0 
    while count <= 1:
        count = len(driver.find_elements(By.XPATH, "//table/tbody/tr"))
        
    print(f" count: {count}")
    #count = 2
    counter = 0
    

    #assign_count = 0
    #associated_module = ""
    #module_set = False
    
    
    while counter <= count:
        counter += 1
        
        # ascertain the module of the assignment.
        assignment_name = ""
        while True:
            try:
                assignment_name = driver.find_element(By.XPATH, f"//table/tbody/tr[{counter}]/td[1]").text.split("Select assignment:")[1].lstrip(" ")
                break
            except:
                sleep(.05)
        #print(assignment_name)
        due_date = ""
        avail_from = ""
        
        
        try:
            module_hit = False
            for module in modules:
                #print(module)
                for assignment in module['assignments']:
                    if assignment_name == assignment:
                        associated_module = module
                        #print(f"module {module['title']} associated...")
                        #module_set = True
                        module_hit = True
                        break
            if associated_module == "":
                continue
            # retrieve the desired dates of the assignment.
            due_date = associated_module['due_date']
        except Exception as ex:
            print(ex)
            input("[!] PAUSED DURRING ERROR HANDNLING TO CHECK STATUS.")
            #break
            continue
        
        avail_from = associated_module['open_date']
        
        #print(due_date)
        #print(avail_from)
        
        # write due date
        #driver.find_element(By.XPATH, f"//table/tbody/tr[{counter}]/td[3]//input").click()        
        driver.find_element(By.XPATH, f"//table/tbody/tr[{counter}]/td[3]//input").send_keys(Keys.CONTROL+"a")
        driver.find_element(By.XPATH, f"//table/tbody/tr[{counter}]/td[3]//input").send_keys(due_date)
        #driver.find_element(By.XPATH, f"//table/tbody/tr[{counter}]/td[3]//input").send_keys(Keys.ENTER)
        
        # write Avail from
        driver.find_element(By.XPATH, f"//table/tbody/tr[{counter}]/td[4]").click()
        driver.find_element(By.XPATH, f"//table/tbody/tr[{counter}]/td[4]//input").send_keys(Keys.CONTROL+"a")
        driver.find_element(By.XPATH, f"//table/tbody/tr[{counter}]/td[4]//input").send_keys(avail_from)
        #driver.find_element(By.XPATH, f"//table/tbody/tr[{counter}]/td[4]//input").send_keys(Keys.ENTER)
        # write Avil until
        # not implemented.
    
    input("Date modificaiton complete. Please review and save.")
    return True


if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(
        prog="Canvas Assignment Dater",
        description="This program will enter assignment dates in Canvas for instructors.",
        epilog="This program comes with no implied support or warranty.")
    
    parser.add_argument('-l','--login-page',type=str,required=True,help="The logon page URL.")
    parser.add_argument('-e','--email',type=str,required=True,help="Your account email.")
    parser.add_argument('-c','--course-sn',type=str,required=True,help="The course's instance number")
    parser.add_argument('-b','--course-block',type=str,required=True,help="The specific block.")
    parser.add_argument('-d','--days-until',type=int,required=True,help="The number of days until the class starts.")
    
    args = parser.parse_args()
    
    days_until = args.days_until
    #start_date = datetime.now() + timedelta(days=4)
    start_date = datetime.now() + timedelta(days=days_until)
    storeDates(start_date)
    for item in dates:
        print(item)    
    
    answer = input("> Are these dates accurate? [y|n] ")
    if (answer.upper() != 'Y'):
        exit()
        
    login_page = args.login_page
    email = args.email
    course_sn = args.course_sn
    course_block = args.course_block
    
    desired_course = f"{course_code}.{course_sn}.{course_block}.{course_mode}"
    
    driver = getToLoginScreen(login_page)
    login(driver, email)
    locateAndEnterCourseContext(driver, course_sn, course_block)
    modules = obtainCourseModuleDetails(driver)
    for module in modules:
        for date in dates:
            if module['title'].split(' ')[-1] == date['module']:
                module['open_date'] = date['available']
                module['due_date'] = date['due']
                break

    modifyAssignmentDates(driver, modules)
