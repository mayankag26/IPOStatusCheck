from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Set up the Chrome WebDriver
driver = webdriver.Chrome()

# Open the website
driver.get("https://linkintime.co.in/initial_offer/public-issues.html")

def handle_dialog():
    """
    Checks for any dialog that may appear, clicks OK, and returns True if a dialog was found.
    Returns False if no dialog is present.
    """
    try:
        dialog = WebDriverWait(driver, 3).until(
            EC.visibility_of_element_located((By.ID, "dialog"))
        )
        # Click the "OK" button to close the dialog
        ok_button = driver.find_element(By.XPATH, "//button[contains(@class, 'ui-button') and text()='Ok']")
        ok_button.click()
        
        # Return True to indicate that a dialog was handled
        return True
    except:
        # No dialog was present
        return False

def submit_form(pan_number):
    while True:  # Retry loop for the current PAN if alert appears
        # Handle any dialog that appears before filling in the form
        while handle_dialog():
            time.sleep(1)  # Optional: short wait before retrying

        try:
            # Select Issue Name
            issue_name_dropdown = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "ddlCompany"))
            )
            issue_name_dropdown.send_keys("Waaree Energies Limited - IPO")

            # Enter PAN number
            pan_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "txtStat"))
            )
            pan_input.clear()
            pan_input.send_keys(pan_number)

            # Click the "Submit" button
            submit_button = driver.find_element(By.ID, "btnsearc")
            submit_button.click()

            # Handle any dialog that appears after clicking the submit button
            if handle_dialog():
                # If the message indicates "Not Applied", move to the next PAN
                message_element = driver.find_element(By.ID, "lblMessage")
                message = message_element.text
                if "no record found" in message.lower():
                    return f"{pan_number} Not Applied\n"  # Move to the next PAN

                # Otherwise, continue the loop to retry with the same PAN
                continue

            # Wait for "tbl_DetSec" (for applied status)
            WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.ID, "tbl_DetSec"))
            )
            securities_allotted_element = driver.find_element(By.XPATH, "//td[contains(text(), 'Securities Allotted')]/following-sibling::td")
            name_element = driver.find_element(By.XPATH, "//td[@class='table_data_name' and contains(text(), 'Sole / 1st Applicant')]/following-sibling::td")
             
            # Extract information
            name = name_element.text            
            securities_allotted = securities_allotted_element.text
            return f"{pan_number} {name} Applied {securities_allotted}\n"  # PAN applied with securities allotted

        except Exception:
            handle_dialog()
            continue

# Read PAN numbers from the file
pan_file_path = './pan.txt'  # Replace with the actual file path
with open(pan_file_path, 'r') as file:
    pan_numbers = file.readlines()

# Loop over each PAN number and submit the form, then collect results
results = []
for pan in pan_numbers:
    pan = pan.strip()  # Remove any trailing newlines or spaces
    if pan:  # Ensure the PAN number is not empty
        result = submit_form(pan)
        print(result)
        results.append(result)
        time.sleep(2)  # Wait for a couple of seconds before processing the next PAN (optional)

# Write the updated results to the same file
with open(pan_file_path, 'w') as file:
    file.writelines(results)

# Close the browser once all PAN numbers are processed
driver.quit()
