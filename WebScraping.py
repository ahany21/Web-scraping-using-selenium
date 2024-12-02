import time
import signal
import sys
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
from datetime import datetime
import requests

def date_format(month,year):
    months = {
        "Jan": "01", "Feb": "02", "Mar": "03", "Apr": "04",
        "May": "05", "Jun": "06", "Jul": "07", "Aug": "08",
        "Sep": "09", "Oct": "10", "Nov": "11", "Dec": "12"
    }

    return f"{year}-{months[month.capitalize()]}-01"

def is_graduate(end):
    try:
        end_parts = end.split()

        if len(end_parts) == 2:
            month_str, year_str = end_parts
            end_month = month_str[:3].capitalize()
            end_year = int(year_str)

        else:
            end_month = "Jun"
            end_year = int(end_parts[-1])

        months = {
            "Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4,
            "May": 5, "Jun": 6, "Jul": 7, "Aug": 8,
            "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12
        }

        end_month_num = months.get(end_month)
        current_date = datetime.now()
        current_year = current_date.year
        current_month = current_date.month

        if end_year < current_year or (end_year == current_year and end_month_num <= current_month):
            return True

        else:
            return False

    except (ValueError, IndexError) as e:
        print(f"Invalid end date: {end}, error: {e}")
        return False


#API IS USED TO CHECK GENDER
def get_gender(name):
    try:
        req = requests.get(f"https://api.genderize.io?name={name}")
        req.raise_for_status()
        result = req.json()

        if result.get("gender") is not None:
            return 'male' if result["gender"] == 'male' else 'female'

        else:
            return 'male'

    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None  # Return None if there is an error

#AGE IS CALCULATED USING THE START YEAR OF UNIVERSITY BY GETTING DIFFERENCE BETWEEN CURRENT DATE AND HIS/HER UNIVERSITY START YEAR AND SUMMING IT WITH 18 WHICH IS THE AVERAGE
#AGE OF STUDENTS ENTERING UNIVERITY
def get_age(start):
    try:
        start_year = int(start.split()[-1])
        current_year = datetime.now().year
        return (current_year - start_year) + 18
    except (ValueError, IndexError):
        print(f"Invalid start year: {start}")
        return None

#EXPORT FUNCTION TO BE EXPORTED AS JSON FILE TO SPECIFIC FILEPATH
def export_to_json(data):
    file_path = r"C:\Users\Ahmed\Downloads\linkedin_profiles.json"
    with open(file_path, 'w',encoding='utf-8') as json_file:
        json.dump(data, json_file, ensure_ascii=False,indent=4)
    print(f"Data successfully exported to {file_path}")


def linkedin_login():
    username = input("UserName: ")  # Replace with your email
    password = input("PassWord: ")  # Password input hidden
    print("Signing in...")

    driver = webdriver.Chrome()
    all_profiles_data = []

    def export_data():
        export_to_json(all_profiles_data)

    def parse_links():
        nonlocal all_profiles_data
        with open(r"C:\Users\Ahmed\Downloads\links.json") as file:
            data = json.load(file)
        for idx, link in enumerate(data, start=1):
            print(f"{idx}. Visiting: {link}")
            driver.get(link)
            try:
                WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located((By.XPATH, "//section"))
                )
            except TimeoutException:
                print("Page took too long to load. Skipping...")
                continue

            time.sleep(10)  # Adjust this delay based on your internet speed and system performance

            profile_data = {}
            final_post_graduation = 0
            final_major = None
            final_graduation_date = None
            final_age = 0
            is_MET = False
            is_Graduate = False
            in_guc = False
            try:
                name = driver.find_element(By.XPATH,
                    "/html/body/div[5]/div[3]/div/div/div[2]/div/div/main/section[1]/div[2]/div[2]/div[1]/div[1]/span[1]/a/h1").text
                profile_data["name"] = name.strip()
                profile_data["gender"] = get_gender(name)
            except NoSuchElementException:
                print("Name not found")
            sections = driver.find_elements(By.XPATH, "//section")
            for actual_index, section in enumerate(sections, start=1):
                try:
                    header = section.find_element(By.TAG_NAME, 'h2').text.strip()
                    if "Education" in header:
                        education_items = section.find_elements(By.CLASS_NAME, 'artdeco-list__item')
                        for item in education_items:
                            try:
                                degree = item.find_element(By.XPATH,
                                                           ".//div/div[2]/div[1]/a/span[1]/span[1]").text.strip()
                                if "Master" in degree or "PhD" in degree:
                                    final_post_graduation = max(final_post_graduation, 1 if "Master" in degree else 2)

                                MET = ['Computer Engineering', 'Computer Science', 'MET', 'CSE',
                                       'Digital Media Engineering','Computer Software','Software Engineering']
                                for met in MET:
                                    if met.lower() in degree.lower():
                                        final_major = "MET"
                                        is_MET = True
                                        break
                            except NoSuchElementException:
                                print("Degree information not found")
                            try:
                                institution = item.find_element(By.XPATH,
                                                                ".//div/div[2]/div[1]/a/div/div/div/div/span[1]").text.strip()
                                if "GUC" in institution or "guc" in institution or \
                                        "German University in Cairo" in institution or "german university in cairo" in institution:
                                    in_guc = True
                                    try:
                                        duration_text = item.find_element(By.XPATH,
                                                                          ".//div/div[2]/div[1]/a/span[2]/span[1]").text.strip()
                                        if any(char.isdigit() for char in duration_text):
                                            if " - " in duration_text:
                                                start, end = duration_text.split(" - ")
                                                if " " in end:
                                                    final_graduation_date = date_format(*end.split())
                                                else:
                                                    final_graduation_date = date_format("Jun",end)
                                                final_age = get_age(start)
                                                is_Graduate = is_graduate(end)
                                            else:
                                                if " " in duration_text:
                                                    month,year = duration_text.split()
                                                    year = int(year) + 5
                                                    final_graduation_date = date_format(month, year)
                                                else:
                                                    final_graduation_date = date_format("Jun",duration_text)

                                                is_Graduate = is_graduate(duration_text)
                                                final_age = get_age(duration_text)

                                        else:
                                            print("Non-numeric duration format for this item.")
                                    except NoSuchElementException:
                                        print("Duration not found for this item.")
                            except NoSuchElementException:
                                print("Institution information not found")
                            profile_data["postGraduation"] = final_post_graduation
                            profile_data["major"] = final_major
                            profile_data["graduationDate"] = final_graduation_date or 0
                            profile_data["age"] = final_age or "null"

                    elif "Experience" in header:

                        experience_data = []
                        experience_items = section.find_elements(By.CLASS_NAME, "artdeco-list__item")

                        for item in experience_items:
                            work_mode = ['On-site','Hybrid','Remote']
                            experience_details = {}

                            parent_div = item.find_element(By.XPATH, f".//div/div[2]")

                            child_div = parent_div.find_elements(By.XPATH, './*')

                            if len(child_div) == 1:
                                try:
                                    position = parent_div.find_element(By.XPATH,

                                                                       f"./div/div/div/div/div/div/span[1]").text.strip()
                                    print(1.1)
                                    experience_details["jobTitle"] = position.strip()
                                except NoSuchElementException:
                                    print("Position not found for this item. (1)")
                                try:
                                    company = parent_div.find_element(By.XPATH,
                                                                      f"./div/div/span[1]/span[1]").text.strip()
                                    if " · " in company:
                                        company_name, status = company.split(" · ")
                                        experience_details["companyName"] = company_name.strip()
                                        status = status.lower().replace("-", " ")
                                        experience_details["jobType"] = status.strip()
                                    else:
                                        experience_details["companyName"] = company.strip()
                                except NoSuchElementException:
                                    print("Company name not found for this item.(1)")
                                try:
                                    duration_text = parent_div.find_element(By.XPATH,
                                                                            f"./div/div/span[2]/span[1]").text.strip()
                                    if " · " in duration_text:
                                        start_end, duration = duration_text.split(" · ")
                                        if " - " in start_end:
                                            start, end = start_end.split(" - ")
                                            if " " in start:
                                                start_month, start_year = start.split()
                                                experience_details["startDate"] = date_format(start_month, start_year)
                                            else:
                                                experience_details["startDate"] = date_format("Jun",start)
                                            if "Present" in end or "present" in end:
                                                experience_details["endDate"] = "present"
                                            else:
                                                if " " in end:
                                                    end_month, end_year = end.split()
                                                    experience_details["endDate"] = date_format(end_month, end_year)
                                                else:
                                                    experience_details["endDate"] = date_format("Jun",end)
                                        else:
                                            start_month, start_year = start_end.split()
                                            experience_details["startDate"] = date_format(start_month, start_year)
                                    else:
                                        start_month, start_year = duration_text.split()
                                        experience_details["startDate"] = date_format(start_month, start_year)
                                except NoSuchElementException:
                                    print("Duration not found for this item.(1)")
                                try:
                                    location_text = parent_div.find_element(By.XPATH,
                                                                            f"./div/div/span[3]/span[1]").text.strip()
                                    if " · " in location_text:
                                        first,second = location_text.split(" · ")
                                        for work in work_mode:
                                            if work in first:
                                                work = work.lower()
                                                experience_details["workMode"] = work
                                                experience_details["location"] = second.strip()
                                            if work in second:
                                                work = work.lower()
                                                experience_details["workMode"] = work
                                                experience_details["location"] = first.strip()
                                    else:
                                        for work in work_mode:
                                            if work in location_text:
                                                work = work.lower()
                                                experience_details["workMode"] = location_text.strip()
                                            else:
                                                experience_details["location"] = location_text.strip()


                                except NoSuchElementException:

                                    print("Location not found for this item.")

                            elif len(child_div) == 2:
                                co_name = ""
                                jo_type = ""
                                wo_mo = ""
                                lo = ""
                                try:
                                    company_name = parent_div.find_element(By.XPATH,

                                                                           f"./div[1]/div/span[1]/span[1]").text.strip()
                                    if " · " in company_name:

                                        company, status = company_name.split(" · ")

                                        experience_details["companyName"] = company.strip()
                                        status = status.replace('-', ' ')
                                        status = status.lower()
                                        experience_details["jobType"] = status.strip()
                                    else:
                                        experience_details["companyName"] = company_name.strip()


                                except NoSuchElementException:
                                    try:
                                        company_name = parent_div.find_element(By.XPATH,
                                                                               f"./div[1]/a/div/div/div/div/span[1]").text.strip()

                                        #experience_details["companyName"] = company_name
                                        co_name = company_name
                                    except NoSuchElementException:
                                        print("Company name not found for this item.")

                                try:

                                    range_duration = parent_div.find_element(By.XPATH,

                                                                             f"./div[1]/div/span[2]/span[1]").text.strip()


                                    if " · " in range_duration:

                                        start_end, duration = range_duration.split(" · ")

                                        if " - " in start_end:

                                            start, end = start_end.split(" - ")
                                            start_month, start_year = start.split()
                                            experience_details["startDate"] = date_format(start_month, start_year)
                                            if "Present" in end or "present" in end:
                                                experience_details["endDate"] = "present"
                                            else:
                                                end_month, end_year = end.split()
                                                experience_details["endDate"] = date_format(end_month, end_year)

                                        else:
                                            start_month, start_year = start_end.split()
                                            experience_details["startDate"] = date_format(start_month, start_year)


                                except NoSuchElementException:

                                    try:
                                        status_duration = parent_div.find_element(By.XPATH,
                                                                                  f"./div[1]/a/span/span[1]").text.strip()

                                        if " · " in status_duration:
                                            status, duration = status_duration.split(" · ")
                                            status = status.lower().replace("-", " ")

                                            #experience_details["jobType"] = status.strip()
                                            jo_type = status
                                    except NoSuchElementException:
                                        print("Duration not found for this item.")
                                try:

                                    location_text = parent_div.find_element(By.XPATH,

                                                                            f"./div[1]/div/span[3]/span[1]").text.strip()


                                    if " · " in location_text:

                                        location, job_type = location_text.split(" · ")

                                        experience_details["location"] = location.strip()

                                        job_type = job_type.lower()

                                        experience_details["workMode"] = job_type.strip()

                                    else:
                                        for work in work_mode:
                                            if work in location_text:
                                                work = work.lower()
                                                experience_details["workMode"] = work
                                            else:
                                                experience_details["location"] = location_text.strip()


                                except NoSuchElementException:

                                    try:
                                        range_duration = parent_div.find_element(By.XPATH,
                                                                                f"./div[1]/a/span[2]/span[1]").text.strip()

                                        if " · " in range_duration:
                                            range, duration = range_duration.split(" · ")
                                            for womo in work_mode:
                                                if duration in womo:
                                                    womo = womo.lower()
                                                    wo_mo = womo
                                            #experience_details["location"] = location.strip()
                                            if " - " in range:

                                                start, end = range.split(" - ")
                                                start_month, start_year = start.split()
                                                experience_details["startDate"] = date_format(start_month, start_year)
                                                if "Present" in end or "present" in end:
                                                    experience_details["endDate"] = "present"
                                                else:
                                                    end_month, end_year = end.split()
                                                    experience_details["endDate"] = date_format(end_month, end_year)
                                            else:
                                                lo = range.strip()
                                        else:
                                            lo = range_duration.strip()
                                    except NoSuchElementException:
                                        print("Location not found for this item.")

                                try:
                                    # Handling single position
                                    position = parent_div.find_element(By.XPATH,
                                                                       f"./div[1]/div/div/div/div/div/span[1]").text.strip()
                                    JobLevels = ['junior', 'senior', 'manager', 'techlead', 'associate']
                                    experience_details["jobTitle"] = position
                                    if "Junior Teaching Assistant" in position:
                                        experience_details["jobType"] = "part time"

                                except NoSuchElementException:

                                    multiple_roles = parent_div.find_element(By.XPATH, "./div[2]/ul")

                                    roles_child = multiple_roles.find_elements(By.XPATH, "./li")

                                    for role in roles_child:

                                        role_details = {}

                                        try:

                                            position = role.find_element(By.XPATH,

                                                                         f"./div/div[2]/div/a/div/div/div/div/span[1]").text.strip()

                                            role_details["jobTitle"] = position

                                        except NoSuchElementException:

                                            print("Position not found for this item.")

                                        try:

                                            sub_duration = role.find_element(By.XPATH,

                                                                             f"./div/div[2]/div/a/span[1]/span[1]").text.strip()

                                            if " · " in sub_duration:

                                                start_end, duration = sub_duration.split(" · ")

                                                if " - " in start_end:

                                                    start, end = start_end.split(" - ")
                                                    start_month, start_year = start.split()
                                                    #end_month, end_year = end.split()
                                                    role_details["startDate"] = date_format(start_month, start_year)
                                                    if "Present" in end or "present" in end:
                                                        role_details["endDate"] = "present"
                                                    else:
                                                        end_month, end_year = end.split()
                                                        role_details["endDate"] = date_format(end_month, end_year)

                                                else:
                                                    start_month, start_year = start_end.split()
                                                    role_details["startDate"] = date_format(start_month, start_year)
                                            else:
                                                sub_duration = sub_duration.lower().replace("-", " ")
                                                role_details["job_type"] = sub_duration.strip()


                                        except NoSuchElementException:

                                            print("Duration not found for this item.")

                                        try:

                                            range_duration = role.find_element(By.XPATH,

                                                                         f"./div/div[2]/div/a/span[2]/span[1]").text.strip()
                                            if " · " in range_duration:

                                                ranges,duration = range_duration.split(" · ")
                                                for womo in work_mode:
                                                    if duration in womo:
                                                        womo = womo.lower()
                                                        wo_mo = womo
                                                if " - " in ranges:
                                                    start, end = ranges.split(" - ")
                                                    start_month, start_year = start.split()
                                                    role_details["startDate"] = date_format(start_month, start_year)
                                                    if "Present" in end or "present" in end:
                                                        experience_details["endDate"] = "present"
                                                    else:
                                                        end_month, end_year = end.split()
                                                        role_details["endDate"] = date_format(end_month, end_year)
                                            else:
                                                role_details["location"] = range_duration.strip()
                                        except NoSuchElementException:
                                            print("Location not found for this item.")

                                        try:
                                            erd_nest = role.find_element(By.XPATH,"./div/div[2]/div[1]/a/span[2]/span[1]").text.strip()
                                            if " · " in erd_nest:
                                                first,second = erd_nest.split(" · ")
                                                for womo in work_mode:
                                                    if first in womo:
                                                        womo = womo.lower()
                                                        wo_mo = womo
                                                    if second in womo:
                                                        womo = womo.lower()
                                                        wo_mo = womo
                                            else:
                                                for womo in work_mode:
                                                    if erd_nest in womo:
                                                        womo = womo.lower()
                                                        wo_mo = womo
                                        except NoSuchElementException:
                                            print("element not found for this item.")

                                        # Adding companyName and jobType to each role
                                        if co_name:
                                            role_details["companyName"] = experience_details.get("companyName", co_name)
                                        if jo_type:
                                            role_details["jobType"] = experience_details.get("jobType", jo_type)
                                        if wo_mo:
                                            role_details["workMode"] = experience_details.get("workMode", wo_mo)
                                        if lo:
                                            role_details["location"] = experience_details.get("location", lo)

                                        # Append each role directly to experience_data

                                        experience_data.append(role_details)

                            if experience_details:
                                experience_data.append(experience_details)

                        profile_data["experiences"] = experience_data


                except NoSuchElementException:
                    continue

            if not in_guc:
                print("didnt enter guc")
            elif not is_Graduate:
                print("still undergrad")
            elif not is_MET:
                print("didnt enter met")
            else:
                all_profiles_data.append(profile_data)
                print(f"Profile data: {profile_data}")
        return all_profiles_data

    def handle_signal(signal, frame):
        print("Termination signal received. Exporting data...")
        export_data()
        sys.exit(0)

    signal.signal(signal.SIGINT, handle_signal)  # Handle Ctrl+C
    signal.signal(signal.SIGTERM, handle_signal)  # Handle termination signal

    try:
        driver.get("https://www.linkedin.com/login")
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.ID, "username"))
        ).send_keys(username)  # Inputting username
        driver.find_element(By.ID, "password").send_keys(password)  # Inputting password
        driver.find_element(By.XPATH, "//button[contains(@class, 'btn__primary')]").click()  # Clicking the login button

        try:
            WebDriverWait(driver, 15).until(
                EC.url_contains("https://www.linkedin.com/feed/")
            )
            print("Logged In Successfully")
            parse_links()
        except TimeoutException:
            print("Login did not land on the feed page. Please verify manually.")
            input("After verifying, press Enter to continue...")
            if driver.current_url.startswith("https://www.linkedin.com/feed/"):
                print("Now on feed page. Proceeding to parse links.")
                parse_links()
            else:
                print("Still not on feed page. Exiting...")
                return

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        driver.quit()
        export_data()


linkedin_login()