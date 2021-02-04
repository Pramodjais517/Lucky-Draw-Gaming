# Lucky-Draw-Gaming
An app for implementing a service which allows users to buy lucky draw tickets and use one ticket to participate in a contest and win exciting prizes.

# Features Implemented
  1) User authentication with email verification.
  2) User can see the list of all upcomnig contests.
  3) User can Buy ticket for any contest with is currently running.
  4) As of now only admin can create lucky draw events choosing start time and end time of game.
  5) Once user places order for ticket he will get a ticket code.
  6) Admin can compute winner and declare it.
  7) API to get all list of events in past one week and corressponding winners.
  
# Set-up
  1) Clone the project using repo link.
  2) Make a python environment (I did it with conda)
  <br><i> conda create -n env_name python==3.7 </i>
  3) Install all the requirements using
  <br><i>pip install -r requirements.txt </i>
  4) move to app directory
  <br> <i> cd luckydraw </i>
  5) Make migrations of the models
  <br>  <i> python manage.py makemigrations </i>
  6) Migrate the migrations to reflect the changes on database.
  <br>   <i> python manage.py migrate </i>
  7) Now, you can create a superuser using below command it would ask for email and password.
  <br>  <i> python manage.py create superuser.</i>
  8) That's it, you can run your local server
  <br>  <i> pythno manage.py runserver</i> 
