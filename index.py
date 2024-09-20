from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from datetime import datetime
import webbrowser  # Import webbrowser

# Set up the Chrome WebDriver
driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))

# URLs
login_url = "https://login.microsoftonline.com/87c50b58-2ef2-423d-a4db-1fa7c84efcfa/saml2?SAMLRequest=lZJBb%2BIwEIX%2FSuR7cGICSSxAYuGwSO2CINtDb44zoZacMfU43fbfN0BXSy9Ie%2FX4e%2FPe08xIdfYkl314wT289kAheu8skrwM5qz3KJ0iQxJVBySDlofl44MUo0SevAtOO8tukPuEIgIfjEMWbdZzttruq22Z56kGXbTFdDpJi3TaiLLMiiyHuhZNXY%2BFFuNxWrLoCTwN7JwNUoMAUQ8bpKAwDE%2BJyOKkjEVSpUJOSplkzyxaD3kMqnChXkI4keTcuqPBUWe0d%2BTa4NAahJF2HS9yPUnqSRELaEWciXETq6yp47RVuS4yaHWr%2BDmlYNHyb5SVQ%2Bo78Afwb0bD7%2F3Dv1WAx7M29b7VDuE9jNByNZQNGIy%2B%2BOJ04voqEd%2FUs%2Fvq9ofBxuDxfq319RPJn1W1i3fbQ8UWs7NPeSnJL%2F7TTwdBNSqoGb8VmV1v5dewfrPeOWv0R7S01v1ZeVAB5iz4HhhfXKnvR7X4BA%3D%3D&sso_reload=true"
url = "https://brightspace.avans.nl/d2l/lms/dropbox/user/folders_list.d2l?ou=155026&isprv=0"

# Navigate to the login page
driver.get(login_url)

# Wait for the email input and enter the email
email_input = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.ID, 'i0116')))
email_input.send_keys('EMAIL - HERE', Keys.RETURN)
time.sleep(1)

# Wait for the password input and enter the password
password_input = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.NAME, 'passwd')))
password_input.send_keys('PASS - HERE', Keys.RETURN)
time.sleep(1)

# Wait for the "Next" button and click it
next_button = WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.ID, 'idSIButton9')))
next_button.click()
time.sleep(1)

# Wait for the assignments page to load
driver.get(url)

# Wait for the page title to contain "Assignments"
WebDriverWait(driver, 30).until(EC.title_contains("Assignments"))

assignment_rows = WebDriverWait(driver, 30).until(
    EC.presence_of_all_elements_located((By.XPATH, "//th[contains(@class, 'd_ich') and contains(@class, 'd2l-table-cell-first')]"))
)

assignments = []

# Extract assignments
for row in assignment_rows:
    try:
        title = row.find_element(By.XPATH, './/strong').text.strip()
        due_date_wrapper = row.find_element(By.CLASS_NAME, 'dco.d2l-folderdates-wrapper')
        due_date_element = due_date_wrapper.find_element(By.CLASS_NAME, 'dco.d2l-dates-text')
        due_date_text = due_date_element.text.strip()

        if due_date_text:
            due_date = datetime.strptime(due_date_text, 'Due on %b %d, %Y %I:%M %p')
            assignments.append((title, due_date))

    except Exception as e:
        print(f"Error extracting assignment: {e}")

# Sort assignments by due date
assignments.sort(key=lambda x: x[1])

# Generate HTML content
html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Assignments Output</title>
    <style>
        body { font-family: Arial, sans-serif; }
        table { width: 100%; border-collapse: collapse; }
        th, td { padding: 8px; text-align: left; border: 1px solid #ccc; }
        th { background-color: #f2f2f2; }
        .past-due { background-color: #ffcccc; }  /* Light red background for past due dates */
    </style>
</head>
<body>
    <h1>Extracted Assignments</h1>
    <table>
        <tr>
            <th>Assignment Title</th>
            <th>Due Date</th>
        </tr>
"""

# Add assignment data to the HTML content
for title, due_date in assignments:
    row_class = 'past-due' if due_date < datetime.now() else ''  # Check if due date is in the past
    html_content += f"""
        <tr class="{row_class}">
            <td>{title}</td>
            <td>{due_date.strftime('%Y-%m-%d %I:%M %p')}</td>
        </tr>
    """

html_content += """
    </table>
</body>
</html>
"""

# Write the HTML content to a file
output_file = 'assignments_output.html'
with open(output_file, 'w') as f:
    f.write(html_content)

print(f"HTML file has been generated: {output_file}")

# Automatically open the HTML file in the default web browser
webbrowser.open(output_file)

# Close the driver
driver.quit()
