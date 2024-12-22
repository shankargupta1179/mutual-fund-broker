# mutual-fund-broker

## Prerequisites 
We need to have an API key and API Host of Rapid Api to run this project successfully . Just create an account in this https://rapidapi.com/suneetk92/api/latest-mutual-fund-nav and you will get the required key and host

## Installation and Running in Local
First clone the repository and run this command 
`pip install -r requirements.txt`
<br>After successfull installation of requirements , you can use this command to run the app locally 
`python run.py`
<br>
 **Please make sure to set the Rapid Api key and Host in the .env file**

## Import Postman Collection 
There is a postman collection json file in the repository . You can login to the Postman tool and just import this file to have the collection on your postman tool

## Postman Script
![image](https://github.com/user-attachments/assets/98327849-7e15-4a1b-adfc-1574f4559eba)

There is a javascript code written in the login script which sets the access token in the environment avoiding manual copy pasting of token while running the apis 

## End to End testing
To run End to End tests , just open command prompt at the directory where this project resides and run the command `python  test_routes.py` 


## Screenshots of testing 

### Success 
![image](https://github.com/user-attachments/assets/4234fefb-db87-40f3-8011-af02369d0df4)
![image](https://github.com/user-attachments/assets/9a30a804-8eb4-4f7c-a3f6-fb954a8b5431)
![image](https://github.com/user-attachments/assets/d6bbbce6-2a04-4eff-ab94-6a816ccdf4e7)
![image](https://github.com/user-attachments/assets/39155fb9-4ed1-4959-8cea-7e86fb83eb77)

### Failure
![image](https://github.com/user-attachments/assets/a33ab05c-0244-4f32-ba65-b69e459ee37f)
![image](https://github.com/user-attachments/assets/e449892b-086c-423e-a0ef-418e14bb088e)
![image](https://github.com/user-attachments/assets/6ea3f09b-b3e0-4fd2-93d3-82db514c6d56)
![image](https://github.com/user-attachments/assets/7962a0d8-84d6-4bf0-8f13-3a94695cb940)
