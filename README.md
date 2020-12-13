# Tutoring App
This is a discord bot developed in Python and Discord.py Rewrite that provides the main functions you would expect from a tutoring session, such as joining, viewing, and modifying the waitlist, pulling up tutoring session's hours and sign-in sheet, etc.

# Prerequisites
- Python 3.5.3 or higher [download](https://www.python.org/downloads)
- Pip [install](https://pip.pypa.io/en/stable/installing)

# Requirements 
- discord [documentation](https://discordpy.readthedocs.io) ```pip install -U discord.py```
- python-dotenv [documentation](https://pypi.org/project/python-dotenv) ```pip install -U python-dotenv```
- requests [documentation](https://requests.readthedocs.io/en/master) ```pip install requests```
- cryptography [documentation](https://cryptography.io/en/latest/index.html) ```pip install cryptography```
- gspread [documentation](https://gspread.readthedocs.io/en/latest) ```pip install gspread```

# Tutoring Features
- Features that are used by the Tutees during a tutoring session.

COMMAND | VARIABLE | DESCRIPTION
| :---: | :---: | :---:
.tutee hi | ----- | generate the student's pre-filled tutoring sign-in sheet link. 
.tutee set | [full name][student id][course code][program degree] | store the student's information.
.tutee hours | [course] | display the [course] tutoring location, hours, and tutor.
.tutee join | ----- | add the student to the queue. 
.tutee leave | ----- | remove the student from the queue. 
.tutee que | ----- | display every student and their position in the queue.
.tutee room | [*students] | generate a private room and give access to all [students] mentioned.

- Features that are used by the Tutors during a tutoring session.

COMMAND | VARIABLE | DESCRIPTION
| :---: | :---: | :---:
.tutor start | [course] | ping students with [course] tag that tutoring started.
.tutor end | ----- | end tutor's tutoring session.
.tutor que | ----- | display every student and their position in the tutor's queue.
.tutor next | ----- | move the next student that is ready to the tutor's discord voice channel.
.tutor stop | ----- | stop asking if the next student is ready to be tutored.
.tutor move | [position 1][position 2] | move student in [position 1] to [position 2] in the queue. 
.tutor swap | [position 1][position 2] | swap the student in [position 1] with the student in [position 2] in the queue. 
.tutor kick | [position 1] | remove the student in [position 1] from the queue. 
.tutor clear | ----- | remove all students from the tutor's queue. 

# General Features
- Features that can be used by other discord bots. 
- ESV API [documentation](https://api.esv.org/docs)
- Weather API [documentation](https://openweathermap.org/current)

COMMAND | VARIABLE | DESCRIPTION
| :---: | :---: | :---:
.oops | ----- | remove the last bot command made by the user.
.cal | [expression] | display the calculated results of [expression].
.esv | [passage] | display the Bible [passage] in English Standard Version.
.weather | [city] | display the current weather for [city].
.help | [category] | display the [category] help message.

# CBU Features
- Features that are specific to California Baptist University. 

COMMAND | VARIABLE | DESCRIPTION
| :---: | :---: | :---:
.chapel | [week number] | display the chapel details for [week number].
.java | [class] | display the most commonly used EGR222 java methods for given [class].
