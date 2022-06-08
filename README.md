make sure you create a folder and add all of the project files in the zip to it. open the folder in VS code. Then open up a terminal and do the following.

NOTE: There are TWO different requirement text files. make sure you type the correct one 

You dont need to login to your linux account. no password.txt required. just run it.

if your on windows do the following:
1. in your console type "py -m venv env".dont include the quotes You should see a new folder called env.
2. now activate the environment by typing "env\Scripts\activate" .You should see a (env) appear in the terminal
3. install dependencies by typing "pip install -r requirements1.txt"
3. type "set FLASK_APP=app.py"
4. type "flask run" (make sure you are in the activated environment! meaning you should see the 
(env) at the begining of the terminal)

if your on mac do the following:
1. in your console type "python3 -m venv env".dont include the quotes You should see a new folder called env.
2. now activate the environment by typing "source env/bin/activate" .You should see a (env) appear in the terminal
You might need to type "." at the begining instead of "source"
3. install dependencies by typing "pip install -r requirements2.txt"
4. type "pip install psycopg2-binary"
5. type "export FLASK_APP=app.py"
6. type "flask run" (make sure you are in the activated environment! meaning you should see the 
(env) at the begining of the terminal)

NOTE: if you exit vs code and return, you will have to reactivate the (env) by openening a new terminal window
You can stop the execution by clicking on the terminal and pressing both ctrl + c


LINK TO VIDEO IN CASE YOU CANNOT RUN THE WEB APP: 
https://drive.google.com/file/d/1bYe2AYYduLE9EfojU2DgTygUV1DwBozV/view?usp=sharing
remember to switch to 720p for optimal quality. if the quality is bad and says 720p try changing it to 720p again.

The ER model is included in the zip and is on the website itself.
You can view any SQL used in the output sql files generated from the program.


schema wasnt working so here's our alternative.


using postgres on heroku.