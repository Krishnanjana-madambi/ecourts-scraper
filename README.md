Project : eCourts Cause List Scraper

Author: Krishnanjana M D
Date: 16-10-2025
Goal: Fetch court cause lists and case PDFs from eCourts India

*Project Description:
 This Python project scrapes court listings from the eCourts website.

*Key features include:
 -Input state, district, court complex, date, and case type (Civil/    Criminal).
 -Download cause list PDFs for the selected court and date.
 -Save output and metadata as JSON manifest.

*Requirements:
 Python 3.10+
 Packages: pip install streamlit selenium webdriver-manager requests
 Chrome browser installed (for Selenium).

*Setup Instructions:
1.Clone the repository:
  git clone <https://github.com/Krishnanjana-madambi/ecourts-scraper.git>
2.Install dependencies:
  pip install -r requirements.txt
3.Run the Streamlit web app:
  streamlit run app.py
4.Input parameters in the app:
  State (e.g., Delhi)
  District (e.g., New Delhi)
  Court Complex (e.g., District Court Complex)
  Date (dd-mm-yyyy)
  Case Type: Civil or Criminal
5.Captcha handling:
  Enter the captcha value in the terminal input prompt.
6.View results:
  Downloaded PDFs are stored in the output/<state>/<district>/<court_complex>/<date>/ folder.
  Metadata saved in output/<date>_manifest.json.

*For Example:
 Run the app: streamlit run app.py
 Input:
    State: Delhi
    District: New Delhi
    Court Complex: District Court Complex
    Date: 16-10-2025
    Case Type: Civil
 Click Fetch Cause List PDF.
 Check terminal for captcha prompt and enter the code.
 After completion, the app will display downloaded PDFs and the JSON manifest.

