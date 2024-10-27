# CanvasDateSetter
Sets assignment dates for instructors in Canvas.

## Requirements
1. python3
2. selenium
```python
pip install selenium
```
3. Chrome browser

## What's it doing?
1. It pops a chrome browser and resizes it.
2. It enters your email
3. The terminal will prompt for password
4. The script will navigate to the modules page of the desired course.
5. It will associate all the assignments with their proper week/module
6. It will navigate to the Assignments page and start entering the dates

Note 1: The script will pause on an error to prevent run away erronious data entry

Note 2: After all the dates are entered it pauses so you can check the dates and save.

## Usage
Developed in notepad++ and tested in Windows' cmd.exe and Chrome, nothing else has been tested.

### Arguments
-l, --login-page, The login page, ex. https://[school].instructure.com/

-e, --email, Your login email, ex. sketchy.code@school.edu

-c, --course-sn, The course's instance number, ex. 12730, in canvas located on the course tile on the dashboard ex. SEC[123].[course-sn].[block].Online

-b, --course-block, The specific block, either 1 or 2, ex. B1, B2

-d, --days-until, The days from "today" when the class starts, can be positive or negative, ex. 14, -3


### Examples
This will log you in, navigate to the course with a SN of 12345 and running during block 2 and set assignment dates as if starting 5 days from the execution date.
```
python set_dates.py -l https://[school].instructure.com/ -e sketchy.code@school.edu -c 12345 -b B2 -d 5
```
This will log you in,..., and set the dates as if the class started 2 days ago.
```
python3 set_dates.py -l https://[school].instructure.com/ -e sketchy.code@school.edu -c 14253 -b B1 -d -2
```

## Known issues
1. Sometimes the first assignment will get skipped.
2. Sometimes the weekely discussion assignments will all get assigned the same dates for courses with hundreds of assignments.
