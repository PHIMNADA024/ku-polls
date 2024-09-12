# KU Polls: Installation Guide

### 1. Clone the Repository
``` 
git clone https://github.com/PHIMNADA024/ku-polls.git
```
### 2. Navigate to KU Polls Directory
``` 
cd ku-polls
```
### 3. Create a Virtual Environment
``` 
python -m venv venv
```
### 4. Activate the Virtual Environment
* For Linux and macOS:
```
source venv/bin/activate
```
* For Windows:
```
.\venv\Scripts\activate
```
### 5. Install Required Packages
```
pip install -r requirements.txt
```
### 6. Set Up Environment Variables
* For Linux and macOS
```
cp sample.env .env
```
* For Windows:
```
copy sample.env .env
```
### 7. Edit the ```.env``` File 
Open the ```.env``` file in a text editor and update the variables as needed.
### 8. Apply Database Migrations
```
python manage.py migrate
```
### 9. Run Tests to Verify Installation
```
python manage.py test polls
```
### 10. Load KU Polls Data into the Database
1. For Questions and Choices:
```
python manage.py loaddata data/polls-v4.json
```
2. For User data:
```
python manage.py loaddata data/users.json
```
3. For Votes:
```
python manage.py loaddata data/votes-v4.json
```
Or load all data files in one command:
```
python manage.py loaddata data/polls-v4.json data/votes-v4.json data/users.json
```
> **NOTE:** After completing these steps, follow the instructions in [README.md](README.md) to run the application.