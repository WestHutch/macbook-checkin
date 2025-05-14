from playwright.sync_api import sync_playwright
from credentials import get_credentials
import pandas as pd
from datetime import date

def login_destiny():
    page1.goto('https://turnerusd202.follettdestiny.com')
    page1.click('#Login')
    page1.fill('#ID_loginName', user_credentials[2])
    page1.fill('#ID_password', user_credentials[3])
    page1.get_by_role("button", name="Log In").click()
    page1.get_by_role("link", name="Circulation").click()
    page1.get_by_role("link", name="Check In Items").click()
    page1.get_by_role("textbox").click()

def complete_destiny(serialNum):
    page1.get_by_role("textbox").fill(serialNum)
    page1.get_by_role("button", name="Go!").click()
    page1.wait_for_selector('#blockTransactionList', timeout=3000) #will throw an error on first one if a transaction doesnt go through in 3 seconds
    retrievedNumber = str(page1.query_selector("#transactionList > tbody > tr:nth-child(3) > td:nth-child(2) > span.SmallColRow > a").inner_text())
    #the following will throw an error if the device wasnt checked in
    if len(checkedInStudents) != 0: #check if theres any students added to the array yet, without this next line would error out on the first one
        if retrievedNumber == checkedInStudents[len(checkedInStudents)-1]:
            page1.wait_for_timeout(3000)
            retrievedNumber = str(page1.query_selector("#transactionList > tbody > tr:nth-child(3) > td:nth-child(2) > span.SmallColRow > a").inner_text())
            if retrievedNumber == checkedInStudents[len(checkedInStudents)-1]:
                raise Exception("Destiny")
            else:
                return retrievedNumber
        else:
            return retrievedNumber
    else:
        return retrievedNumber

def login_outlook():
    page2.goto('https://outlook.office.com/mail/')
    page2.get_by_placeholder("Email, phone, or Skype").click()
    page2.get_by_placeholder("Email, phone, or Skype").fill(user_credentials[4])
    page2.get_by_role("button", name="Next").click()
    page2.get_by_placeholder("Password").click()
    page2.get_by_placeholder("Password").fill(user_credentials[5])
    page2.get_by_role("button", name="Sign in").click()
    try:
        page2.get_by_role("button", name="Yes").click(timeout=5000)
    except:
        pass

def complete_outlook(studentNumber, sn):
    page2.locator("button").filter(has_text="New mail").click()
    #add addresses to the to field
    page2.get_by_label("To", exact=True).press_sequentially(studentNumber)
    page2.locator("#FloatingSuggestionsItemId0").filter(has_text=studentNumber).click(timeout=10000)
    #fill in body
    page2.get_by_placeholder("Add a subject").fill(f"{studentNumber} Returned Device")
    page2.get_by_label("Message body, press Alt+F10").fill(f"You turned in device {sn}\n\n~Turner Tech Team\n\n")
    page2.locator("button").filter(has_text="Send").click()
    #page2.keyboard.press("Control+Enter")

def check_outlook(studentNumber):
    try:
        page2.goto('https://outlook.office.com/mail/sentitems/')
        page2.get_by_text(studentNumber).hover()
    except:
        #the following writes a comment in excel next to the final serial number that was tried if the sent email isnt found
        excelSheetFrame.iloc[serialNumbers.index(checkedInSerials[len(checkedInSerials)-1]), 1] = "Final email, never sent, check the rest"

def login_ic():
    page3.goto('https://turnerusd202.infinitecampus.org/campus/turner.jsp')
    page3.fill('#username', user_credentials[0])
    page3.fill('#password', user_credentials[1])
    page3.click('#signinbtn')
    page3.get_by_label("Search").hover() #this is here so that IC stays focused until you enter your SSO key

def complete_ic(studentNumber):
    def open_student_page(attempts):
        try:
            page3.get_by_text("#" + studentNumber).click(timeout=2000)
        except:
            attempts += 1
            page3.get_by_label("Search").click()
            if attempts < 5:
                open_student_page(attempts)
    page3.get_by_label("Search").click()
    page3.get_by_placeholder("Student Search...").fill(studentNumber)
    page3.get_by_placeholder("Student Search...").press("Enter")
    #for some reason search minimizes here, needs to be open in order to see next button to click
    open_student_page(0)
    page3.get_by_role("link", name="Student Technology").click()
    page3.frame_locator("iframe[title=\"workspace\"]").frame_locator("iframe[name=\"frameWorkspace\"]").frame_locator("iframe[name=\"frameWorkspaceWrapper\"]").frame_locator("iframe[name=\"frameWorkspaceDetail\"]").get_by_role("textbox", name="Return Date").fill(f"{todaysDate}")
    page3.frame_locator("iframe[title=\"workspace\"]").frame_locator("iframe[name=\"frameWorkspace\"]").frame_locator("iframe[name=\"frameWorkspaceWrapper\"]").frame_locator("iframe[name=\"frameWorkspaceHeader\"]").get_by_role("link", name="Save").click()
    #ensure it saves
    page3.frame_locator("iframe[title=\"workspace\"]").frame_locator("iframe[name=\"frameWorkspace\"]").frame_locator("iframe[name=\"frameWorkspaceWrapper\"]").frame_locator("iframe[name=\"frameWorkspaceDetail\"]").get_by_role("textbox", name="Student Password").click()


user_credentials = get_credentials()
excelSheetFrame = pd.read_excel('checkin_sheet.xlsx')
excelSheetFrame = excelSheetFrame.astype(str) #convert the data to strings, will make empty cells "NaN"
serialNumbers = excelSheetFrame['Serial'].tolist()
#fill error column with empty string (instead of "NaN")
for i in range(len(serialNumbers)):
    excelSheetFrame.iloc[i, 1] = ""

checkedInStudents = []
checkedInSerials = []
todaysDate = date.today().strftime("%m/%d/%y")

#using context manager to make browser close automatically
with sync_playwright() as p:
    browser = p.chromium.launch(headless=False, slow_mo=50)
    context = browser.new_context()

    page1 = context.new_page()
    page2 = context.new_page()
    page3 = context.new_page()
    login_ic()

    page1.bring_to_front()
    login_destiny()
    for serialNumber in serialNumbers:
        try:
            studentNum = complete_destiny(serialNumber)
            checkedInStudents.append(studentNum)
            checkedInSerials.append(serialNumber)
        except:
            excelSheetFrame.iloc[serialNumbers.index(serialNumber), 1] = "Destiny, Email, IC"
    
    page2.bring_to_front()
    login_outlook()
    for checkedInSerial in checkedInSerials:
        try:
            matchingStudent = checkedInStudents[checkedInSerials.index(checkedInSerial)] #anything but an index counter variable, idk why i chose to write it like this
            complete_outlook(matchingStudent, checkedInSerial)
        except:
            excelSheetFrame.iloc[serialNumbers.index(checkedInSerial), 1] = "Email, IC"
    page2.wait_for_timeout(3000) #adding extra time just to make sure the last email sends
    if(len(checkedInStudents) > 0):
        check_outlook(checkedInStudents[len(checkedInStudents)-1]) #check for the last email in sent folder

    page3.bring_to_front()
    for checkedInSerial in checkedInSerials:
        try:
            matchingStudent = checkedInStudents[checkedInSerials.index(checkedInSerial)]
            complete_ic(matchingStudent)
        except:
            excelSheetFrame.iloc[serialNumbers.index(checkedInSerial), 1] = "IC"
    page3.wait_for_timeout(3000)

excelSheetFrame.to_excel('checkin_sheet.xlsx', index=False)