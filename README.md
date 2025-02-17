# CarbonFootprintWebsite
This project enables users to calculate their **carbon impact** based on the consumption of various utilities such as electricity, water, and fuel. It provides insights into environmental impact and potential ways to reduce carbon emissions.  

## Setting Up The Program
First run
```
pip install -r requirements.txt
```
to install all the requirements for the project.
Then either run the `db.sql` file in the `Setup` module, or run the following in your terminal:
```
mysql -u root -p
```
Make sure to replace root with the user available in your system.
Then enter the password for the user. 
Once inside, use the `source` or `\.` command followed by the absolute path to the SQL file as shown below:
```
mysql> source /Setup/db.sql
```
Finally, exit `mysql`, and run the file `run.py`
