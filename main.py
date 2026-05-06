from playwright.sync_api import sync_playwright
from credentials import get_user_info, set_credentials, write_school_info
import pandas as pd
from datetime import date
import argparse

def login_destiny(page1, user_credentials):
    page1.goto('https://turnerusd202.follettdestiny.com', timeout=180000)
    if user_credentials["school"] == "m":
        page1.get_by_text("Turner Middle School").click(timeout=180000)
    else:
        page1.get_by_text("Turner High School").click(timeout=180000)

    page1.click('#toolbar-guest-login-btn', timeout=180000)
    page1.fill('#userName', user_credentials["destiny_user"])
    page1.fill('#userPassword', user_credentials["destiny_pw"])
    page1.get_by_role("button", name="Log in", exact=True).click()
    page1.locator('#portal-spinner circle').nth(1).wait_for(state='visible', timeout=180000)
    page1.locator('#portal-spinner circle').nth(1).wait_for(state='hidden')
    page1.click("#app-switch-button")
    page1.get_by_text("Back Office").click()
    page1.get_by_text("Circulation", exact=True).click(timeout=180000)
    try:
        page1.get_by_role("button", name="Check In Items", exact=True).click(timeout=10000)
        page1.locator('[id="Library Manager"]').content_frame.locator("input[name='barcode']").click(timeout=10000)
    except:
        page1.get_by_role("button", name="Check In Items", exact=True).click(timeout=10000)
        page1.locator('[id="Library Manager"]').content_frame.locator("input[name='barcode']").click()
    page1.locator('[id="Library Manager"]').content_frame.locator("input[name='barcode']").click()

def complete_destiny(serialNum, page1, checkedInStudents):
    page1.locator('[id="Library Manager"]').content_frame.locator("input[name='barcode']").fill(serialNum)
    page1.locator('[id="Library Manager"]').content_frame.get_by_role("button", name="Go!").click()
    page1.locator('[id="Library Manager"]').content_frame.locator('#blockTransactionList').hover(timeout=3000) #will throw an error on first one if a transaction doesnt go through in 3 seconds
    retrievedNumber = str(page1.locator('[id="Library Manager"]').content_frame.locator("#transactionList > tbody > tr:nth-child(3) > td:nth-child(2) > span.SmallColRow > a").inner_text())
    
    #the following will throw an error if the device wasnt checked in
    if len(checkedInStudents) != 0: #check if theres any students added to the array yet, without this next line would error out on the first one
        if retrievedNumber == checkedInStudents[len(checkedInStudents)-1]: #if it accidentally grabbed the previous checkin student num...
            page1.wait_for_timeout(3000)
            retrievedNumber = str(page1.locator('[id="Library Manager"]').content_frame.locator("#transactionList > tbody > tr:nth-child(3) > td:nth-child(2) > span.SmallColRow > a").inner_text())
            if retrievedNumber == checkedInStudents[len(checkedInStudents)-1]:
                raise Exception("Destiny")
            else:
                return retrievedNumber
        else:
            return retrievedNumber
    else:
        return retrievedNumber

def login_outlook(page2, user_credentials):
    page2.goto('https://outlook.office.com/mail/')
    page2.get_by_placeholder("Email, phone, or Skype").click()
    page2.get_by_placeholder("Email, phone, or Skype").fill(user_credentials["checkin_email"])
    page2.get_by_role("button", name="Next").click()
    page2.get_by_placeholder("Password").click()
    page2.get_by_placeholder("Password").fill(user_credentials["checkin_email_pw"])
    page2.get_by_role("button", name="Sign in").click()
    try:
        page2.get_by_role("button", name="Yes").click(timeout=5000)
    except:
        pass
    page2.wait_for_timeout(3000)

def complete_outlook(studentNumber, sn, page2):
    page2.wait_for_timeout(1000)
    page2.get_by_role("button", name="New mail").first.click()
    page2.wait_for_timeout(3000) #bad practice, but it lets you type before the element is accepting text
    #add addresses to the to field
    page2.get_by_label("To", exact=True).press_sequentially(studentNumber)
    page2.locator("#FloatingSuggestionsItemId0").filter(has_text=studentNumber).click(timeout=10000)
    #fill in body
    page2.get_by_placeholder("Add a subject").fill(f"{studentNumber} Returned Device")
    page2.get_by_label("Message body", exact=True).fill(f"You turned in device {sn}\n\n~Turner Tech Team\n\n")
    page2.wait_for_timeout(2000)
    page2.keyboard.press("Control+Enter")

def check_outlook(studentNumber, page2, excelSheetFrame, serialNumbers, checkedInSerials):
    try:
        page2.goto('https://outlook.office.com/mail/sentitems/')
        page2.get_by_text(studentNumber).first.hover()
    except:
        #the following writes a comment in excel next to the final serial number that was tried if the sent email isnt found
        excelSheetFrame.iloc[serialNumbers.index(checkedInSerials[len(checkedInSerials)-1]), 1] = "Final email, never sent, check the rest"

def login_ic(page3, user_credentials):
    page3.goto('https://turnerusd202.infinitecampus.org/campus/turner.jsp')
    page3.fill('#username', user_credentials["ic_user"])
    page3.fill('#password', user_credentials["ic_pw"])
    page3.click('#signinbtn')
    page3.get_by_label("Search").first.hover() #this is here so that IC stays focused until you enter your SSO key

def complete_ic(studentNumber, page3, todaysDate):
    def open_student_page(attempts):
        try:
            page3.get_by_placeholder("Student Search...").fill(studentNumber, timeout=2000)
            page3.get_by_placeholder("Student Search...").press("Enter", timeout=2000)
            page3.get_by_text("#" + studentNumber).click(timeout=2000)
        except:
            attempts += 1
            page3.get_by_label("Search").first.click()
            if attempts < 5:
                open_student_page(attempts)
    page3.get_by_label("Search").first.click()
    page3.get_by_placeholder("Student Search...").fill(studentNumber)
    page3.get_by_placeholder("Student Search...").press("Enter")
    #for some reason search minimizes here, needs to be open in order to see next button to click
    open_student_page(0)
    page3.get_by_role("link", name="Student Technology").click()
    page3.frame_locator("iframe[title=\"workspace\"]").frame_locator("iframe[name=\"frameWorkspace\"]").frame_locator("iframe[name=\"frameWorkspaceWrapper\"]").frame_locator("iframe[name=\"frameWorkspaceDetail\"]").get_by_role("textbox", name="Return Date").fill(f"{todaysDate}")
    page3.frame_locator("iframe[title=\"workspace\"]").frame_locator("iframe[name=\"frameWorkspace\"]").frame_locator("iframe[name=\"frameWorkspaceWrapper\"]").frame_locator("iframe[name=\"frameWorkspaceHeader\"]").get_by_role("link", name="Save").click()
    #ensure it saves
    page3.frame_locator("iframe[title=\"workspace\"]").frame_locator("iframe[name=\"frameWorkspace\"]").frame_locator("iframe[name=\"frameWorkspaceWrapper\"]").frame_locator("iframe[name=\"frameWorkspaceDetail\"]").get_by_role("textbox", name="Student Password").click()

def main():
    parser = argparse.ArgumentParser(description="Broken device script")
    parser.add_argument("--reset-credentials", action="store_true", dest="reset_credentials", help="Reset stored credentials before running")
    parser.add_argument("--reset-school-info", action="store_true", dest="reset_school_info", help="Reset stored school information before running")
    args = parser.parse_args()

    if args.reset_credentials:
        set_credentials()
    
    if args.reset_school_info:
        write_school_info()


    user_credentials = get_user_info()
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
        login_ic(page3, user_credentials)

        page1.bring_to_front()
        login_destiny(page1, user_credentials)
        for serialNumber in serialNumbers:
            try:
                studentNum = complete_destiny(serialNumber, page1, checkedInStudents)
                checkedInStudents.append(studentNum)
                checkedInSerials.append(serialNumber)
            except:
                excelSheetFrame.iloc[serialNumbers.index(serialNumber), 1] = "Destiny, Email, IC"
        
        page2.bring_to_front()
        login_outlook(page2, user_credentials)
        for checkedInSerial in checkedInSerials:
            try:
                matchingStudent = checkedInStudents[checkedInSerials.index(checkedInSerial)] #anything but an index counter variable, idk why i chose to write it like this
                complete_outlook(matchingStudent, checkedInSerial, page2)
            except:
                excelSheetFrame.iloc[serialNumbers.index(checkedInSerial), 1] = "Email, IC"
        page2.wait_for_timeout(3000) #adding extra time just to make sure the last email sends
        if(len(checkedInStudents) > 0):
            check_outlook(checkedInStudents[len(checkedInStudents)-1], page2, excelSheetFrame, serialNumbers, checkedInSerials) #check for the last email in sent folder

        page3.bring_to_front()
        for checkedInSerial in checkedInSerials:
            try:
                matchingStudent = checkedInStudents[checkedInSerials.index(checkedInSerial)]
                complete_ic(matchingStudent, page3, todaysDate)
            except:
                excelSheetFrame.iloc[serialNumbers.index(checkedInSerial), 1] = "IC"
        page3.wait_for_timeout(3000)

    excelSheetFrame.to_excel('checkin_sheet.xlsx', index=False)

if __name__ == "__main__":
    main()