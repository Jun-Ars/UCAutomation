# Cisco Unified Communications Manager Administration Automation
*Automation for a Cisco Unified Communications environment.*

### Usage
___
1. Install Python 3
2. *(Optional)* Create/activate a Python virtual environment to segregate project related dependencies from global packages using:
    ```
    python -m venv venv
    venv\Scripts\activate.ps1
    ```
3. Install needed dependency packages:
    ```
    pip install -r requirements.txt
    ```
4. Run the 'UCAutomation.py' file in your shell:
    1. From Powershell:
   ```
   python .\UCAutomation.py
   ```
   2. From Python Shell:
   ```
   exec(open("UCAutomation.py").read())
   ```
