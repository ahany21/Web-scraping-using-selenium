\# Webscraping using Selenium

\#\# \*\*Project Description\*\*

This project automates the collection of alumni data from LinkedIn profiles using \*\*Python\*\* and the \*\*Selenium\*\* library where we also used \*
\*WebDriver\*\* for automation. The script performs automated login, navigates through previously collected LinkedIn profile links, extracts key data, and
exports the results in a structured JSON format. The primary goal is to collect data of alumni who graduated from the \*\*German University in Cairo (GUC)\*\* and
majored in \*\*Media Engineering and Technology (MET)\*\*.

\---

\#\# \*\*Features\*\*

1\. \*\*Automated LinkedIn Login\*\*:  
 \- Uses Selenium WebDriver to sign in to LinkedIn with user-provided credentials.

2\. \*\*Profile Parsing\*\*:  
 \- Extracts key data such as:  
 \- Name  
 \- Gender (using the Genderize API)  
 \- Graduation status  
 \- Age estimation  
 \- Post-graduate studies (Master’s/PhD)  
 \- Work experiences, including:  
 \- Job title  
 \- Work mode (On-site, Hybrid, Remote)  
 \- Start and end dates  
 \- Company name  
 \- Job type (Internship, Full time, Part time)  
 \- Location

3\. \*\*Filters\*\*:  
 \- Data is collected only for alumni who meet the following criteria:  
 \- Graduated from the GUC.  
 \- Majored in MET.

4\. \*\*Export Functionality\*\*:  
 \- Collected data is exported as a JSON file for further use.

\---

\#\# \*\*Dependencies\*\*

1\. \*\*Python\*\*: Ensure Python 3.6+ is installed on your system.  
2\. \*\*Selenium\*\*: Install Selenium using pip:  
\*\*\*\*  
 pip install selenium  
\*\*\*\*  
3.\*\*WebDriver\*\*:For automation  
Download the WebDriver compatible with your browser:  
 Chrome: Download ChromeDriver.  
 Firefox: Download GeckoDriver.  
 Edge: Download EdgeDriver.  
Add the WebDriver to your system's PATH or specify its path in the script.  
4.\*\*Requests\*\*: Install Requests for handling API calls

Code Workflow:  
1\. Input and Authentication  
User provides LinkedIn credentials (username and password).  
Script automates LinkedIn login using Selenium WebDriver.  
2\. Profile Parsing  
The script iterates through profile links stored in links.json.  
Extracted data includes:  
Basic Information: Name, gender.  
Education:  
Post-graduate studies (Master’s, PhD). Masters return 1, PHD return 2 and no postgrad studies return 0  
Graduation date (handled with cases for missing months/years).  
Major and institution validation.  
Work Experience:  
Job title, company name, job type, start/end dates, location, work mode.  
3\. Filtering  
Profiles are included in the final dataset only if:  
The user is a graduate.  
The user majored in MET.  
The user graduated from the GUC.  
4\. Export  
Data is exported to linkedin_profiles.json in a structured format

Helper Functions

1.date_format(month, year):

Converts the given month and year into the format "YYYY-MM-DD".  
Defaults to "June" if no month is provided.

2.is_graduate(end_date):

Checks if the user has graduated by comparing the end_date with the current date.  
Handles missing data gracefully.

3.get_gender(name):

Fetches gender information from the Genderize API based on the first name.

4.get_age(start_year):

Estimates age using the start year of university, assuming an average starting age of 18\.

5.export_to_json(data):

Saves the collected data into a JSON file with proper formatting

Edge Cases Handled

1.Incomplete Profiles:

Missing fields (e.g., no graduation date, no job type) are assigned default values.

2.Dynamic LinkedIn Formats:

The script uses flexible XPath expressions to handle varying structures of LinkedIn profiles.

3.Timeouts:

Profiles that take too long to load are skipped with appropriate logging.

Challenges and Solutions

1.Dynamic Profile Structures:

Used flexible XPaths and fallback logic to extract consistent data.

2.Performance:

Added timeout and delay mechanisms to balance speed and reliability.

3.Data Consistency:

Standardized dates and strings using helper functions.

4.Interrupted Execution:

Signal handling ensures that data is saved even if the script is interrupted.

NOTES:  
IN THE HTML SCRIPTS THE VARYING XPATHS WERE HANDLED AS STATED ABOVE. THE XPATHS WERE DIFFERENT BECAUSE OF THE SECTION NUMBER WHICH DIFFERS FROM ACCOUNT AND ANOTHER
THAT'S WHY I MADE SECTION NUMBER A VARIABLE AND WE CHECK ITS HEADER, MOREOVER THE FORMAT OF THE SECTION ITSELF IS DIFFERENT FOR EXAMPLE
SOME IN THE EXPERIENCE WRITE DESCRIPTION OR SHARE IMAGES AND THIS MAKES THE DIVS EQUAL 2 OR SOME SHARE THEIR MULTIPLE EXPERIENCES OF THE SAME COMPANY AND
THIS HAS ANCHOR ELEMENT WHICH HAS MANY TEXTS FOR EXAMPLE AND ALL OF THIS IS HANDLED IN CODE. I MADE CLASS WE LOOP ON LIKE "artdeco-list\_\_item" WHICH IS SORT OF COMMON FOR ALL
SECTIONS AND THAT'S WHY I LOOP ON IT TO GET ALL EXPERIENCES FOR EXAMPLE, ALSO I USED SUPER DIRECTORIES THAT'S WHY I START XPATHS WITH './'.

WHAT’S MISSING:  
THE SHOW MORE EXPERIENCE, SHOW MORE EDUCATION BUTTON IS NOT WORKING, IT ALWAYS TERMINATES BECAUSE PAGE DOESNT RELOAD.  
APPROACHES I TOOK AND FAILES:  
1)GOING THROUGH ALL SECTIONS THEN CLICKING ON BUTTON, THEN GOING TO NEXT LINK BUT THE OUTCOME IS SUCCESSFULL SCRAPING BUT TERMINATION.  
2)NORMAL CLICKING ON BUTTON, CLICKING BACK BUT OUTCOME ALSO TERMINATION  
3)REDIRECTING TO FEED PAGE AGAIN AND CONTINUE ALSO TERMINATION.
