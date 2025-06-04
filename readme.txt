----Installation Instructions--
Install Dependencies:
Ensure that all necessary dependencies are installed. You can do this by following the instructions provided in the project documentation or by running the appropriate commands for your package manager.
-pip install -r requirements.txt



----for database using mysql.---
open mysql and create schema name dashboard

---Install migrate.--
python manage.py makemigrations
python manage.py migrate



---how to use.---

type in terminal python manage.py runserver. 
then run this url. http://localhost:8000/api/get_data to load the data from the sql and then converted to LRUCached

if you want to use live data 
run sql_live_data.py to sync the data for every 4 hours and to load the initial data automatically.

or use cron job..


"Note that this is run at the same time and wait for the initial data to load the data in home page or manually run the url using the http://localhost:8000/api/get_data to load the data. 
Upon successful loading, the output 'Data Loaded Successfully Sheesh!' on the url. then go back to homepage"



---CACHEMANAGER!--
if you want to use LRU cache means loaded the data from ram CachedMEM uncomment the LRU on cacha_manager.py.

if you want to use Disk Cached to load the data from disk uncomment the diskcache.

---------------------------------------------------------------------------------------------------
For troubleshooting

Fixing Caching_sha2_password Error:
If you encounter the "caching_sha2_password" error while connecting to MySQL or add     auth_plugin='mysql_native_password' on settings.py, follow these steps to resolve it






For Linux/Unix:
Restart the MySQL service using the following command:

bash
Copy code
sudo service mysql restart
For Windows:

Open the Windows Services manager.
Locate the MySQL service, right-click, and choose "Stop."
After stopping, right-click again and choose "Start" to restart the MySQL service.
If MySQL is running in the command line:
Restart MySQL by using the following command:

bash
Copy code
mysql restart -p
You will be prompted to enter your MySQL password.

Retry Connection:
After resolving any issues, attempt to connect to MySQL again.

For further assistance or troubleshooting, refer to the project documentation or seek help from the community.