# Task manager program

from datetime import date
from datetime import datetime
import sys
import dropbox
from dropbox.exceptions import ApiError
import os
import re

TOKEN = '1eCYAbSDba0AAAAAAAAAAUJriW30xKNVwc-bSSZhpG947EXFarxVqzWGq7AC41hK'
dbx = dropbox.Dropbox(TOKEN)
DB_DIR = "/task_logs"
LOCAL_FILE = 'report_log.txt'
DB_FILE = f'{DB_DIR}/{datetime.date(datetime.now())}_task_report.txt'


# Definition of all functions

def db_upload(dbx, file_to_upload, local_file):
        # We use WriteMode=overwrite to make sure that the settings in the file
        # are changed on upload
        

        with open(local_file, "rb") as f:
            print("\nUploading " + local_file + " to Dropbox as " + file_to_upload + "...")

            try:
                dbx.files_upload(f.read(), file_to_upload, mute = True)
                print("File uploaded")

            except ApiError as err:
                # This checks for the specific error where a user doesn't have
                # enough Dropbox space quota to upload this file
                if (err.error.is_path() and
                        err.error.get_path().reason.is_insufficient_space()):
                    sys.exit("ERROR: Cannot back up; insufficient space.")
                elif err.user_message_text:
                    print(err.user_message_text)
                    sys.exit()
                else:
                    print(err)
                    sys.exit()

def dropbox_dir_exists(path, dbx):
    # check if logs folder exists in dropbox

    try:
        return dbx.files_get_metadata(path) is not None
    
    except dropbox.exceptions.ApiError as err:
        error_e = err.error

        if isinstance(error_e, dropbox.files.GetMetadataError) and error_e.is_path():
            base_error = error_e.get_path()

            if isinstance(base_error, dropbox.files.LookupError) and base_error.is_not_found():
                return False
            else:
                print("***Api Error:", base_error)
        
        else:
            raise error_e


def create_folder_on_dropbox(folder, dbx):
    # create a directory at the path. check that it is not a file
    if re.search(r"\.[^.]*$", folder) is not None:
        raise ValueError("\n\nPath needs to be a directory not a file.")

    _ = dbx.files_create_folder(folder)
    print(f"\nCreated folder at path: \"{folder}\"")


def download_logs(dbx, file_name, dest_name):

    with open(dest_name, "wb") as f:
        metadata, res = dbx.files_download(file_name)
        f.write(res.content)



def list_folder(dbx, path):
    """List a folder.
    Return a dict mapping unicode filenames to
    FileMetadata|FolderMetadata entries.
    """
    log_list = {}

    for entry in dbx.files_list_folder(path, recursive=True).entries:

        if isinstance(entry, dropbox.files.FileMetadata):
            log_list[entry.name] = entry.path_lower

    return log_list

def open_file_read(filename):
    with open(filename, 'r+') as file:
        data = file.read()

def login_user():
    global login
    login = False
    global current_user
    current_user = ""   # current user variable used to determine menu permissions

    with open('user.txt', 'r+') as user_file:

        global user_name
        user_name = input("\n\tEnter your user name: ")
        global password
        password = input("\n\tEnter user password: ")
        user_name = user_name.strip()
        password = password.strip()

        for line in user_file.readlines():
            line = line.strip()
            global login_credentials
            login_credentials = line.split(", ")

            # Check if user and password is valid
            if user_name == login_credentials[0] and password == login_credentials[1]: 
                print("\n\t\t\t\tLogin Successful")
                current_user = user_name
                return login == True
            
        
        if login == False:  # Display error message if login unsuccessful
            print("\n\t\t\t\tIncorrect Credentials")
                
        user_file.seek(0)
    

def add_user():
     with open('user.txt', 'r+') as user_file:

        verify = False
        user_check = 0

        while user_check == 0:
            
            new_user = input("\nEnter the new user name: ")
            
            # create user list and password list from file to check that no duplicates are accepted.
            for line in user_file.readlines():
                line = line.strip()
                login_credentials = line.split(", ")

                existing_users = login_credentials[0]
                passwords = login_credentials[1]

            if new_user in existing_users:
                print("\nUser already exist. \nTry a different user name")

            else:
                print("\nUser name accepted.")
                user_check += 1


        while verify == False:

            new_pass = input("Enter a password: ")
            
            # Verify password   
            verify_pass = input("Please verify password: ")
            
            if verify_pass == new_pass:
                verify = True
                
                # add new user to file
                user_file.write(f"\n{new_user}, {new_pass}")
                print("\nNew user added")
                
            if verify_pass != new_pass:
                verify = False
                print("\nPassword did not match.")
                verify = True

        return_main()
            
    
def add_task():
    with open('tasks.txt', 'a+') as task_file:
    
        for line in task_file:
                user_task = input("\nPlease enter the name of the user to which the task will be assigned: ")
                task_title = input("Please enter the title of the task: ")
                task_descrep = input("Please enter a short task description: ")
                issue_date = date.today()
                due_date = input("Please enter the due date for this task (e.g. 2020-12-15): ")
                completed = "No"

                task_file.write(f"\n{user_task}, {task_title}, {task_descrep}, {issue_date}, {due_date}, {completed}")

                print("\nNew task added.")

        return_main()

            
def view_all():
    with open("tasks.txt", "r") as task_file:
        task_file.seek(0)
                        
        ("\n\t\t\t\tTask Manager")

        for line in task_file:
            user_task, task_title, task_descrep, issue_date, due_date, completed = line.split(", ")
                        
            print(f"""
            User Name:  {user_task}
            Task Title: {task_title}
            Task Description:  {task_descrep}
            Issue Date: {issue_date}
            Due Date: {due_date}
            Completed: {completed}
            """)

        return_main()

def view_mine():
    with open('tasks.txt', 'r+') as task_file:
        global task_data
        task_data = {}
        task_key = 0
        valid_users = []
        # current_user = user_name
        task_select = 0

        
        for line in task_file:
            line = line.strip()
            user_task, task_title, task_descrip, issue_date, due_date, completed = line.split(", ")

            task_key += 1

            task_data[task_key] = line.split(", ")

        for key, task in task_data.items():

            valid_users.append(task[0])


            if current_user in task:

                print('\n', 'Task Number:', key)
                print('\nuser:', '\t\t', task[0], '\ntask title:', '\t', task[1], '\ndescription:', '\t', task[2], '\nissue date:', '\t', task[3], '\ndue date:', '\t', task[4], '\ncompleted:', '\t', task[5])


                task_select = int(input("\nEnter task number to edit OR enter '-1' to return to the main menu: "))

                if task_select == "-1":
                    menu()

            if current_user not in valid_users:
                print("\nYou currently have no assigned tasks.")
                menu()


            for key, task in task_data.items():
                
                if task_select == key:

                    print(" Task Number:", str(task_select))
                            
                    print("\nOptions:", "\n\t1  -  mark task as complete", "\n\t2  -  edit task")

                    task_option = input("\n\tEnter option number: ")
                                                        
                    if task_option == "1":
                        
                        for key, task in task_data.items():

                            if task_select == key:

                                task[5] = "Yes"
                                
                                update_task_status()


                    if task_option == "2" and task[5] == "No":

                        print("\nEdit Options:", "\n\t1  -  change assigned user", "\n\t2  -  change due date")

                        edit_option = input("\n\tEnter option number: ")
                        
                        if edit_option == "1":

                            print("\nUser Change")

                            user_change = input("\nPlease enter user name to which this task will be assigned: ")

                            for key, task in task_data.items():

                                if task_select == key:

                                    task[0] = user_change

                                    update_task_status()


                        if edit_option == "2":

                            print("\nDue date change")

                            new_due_date = input("\nPlease enter new due date (e.g. 2021-01-05): ")

                            for key, task in task_data.items():

                                if task_select == key:

                                    task[4] = new_due_date

                                    update_task_status()



def update_task_status():
    with open('tasks.txt', 'w') as update_task_file:
            
            for key, task in task_data.items():

                update_task_file.write(task[0] + ", " + task[1] + ", " + task[2] + ", " + task[3] + ", " + task[4] + ", " + task[5] + "\n")

    print("Task Updated")
        

def write_user_task_overview():

    with open('tasks.txt', 'r+') as task_file, open('user.txt', 'r+') as user_file:
    # task overview

        task_key = 0
        task_data = {}
        assigned_users = {}
        valid_users = []
        date_today = date.today()
        total_tasks = 0
        completed_tasks = 0
        incompleted_tasks = 0
        overdue_tasks = 0
        total_users = 0
        perc_per_user = {}
        os_per_user = {}
        perc_os_per_user = {}
        perc_tbc_per_user = {}
        tbc_per_user = {}
    

    
##    current_user = user_name
        task_select = 0

            
        for line in task_file:
            line = line.strip()
            user_task, task_title, task_descrip, issue_date, due_date, completed = line.split(", ")

            task_data[task_key] = line.split(", ")

            task_key += 1
            
            total_tasks += 1


        for key, task in task_data.items():
            if task[5] == "Yes":
                completed_tasks += 1

            elif task[5] == "No":
                incompleted_tasks += 1

            if datetime.strptime(task[4], "%Y-%m-%d").date() < date_today:

                overdue_tasks += 1


        perc_incompleted = round(((incompleted_tasks / total_tasks) * 100), 2)
        perc_overdue = round(((overdue_tasks / total_tasks) * 100), 2)
            

        for line in user_file:
            line = line.strip()
            user, password = line.split(", ")
            
            total_users += 1

            valid_users.append(user)

        # total_tasks_per_user
        for key, task in task_data.items():
            if task[0] in assigned_users:
                assigned_users[task[0]] = int(assigned_users[task[0]]) + 1

            else:
                assigned_users[task[0]] = 1


        for key, value in assigned_users.items():
            
            perc_per_user[key] = round((int(assigned_users[key]) / total_tasks) * 100, 2)

        for key, task in task_data.items():
            if datetime.strptime(task[4], "%Y-%m-%d").date() < date_today and task[5] == "No" and task[0] in assigned_users:

                if task[0] in os_per_user:
                
                    os_per_user[task[0]] = int(os_per_user[task[0]]) + 1  

                else:
                    os_per_user[task[0]] = 1


                perc_os_per_user[task[0]] = round(((int(os_per_user[task[0]]) / int(assigned_users[task[0]])) * 100))

            if task[0] not in os_per_user:

                os_per_user[task[0]] = 0
                
            
        for key, task in task_data.items():
            if task[5] == "No" and task[0] in assigned_users:

                if task[0] in tbc_per_user:

                    tbc_per_user[task[0]] = int(tbc_per_user[task[0]]) + 1

                else:
                    tbc_per_user[task[0]] = 1
                    

                perc_tbc_per_user[task[0]] = round(((int(tbc_per_user[task[0]]) / int(assigned_users[task[0]])) * 100))

    with open('user_overview.txt', 'w') as user_overview, open('task_overview.txt', 'w') as task_overview, open('task_report.txt', 'w') as report_log:

        for k, v in assigned_users.items():
            user_overview.write("\nTasks per user: " + k + ": " + str(v))
            report_log.write("\nTasks per user: " + k + ": " + str(v))

        for k, v in os_per_user.items():
            user_overview.write("\nOverdue per user: " + k + ": " + str(v))
            report_log.write("\nOverdue per user: " + k + ": " + str(v))

        for k, v in perc_os_per_user.items():
            user_overview.write("\nPercentage(%) overdue per user: " + k + ": " + str(v))
            report_log.write("\nPercentage(%) overdue per user: " + k + ": " + str(v))

        for k,v in tbc_per_user.items():
            user_overview.write("\nTo be completed per user: " + k + ": " + str(v))
            report_log.write("\nTo be completed per user: " + k + ": " + str(v))

        for k, v in perc_tbc_per_user.items():
            user_overview.write("\nPercentage(%) to be completed per user: " + k + ": " + str(v))
            report_log.write("\nPercentage(%) to be completed per user: " + k + ": " + str(v))

        
        task_overview.write("Total tasks: " + str(total_tasks) + "\nTotal completed tasks: " + str(completed_tasks) +
                            "\nTotal tasks overdue: " + str(overdue_tasks) + "\nPercentage(%) tasks incomplete: " +
                            str(perc_incompleted) + "\nPercentage(%) tasks overdue: " + str(perc_overdue))

        report_log.write("Total tasks: " + str(total_tasks) + "\nTotal completed tasks: " + str(completed_tasks) +
                            "\nTotal tasks overdue: " + str(overdue_tasks) + "\nPercentage(%) tasks incomplete: " +
                            str(perc_incompleted) + "\nPercentage(%) tasks overdue: " + str(perc_overdue))

def menu():
              
    admin_menu = """\nMAIN MENU:
                r       -   register user
                a       -   add task
                va      -   view all tasks
                vm      -   view my tasks
                dr      -   display reports
                ds      -   display statistics
                lr      -   log report to dropbox
                rh      -   view log history
                e       -   exit"""

    user_menu = """\nMAIN MENU:
                a       -   add task
                va      -   view all tasks
                vm      -   view my tasks
                dr      -   display reports
                lr      -   Log Report(Dropbox)
                e       -   exit"""

    
    if current_user == "admin":
        print(admin_menu)
        global select
        select = input("\nSelect an option from the menu by entering the key here: \n")

    else:
        print(user_menu)
        select = input("\nSelect an option from the menu by entering the key here: \n")
              

def display_statistics():
    with open('user_overview.txt', 'r+') as user_overview, open('task_overview.txt', 'r+') as task_overview:

        print("\n\nUser Overview\n")
        for line in user_overview:
            print(line)


        print("\n\nTask Overview\n")
        for line in task_overview:
            print(line)

    return_main()

def log_report():

    write_user_task_overview()
    
    print("\nChecking Dropbox to see if destination folder exists...")
    
    if not dropbox_dir_exists(DB_DIR, dbx):

        print("\nDirectory does not exist...\nCreating new directory...\n")
        create_folder_on_dropbox(DB_DIR, dbx)

    
    db_upload(dbx, DB_FILE, 'report_log.txt')

    return_main()

def show_log_list():

    log_list = list_folder(dbx, DB_DIR)

    print("\nCurrent Logs")
    for key, value in log_list.items():
        print(f"""\n
            {key}       -   {value}
        """)

    print("""\n
        dl  - Download log
        -1  - Return to main menu
    """)

    opt = input("\nEnter option: ")

    if opt == "dl":
        log_entry = input("\nPlease enter log name from list above:\n")

        if log_entry in log_list:
            print("\nDownloading...\n")
            log_path = log_list[log_entry]

            download_logs(dbx, log_path, log_entry)

            after_download(log_entry)


def display_reports():
    with open('tasks.txt', 'r+') as task_file, open('user.txt', 'r+') as user_file:
    # task overview

        task_key = 0
        task_data = {}
        assigned_users = {}
        valid_users = []
        date_today = date.today()
        total_tasks = 0
        completed_tasks = 0
        incompleted_tasks = 0
        overdue_tasks = 0
        total_users = 0
        perc_per_user = {}
        os_per_user = {}
        perc_os_per_user = {}
        perc_tbc_per_user = {}
        tbc_per_user = {}
    

    
##    current_user = user_name
        task_select = 0

            
        for line in task_file:
            line = line.strip()
            user_task, task_title, task_descrip, issue_date, due_date, completed = line.split(", ")

            task_data[task_key] = line.split(", ")

            task_key += 1
            
            total_tasks += 1


        for key, task in task_data.items():
            if task[5] == "Yes":
                completed_tasks += 1

            elif task[5] == "No":
                incompleted_tasks += 1

            if datetime.strptime(task[4], "%Y-%m-%d").date() < date_today:

                overdue_tasks += 1


        perc_incompleted = round(((incompleted_tasks / total_tasks) * 100), 2)
        perc_overdue = round(((overdue_tasks / total_tasks) * 100), 2)
            

        for line in user_file:
            line = line.strip()
            user, password = line.split(", ")
            
            total_users += 1

            valid_users.append(user)

        # total_tasks_per_user
        for key, task in task_data.items():
            if task[0] in assigned_users:
                assigned_users[task[0]] = int(assigned_users[task[0]]) + 1

            else:
                assigned_users[task[0]] = 1


        for key, value in assigned_users.items():
            
            perc_per_user[key] = round((int(assigned_users[key]) / total_tasks) * 100, 2)

        for key, task in task_data.items():
            if datetime.strptime(task[4], "%Y-%m-%d").date() < date_today and task[5] == "No" and task[0] in assigned_users:

                if task[0] in os_per_user:
                
                    os_per_user[task[0]] = int(os_per_user[task[0]]) + 1  

                else:
                    os_per_user[task[0]] = 1


                perc_os_per_user[task[0]] = round(((int(os_per_user[task[0]]) / int(assigned_users[task[0]])) * 100))

            if task[0] not in os_per_user:

                os_per_user[task[0]] = 0
                
            
        for key, task in task_data.items():
            if task[5] == "No" and task[0] in assigned_users:

                if task[0] in tbc_per_user:

                    tbc_per_user[task[0]] = int(tbc_per_user[task[0]]) + 1

                else:
                    tbc_per_user[task[0]] = 1
                    

                perc_tbc_per_user[task[0]] = round(((int(tbc_per_user[task[0]]) / int(assigned_users[task[0]])) * 100))
                
        
        with open('user_overview.txt', 'r+') as user_overview, open('task_overview.txt', 'r+') as task_overview:

            print("\n\nUser Overview\n")
            for line in user_overview:
                print(line)


            print("\n\nTask Overview\n")
            for line in task_overview:
                print(line)


            return_main()
        

def after_download(local_file):
    view_results = input("\nView log file data now? (y/n): \n")

    if view_results == "y":
        with open(local_file, "r") as dl_file:
            for line in dl_file:

                print(line)

    elif view_results == "n":
        print("\nFile saved to Local storage.")

    return_main()

# auxilary function to print iterations progress (from https://stackoverflow.com/questions/3173320/text-progress-bar-in-the-console)
def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█'):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix), end = '\r')
    # Print New Line on Complete
    if iteration == total: 
        print("\n**Downloads complete")

        return_main()

def return_main():
    
    return_main = input("\nEnter '-1' to return to main menu: ")
    if return_main == "-1":
        menu()
      
    

def main():
    print("\t\t\t\tWelcome to Task Manager")

    login_user()

    while user_name == login_credentials[0] and password == login_credentials[1]:
    
        menu()
               
        if select == "r":
            print("\n\t\t\t\tUser Registration")

            add_user()


        if select == "a":
            print("\n\t\t\t\tTask Manager")

            add_task()
            

        elif select == "va":            
            print("\n\t\t\t\tTask Manager")

            view_all()


        elif select == "vm":
            print("\n\t\t\t\tTask Manager")

            view_mine()
            
                            
        elif select == "ds":
            print("\n\t\t\t\tStatistics")

            display_statistics()

                 
        elif select == "dr":

            display_reports()

        elif select == "lr":
            log_report()

        elif select == "rh":
            show_log_list()

        elif select == "e":
            login = False
            main()



if __name__ == '__main__':
    main()


                    
                    
                    
                    
                    
    
    
    



    

















    

            
            


        
            

        
    
