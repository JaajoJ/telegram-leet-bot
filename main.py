import telebot
from datetime import datetime, timedelta
import sqlite3
import os
import time
import matplotlib.pyplot as plt
import numpy as np
from io import BytesIO
import configparser
import sys
import os.path
helpString = """Leet bot:
-- Commands:

    /help               Prints this message.
    /ranking            Graphs the current ranking.
    /1337               If the time is 1337, you earn points based on your individual multiplication. Extra points for certain dates.
    /wtf                Prints the last 5 entries.

-- Rules:
1) Time: First place gets 2 points. Others get 1 point.
2) Combo: Consecutive participation days result in an individual multiplication of daily points * consecutive days. Note: Multiplication caps at 5.
3) Bonus days: Your points are multiplied by 5. Multiplications stack if you participate on these days:

"""

class leetSession:
    def __init__(self):
        config=configparser.ConfigParser()
        while  config.read('data/config.conf') == []:
            self.generate_config()
        
        self.botToken=str(config['BASICS']['botToken'])
        self.dbFile=str(config['BASICS']['dbFile'])
        self.dbFileTest=str(config['BASICS']['dbFileTest'])
        self.bonusDays_multiplication=int(config['BASICS']['bonusDays_multiplication'])

        self.bonusDays={}
        for variable in config['BONUSDAYS']:
            string = config['BONUSDAYS'][variable]
            string = string.split(":")
            #print("Bonus day", string[0])
            self.bonusDays[string[0]] = str(string[1])

        self.allowedChats=[]
        if 'ALLOWEDCHATS' in config:
            for variable in config['ALLOWEDCHATS']:
                self.allowedChats.append(int(config['ALLOWEDCHATS'][variable]))
            
    def generate_config(self):
        config_directory = os.path.dirname("data/config.conf")

        # Check if the directory exists, if not, create it
        if config_directory != '':
            if not os.path.exists(config_directory):
                os.makedirs(config_directory)

        with open("data/config.conf", "w") as f:
            f.write("[BASICS]\n")

            botToken=input("Give botToken given by telegram:")
            f.write("botToken = "+botToken+"\n")

            dbFile=input("Give the name for a database: ")
            f.write("dbFile = "+dbFile+"\n")

            dbFileTest=input("Give the name for a test database: ")
            f.write("dbFileTest = "+dbFileTest+"\n")

            bonusDays_multiplication=input("How many bonus points for special days:")
            f.write("bonusDays_multiplication = "+bonusDays_multiplication+"\n")

            f.write("[BONUSDAYS]\n")
            print("Write the bonusdays in format:")
            print("01-01:New Years")
            value=1
            print()
            
            while True:
                input_tmp=input(f"bonusday{value} (write exit to exit):")
                if input_tmp == "exit":
                    break
                f.write(f"bonusDay{value} = {input_tmp}"+"\n")
                value+=1
            
            f.write("[ALLOWEDCHATS]"+"\n")
            print()
            print("Write the chat id's which are allowed to use this bot.")
            print("The chat id can be accquired using link: https://api.telegram.org/bot<YourBOTToken>/getUpdates")
            print("and looking at the chat object. Example value: -912330515")
            value=1
            print()
            while True:
                input_tmp=input(f"allowedChatId1{value} (write exit to exit):")
                if input_tmp == "exit":
                    break
                f.write(f"allowedChatId{value} = {input_tmp}"+"\n")
                value+=1

                
            
    
    def get_botToken(self):
        return self.botToken
    
    def get_dbFile(self):
        return self.dbFile

    def get_dbFileTest(self):
        return self.dbFileTest
    
    def get_bonusDays_multiplication(self):
        return int(self.bonusDays_multiplication)
    
    def get_bonusDays(self):
        return self.bonusDays
    
    def get_allowedChats(self):
        return self.allowedChats
    
    def get_helpString(self):
        string = helpString
        dictionary=self.get_bonusDays()
        for key in dictionary:
            string+=f" - {key} ({dictionary[key]})\n"

        return string
    
    def print_session(self):
        print("botToken:\n", self.get_botToken())
        print("dbFile:\n", self.get_dbFile())
        print("dbFileTest:\n", self.get_dbFileTest())
        print("bonusDays_multiplication:\n", self.get_bonusDays_multiplication())
        print("bonusDays:\n", self.get_bonusDays())
        print("allowedChats\n", self.get_allowedChats())


sessionVariables=leetSession()

sessionVariables.print_session()

bot = telebot.TeleBot(sessionVariables.get_botToken())





def create_database(db):
    # Connect to the SQLite database (or create it if it doesn't exist)
    db_directory = os.path.dirname(db)

    # Check if the directory exists, if not, create it
    if db_directory != '':
        if not os.path.exists(db_directory):
            os.makedirs(db_directory)

    connection = sqlite3.connect(db)
    cursor = connection.cursor()

    # Create the 'entries' table with columns timestamp (Primary Key) and name

    # timestamp in format "%Y-%m-%d %H:%M:%S.%f", arbitrary name and value of daily points. 
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS entries (
            timestamp TEXT,
            name TEXT,
            value INTEGER,
            PRIMARY KEY(timestamp, name)
        )
    ''')

    # Commit the changes and close the connection
    connection.commit()
    connection.close()


def destroy_database(db):
    if os.path.exists(db):
    # Remove the database file
        os.remove(db)
        print(f"The database file '{db}' has been removed.")
    else:
        print(f"The database file '{db}' does not exist.")

def get_stats_string(db, before_day='now'):

    if before_day == 'now':
        before_day = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    query = '''
        SELECT name, SUM(value) as total_value
        FROM entries
        WHERE timestamp <= ?
        GROUP BY name
        ORDER BY total_value DESC;
    '''
    connection = sqlite3.connect(db)
    cursor = connection.cursor()
    cursor.execute(query, (before_day,))
    result = cursor.fetchall()
    connection.close()

    #print(result)
    return result

def plot_arrays(names, values, plot=False):
    fig, ax = plt.subplots()

    for i, name in enumerate(names):
        ax.plot(np.arange(len(values[i])), values[i], label=name)

    ax.set_xlabel('Päivät')
    ax.set_ylabel('Pisteet')
    ax.set_title('Viimeiset 100 päivää')
    ax.legend()
    if plot:
        plt.show()
    else:
        buffer = BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        return buffer
    #plt.show()
def plot_100_days_entries(db, test_mode=False):
    
    this_day = datetime.now()
    
    daily_arrays = []

    for i in range(0, 100):
        tmp_day = this_day - timedelta(98-i)
        tmp_timestamp = tmp_day.strftime("%Y-%m-%d")
        #print(get_stats_string(tmp_timestamp), tmp_timestamp)
        daily_arrays.append(get_stats_string(db, tmp_timestamp))

    #print(daily_arrays)

    names = []
    data_points=[]
    for i in daily_arrays[-1]:
        names.append(i[0])
        data_points.append([])

    for day_vals in daily_arrays:
        tmp = []
        for i in names:
            tmp.append(0)

        for name_vals in day_vals:
            count=0
            for name in names:
                if name_vals[0] == name:
                    tmp[count]=name_vals[1]
                    break
                count+=1

        count=0
        for i in tmp:
            data_points[count].append(i)
            count+=1
    #print(names)
    #print(data_points)
    if test_mode==True:
        plot_arrays(names, data_points, plot=True)
    else:
        return plot_arrays(names, data_points)
        
            


def insert_entry(name, db, overwriteTimestamp=None):
    #print("123")
    # Connect to the SQLite database
    print(db)
    connection = sqlite3.connect(db)
    cursor = connection.cursor()

    # Get the current timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
    if overwriteTimestamp:
         timestamp=overwriteTimestamp


    # check if user has participated according to timestamp.
    query = '''
        SELECT * FROM entries
        WHERE name = ? AND timestamp LIKE ?;
    '''

    cursor.execute(query, (name, timestamp[0:10] + '%'))

    if len(cursor.fetchall()) > 0:
        #print("Already participated")
        connection.close()
        return -1
    
    # check past 5 days if user has participated
    personal_multiplication=1
    timestamp_datetime = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S.%f")
    for i in range (1,5):
        timestamp_datetime = timestamp_datetime - timedelta(1) 
        tmp_timestamp = timestamp_datetime.strftime("%Y-%m-%d %H:%M:%S.%f")
        cursor.execute(query, (name, tmp_timestamp[0:16] + '%',))
        
        if len(cursor.fetchall()) > 0:
            hour = int(tmp_timestamp[11:13])
            minute = int(tmp_timestamp[14:16])
            if hour != 13 or minute != 37:
                break
            personal_multiplication+=1
            
        else:
             break
    #print("5 day bonus", personal_multiplication)
   
    # Check if user is first today and clock is 13:37
    query = '''
        SELECT * FROM entries
        WHERE timestamp LIKE ?;
    '''
    
    hour = int(timestamp[11:13])
    minute = int(timestamp[14:16])

    if hour != 13 or minute != 37:
        value=-1
    else:
        cursor.execute(query, (timestamp[0:11]+"13:37" + '%',))
        value = 1
        if len(cursor.fetchall()) == 0:
            value = 2

    # check if day is one in the array
    
    for key in sessionVariables.get_bonusDays().keys():
        if timestamp[5:10] == key:
            #print("Extra points")
            personal_multiplication=personal_multiplication*sessionVariables.get_bonusDays_multiplication()
            #print(personal_multiplication,sessionVariables.get_bonusDays_multiplication())
    
    if value == -1:
         personal_multiplication=1

    # Insert a new entry into the 'entries' table
    cursor.execute('''
        INSERT INTO entries (timestamp, name, value)
        VALUES (?, ?, ?)
    ''', (timestamp, name, value*personal_multiplication))

    # Commit the changes and close the connection
    connection.commit()
    connection.close()
    return 1



def print_database(db, count=None):
    # Connect to the SQLite database
    connection = sqlite3.connect(db)
    cursor = connection.cursor()

    # Retrieve all entries from the 'entries' table
    if count == None:
        cursor.execute('SELECT * FROM entries')
    else:
        cursor.execute('SELECT * FROM entries ORDER BY timestamp DESC LIMIT '+str(count) +';')
        entries = cursor.fetchall()
        connection.close()
        ret=""
        for i in entries:
            ret+=str(i).replace("(", "").replace(")","").replace("'","")+'\n'
        return ret
    entries = cursor.fetchall()

    if not entries:
        print("The database is empty.")
    else:
        print("Database entries:")
        for entry in entries:
            print(entry)

    # Close the connection
    connection.close()


def test_db():
    
    print(sessionVariables.get_helpString())
    dbFileTest=sessionVariables.get_dbFileTest()
    create_database(dbFileTest)
    insert_entry("Joni", dbFileTest)
    insert_entry("Pertti",dbFileTest, "2024-01-14 13:37:13.384583")
    insert_entry("Pertti", dbFileTest,"2024-01-14 13:38:13.384583")
    insert_entry("Pertti2", dbFileTest,"2024-01-14 13:37:13.284583")
    insert_entry("Pertti2", dbFileTest,"2024-01-13 13:37:13.284583")
    insert_entry("Pertti2", dbFileTest,"2024-01-12 13:37:13.284583")
    insert_entry("Pertti3", dbFileTest)

    insert_entry("Grindaaja69", dbFileTest, "2024-01-11 13:37:13.384583")
    insert_entry("Grindaaja69", dbFileTest,"2024-01-12 13:37:13.384583")
    insert_entry("Grindaaja69", dbFileTest,"2024-01-12 13:37:13.384583")
    insert_entry("Grindaaja69", dbFileTest,"2024-01-13 13:37:13.384583")
    insert_entry("Grindaaja69s", dbFileTest,"2024-01-13 13:37:23.384583")
    insert_entry("Grindaaja69", dbFileTest,"2024-01-14 13:37:13.384583")
    insert_entry("Grindaaja69", dbFileTest,"2024-01-15 13:37:13.384583")
    insert_entry("Grindaaja69", dbFileTest,"2024-01-16 13:37:13.384583")

    insert_entry("Grindaaja69", dbFileTest,"2024-01-18 13:37:13.384583")

    print("New years!")
    insert_entry("Grindaaja69", dbFileTest,"2024-01-01 13:37:13.384583")
    #insert_entry("JJ", "test_"+dbFile, '2024-01-13 20:41:31.273297')
    insert_entry("JJ", dbFileTest)

    print_database(dbFileTest)

    print("printing last 5 entries")
    print(print_database(dbFileTest, 5))
    print("end")
    time.sleep(2)
    print("here stats")
    print(get_stats_string(dbFileTest))
    s=""
    for i in get_stats_string(dbFileTest):
        s+=str(i)+"\n"
    print(s)

    print("no stats")
    plot_100_days_entries(dbFileTest,test_mode=True)
    destroy_database(dbFileTest)

    create_database(dbFileTest)
    insert_entry("JJ", dbFileTest)
    print(print_database(dbFileTest, 5))
    destroy_database(dbFileTest)

@bot.message_handler(commands=['help'])
def send_welcome(message):
    bot.reply_to(message, sessionVariables.get_helpString())
    print(message.chat.id)
	
@bot.message_handler(commands=['wtf'])
def send_last_5(message):
    if message.chat.id in sessionVariables.get_allowedChats():
        send=print_database(sessionVariables.get_dbFile(), 5)
        if send:
            bot.reply_to(message, send)
        print(message.chat.id)


@bot.message_handler(commands=['ranking'])
def send_ranking(message):
	# Send the image as a reply to the original message
    if message.chat.id in sessionVariables.get_allowedChats():
        buffer=plot_100_days_entries(sessionVariables.get_dbFile())
        bot.send_photo(message.chat.id, photo=('plot.png', buffer), reply_to_message_id=message.message_id)
        s=""
        for i in get_stats_string(sessionVariables.get_dbFile()):
            s+=str(i).replace("(","").replace(")","").replace("'","")+"\n"
        bot.reply_to(message, s)


    

@bot.message_handler(commands=['1337'])
def log_1337(message):
    if message.chat.id in sessionVariables.get_allowedChats():
        user_name = message.from_user.first_name
        val = insert_entry(user_name,sessionVariables.get_dbFile())



if len(sys.argv)>1:
    if "-t" in sys.argv:
        test_db()
        exit
else:
    create_database(sessionVariables.get_dbFile())

    bot.infinity_polling()


