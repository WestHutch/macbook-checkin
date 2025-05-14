This is only to be used by THS/TMS techs to automate the process for MacBook check-in.

Upon first running the program, you will be prompted to enter your credentials for each step. After that, the program will never ask you again. If you entered these incorrectly, you can simply edit them in the userinfo.txt file that was created.

To run this program...
  1. Ensure python is installed on your machine
  2. Download this repo to your desktop, and unzip it
  3. In the checkin_sheet Excel doc, fill the Serial colum
  4. In the command prompt, naviate to where you have this repo saved
     
       `cd Desktop\macbook_checkin-main\macbook_checkin-main`
  5. Run the following commands sequentially. This will ensure you have all necessary packages installed

       `python -m venv venv`
     
       `venv\Scripts\activate.bat`
     
       `pip install -r requirements.txt`
  6. Run the main script

       `python main.py`
