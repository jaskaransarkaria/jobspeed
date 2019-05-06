import sqlite3
import itertools
import kivy
kivy.require("1.10.0")
from kivy.app import App
import collections
import matplotlib.pyplot as plt


def update_dict(d, u):
    for k, v in u.items():
        if isinstance(v, collections.Mapping): #WHAT IS THIS DOING?????
            d[k] = update_dict(d.get(k, {}), v)
        else:
            d[k] = v
    return d

def convert_to_integer(value):
    if value is True:
        value = 1
    else:
        value = 0
    return value

def convert_from_integer(value):
    if value == 1:
        value = True
    else:
        value = False
    return value

class DBMethods:
    def __init__(self, job_number):
        self.job_number =job_number

    def take_dict_update_job_in_db(self, dict):
        '''add new subjob data to existing job in database'''
        conn = sqlite3.connect('enki_sqlite_database.db')
        c = conn.cursor()
        counter = 1
        c.execute("SELECT * FROM SubJobTable WHERE jobnumber=(?)", (self.job_number,))
        length = len(c.fetchall())  # length of original subjobs without the extension
        subjob_num = len(dict) + 1  # length of subjob extension
        subjob = length + 1

        while counter < subjob_num:
            with conn:
                c.execute("""INSERT INTO SubJobTable VALUES((?), (?), (?), (?), (?), (?), (?),
                                    (?), (?))""", (self.job_number, subjob,
                                                   dict[subjob]['Repair/ Commission'], dict[subjob]['Job Description'],
                                                   dict[subjob]['Metal'], dict[subjob]['Stones'],
                                                   dict[subjob]['Estimated Cost'], dict[subjob]['Actual Cost'],
                                                   dict[subjob]['Status']))
            subjob = subjob + 1
            counter = counter + 1
        c.close()
        conn.close()

    def update_table(self, field, new_info, subjob_num=1):
        '''update customer info whether in customer table or in the subjobtable'''
        conn = sqlite3.connect('enki_sqlite_database.db')
        c = conn.cursor()
        customer_field = ['Customer Name', 'Contact Number', 'Email', 'Deposit', 'Total Money Owed', 'Overall Status',
                          'Deadline', 'Date of Order', 'phone_checked', 'email_checked']
        subjob_field = ['Repair/ Commission', 'Job Description', 'Metal', 'Stones',
                        'Estimated Cost', 'Actual Cost', 'Status']
        if field in customer_field:
            if field == 'Customer Name':
                with conn:
                    c.execute("UPDATE CustomerTable SET customername=(?) WHERE jobnumber=(?)",
                              (new_info, self.job_number))
            elif field == 'Date of Order':
                with conn:
                    c.execute("UPDATE CustomerTable SET dateoforder=(?) WHERE jobnumber=(?)",
                              (new_info, self.job_number))
            elif field == 'Contact Number':
                with conn:
                    c.execute("UPDATE CustomerTable SET contactnumber=(?) WHERE jobnumber=(?)",
                              (new_info, self.job_number))
            elif field == 'Email':
                with conn:
                    c.execute("UPDATE CustomerTable SET email=(?) WHERE jobnumber=(?)", (new_info, self.job_number))
            elif field == 'Deposit':
                with conn:
                    c.execute("UPDATE CustomerTable SET deposit=(?) WHERE jobnumber=(?)", (new_info, self.job_number))
            elif field == 'Total Money Owed':
                with conn:
                    c.execute("UPDATE CustomerTable SET totalmoneyowed=(?) WHERE jobnumber=(?)",
                              (new_info, self.job_number))
            elif field == 'Overall Status':
                with conn:
                    c.execute("UPDATE CustomerTable SET overallstatus=(?) WHERE jobnumber=(?)",
                              (new_info, self.job_number))
            elif field == 'Deadline':
                with conn:
                    c.execute("UPDATE CustomerTable SET deadline=(?) WHERE jobnumber=(?)", (new_info, self.job_number))
            elif field == 'phone_checked':
                phone_checked = convert_to_integer(new_info)
                with conn:
                    c.execute("UPDATE CustomerTable SET phonechecked=(?) WHERE jobnumber=(?)", (phone_checked, self.job_number))
            elif field == 'email_checked':
                email_checked = convert_to_integer(new_info)
                with conn:
                    c.execute("UPDATE CustomerTable SET emailchecked=(?) WHERE jobnumber=(?)", (email_checked, self.job_number))
            else:
                pass

        elif field in subjob_field:
            if field == 'Repair/ Commission':
                with conn:
                    c.execute("UPDATE SubJobTable SET repaircommission=(?) WHERE jobnumber=(?) AND subjob=(?)",
                              (new_info, self.job_number, subjob_num))
            elif field == 'Job Description':
                with conn:
                    c.execute("UPDATE SubJobTable SET jobdescription=(?) WHERE jobnumber=(?) AND subjob=(?)",
                              (new_info, self.job_number, subjob_num))
            elif field == 'Metal':
                with conn:
                    c.execute("UPDATE SubJobTable SET metal=(?) WHERE jobnumber=(?) AND subjob=(?)",
                              (new_info, self.job_number, subjob_num))
            elif field == 'Stones':
                with conn:
                    c.execute("UPDATE SubJobTable SET stones=(?) WHERE jobnumber=(?) AND subjob=(?)",
                              (new_info, self.job_number, subjob_num))
            elif field == 'Estimated Cost':
                with conn:
                    c.execute("UPDATE SubJobTable SET estimatedcost=(?) WHERE jobnumber=(?) AND subjob=(?)",
                              (new_info, self.job_number, subjob_num))
            elif field == 'Actual Cost':
                with conn:
                    c.execute("UPDATE SubJobTable SET actualcost=(?) WHERE jobnumber=(?) AND subjob=(?)",
                              (new_info, self.job_number, subjob_num))
            elif field == 'Status':
                with conn:
                    c.execute("UPDATE SubJobTable SET status=(?) WHERE jobnumber=(?) AND subjob=(?)",
                              (new_info, self.job_number, subjob_num))
            else:
                pass
        else:
            print("something got misspelled somewhere...")

    def delete_subjob_row(self, subjob_num):
        '''delete a subjob'''
        conn = sqlite3.connect('enki_sqlite_database.db')
        c = conn.cursor()
        with conn:
            c.execute("DELETE FROM SubJobTable WHERE jobnumber=(?) AND subjob=(?)", (self.job_number, subjob_num))

    def subjob_length(self):
        conn = sqlite3.connect('enki_sqlite_database.db')
        c = conn.cursor()
        c.execute("SELECT * FROM SubJobTable WHERE jobnumber=(?)", (self.job_number,))
        data = c.fetchall()
        data = len(data)
        c.close()
        conn.close()
        return data

    def build_dict_from_subjob(self):
        conn = sqlite3.connect('enki_sqlite_database.db')
        c = conn.cursor()
        c.execute("SELECT * FROM SubJobTable Where jobnumber=(?)", (self.job_number,))
        data = c.fetchall()
        subjob_dict = {}
        counter = 1
        while counter < len(data) + 1:
            subjob_dict[counter] = {}
            c.execute("SELECT repaircommission FROM SubJobTable Where jobnumber=(?) AND subjob=(?)",
                      (self.job_number, counter))
            subjob_dict[counter]['Repair/ Commission'] = c.fetchone()[0]
            c.execute("SELECT jobdescription FROM SubJobTable Where jobnumber=(?) AND subjob=(?)",
                      (self.job_number, counter))
            subjob_dict[counter]['Job Description'] = c.fetchone()[0]
            c.execute("SELECT metal FROM SubJobTable Where jobnumber=(?) AND subjob=(?)", (self.job_number, counter))
            subjob_dict[counter]['Metal'] = c.fetchone()[0]
            c.execute("SELECT stones FROM SubJobTable Where jobnumber=(?) AND subjob=(?)", (self.job_number, counter))
            subjob_dict[counter]['Stones'] = c.fetchone()[0]
            c.execute("SELECT estimatedcost FROM SubJobTable Where jobnumber=(?) AND subjob=(?)",
                      (self.job_number, counter))
            subjob_dict[counter]['Estimated Cost'] = c.fetchone()[0]
            c.execute("SELECT actualcost FROM SubJobTable Where jobnumber=(?) AND subjob=(?)",
                      (self.job_number, counter))
            subjob_dict[counter]['Actual Cost'] = c.fetchone()[0]
            c.execute("SELECT status FROM SubJobTable Where jobnumber=(?) AND subjob=(?)", (self.job_number, counter))
            subjob_dict[counter]['Status'] = c.fetchone()[0]
            counter = counter + 1
        c.close()
        conn.close()
        return subjob_dict

    def subjob_into_list(self):
        ''' takes the job and puts each subjob into a list and puts all this list into one list of lists'''
        conn = sqlite3.connect('enki_sqlite_database.db')
        c = conn.cursor()
        parent_list = []
        counter = 1
        num_subjob = self.subjob_length()
        while counter < num_subjob + 1:
            child_list = []
            c.execute("SELECT repaircommission FROM SubJobTable WHERE jobnumber=(?) AND subjob=(?)",
                      (self.job_number, counter))
            repair_commission = c.fetchone()[0]
            child_list.append(str(repair_commission))
            c.execute("SELECT jobdescription FROM SubJobTable WHERE jobnumber=(?) AND subjob=(?)",
                      (self.job_number, counter))
            job_description = c.fetchone()[0]
            child_list.append(str(job_description))
            c.execute("SELECT metal FROM SubJobTable WHERE jobnumber=(?) AND subjob=(?)", (self.job_number, counter))
            metal = c.fetchone()[0]
            child_list.append(str(metal))
            c.execute("SELECT stones FROM SubJobTable WHERE jobnumber=(?) AND subjob=(?)", (self.job_number, counter))
            stones = c.fetchone()[0]
            child_list.append(str(stones))
            c.execute("SELECT estimatedcost FROM SubJobTable WHERE jobnumber=(?) AND subjob=(?)",
                      (self.job_number, counter))
            estimated_cost = c.fetchone()[0]
            child_list.append(str(estimated_cost))
            c.execute("SELECT actualcost FROM SubJobTable WHERE jobnumber=(?) AND subjob=(?)",
                      (self.job_number, counter))
            actual_cost = c.fetchone()[0]
            child_list.append(str(actual_cost))
            c.execute("SELECT status FROM SubJobTable WHERE jobnumber=(?) AND subjob=(?)", (self.job_number, counter))
            status = c.fetchone()[0]
            child_list.append(str(status))
            parent_list.append(child_list)
            counter = counter + 1
        c.close()
        conn.close()
        return parent_list

    def edit(self):
        '''sends the ui here after double click from the main screen'''
        conn = sqlite3.connect('enki_sqlite_database.db')
        c = conn.cursor()
        app = App.get_running_app()
        c.execute("SELECT jobnumber FROM CustomerTable WHERE jobnumber=(?)", (self.job_number,))
        job_number = c.fetchall()[0]
        c.execute("SELECT customername FROM CustomerTable WHERE jobnumber=(?)", (self.job_number,))
        customer_name = c.fetchall()[0]
        app.customer_name = str(customer_name[0])
        c.execute("SELECT contactnumber FROM CustomerTable WHERE jobnumber=(?)", (self.job_number,))
        contact_number = c.fetchone()[0]
        app.contact_number = str(contact_number)
        c.execute("SELECT email FROM CustomerTable WHERE jobnumber=(?)", (self.job_number,))
        email_add = c.fetchone()[0]
        app.email_add = str(email_add)
        c.execute("SELECT dateoforder FROM CustomerTable WHERE jobnumber=(?)", (self.job_number,))
        date_of_order = c.fetchone()[0]
        app.date_of_order = str(date_of_order)
        c.execute("SELECT deposit FROM CustomerTable WHERE jobnumber=(?)", (self.job_number,))
        customer_deposit = c.fetchone()[0]
        app.customer_deposit = str(customer_deposit)
        c.execute("SELECT totalmoneyowed FROM CustomerTable WHERE jobnumber=(?)", (self.job_number,))
        customer_money_owed = c.fetchone()[0]
        app.customer_money_owed = str(customer_money_owed)
        c.execute("SELECT deadline FROM CustomerTable WHERE jobnumber=(?)", (self.job_number,))
        customer_deadline = c.fetchone()[0]
        app.customer_deadline = str(customer_deadline)
        c.execute("SELECT overallstatus FROM CustomerTable WHERE jobnumber=(?)", (self.job_number,))
        overall_status = c.fetchone()[0]
        app.overall_status = str(overall_status)
        c.execute("SELECT phonechecked FROM CustomerTable WHERE jobnumber=(?)", (self.job_number,))
        phone_checked = c.fetchone()[0]
        app.phone_checked = convert_from_integer(phone_checked)
        c.execute("SELECT emailchecked FROM CustomerTable WHERE jobnumber=(?)", (self.job_number,))
        email_checked = c.fetchone()[0]
        app.email_checked = convert_from_integer(email_checked)

        subjob_len = self.subjob_length()
        app.subjob_num = 1
        subjob_dict = {}
        subjob_dict.clear() #just in case there is another variable pointing to this
        subjob_dict = self.build_dict_from_subjob()
        app.subjob_dict = {}
        update_dict(app.subjob_dict, subjob_dict)

        if subjob_len > 0:
            app.root.load_grid(subjob_len)
        c.close()
        conn.close()
        return job_number, app.customer_name, app.contact_number, app.email_add, app.date_of_order, app.subjob_dict, \
               subjob_len

#
# def create_table_parent():
#     # when not in :memory: CREATE TABLE IF NOT EXISTS
#     c.execute("""CREATE TABLE CustomerTable(jobnumber INTEGER PRIMARY KEY, dateoforder TEXT, customername TEXT,
#             contactnumber TEXT, email TEXT, deposit TEXT, totalmoneyowed TEXT, deadline TEXT, overallstatus TEXT,
#              phonechecked INTEGER,  emailchecked INTEGER)""")
#
# def create_table_child():
#     with conn:
#         c.execute("""CREATE TABLE SubJobTable(jobnumber INTEGER, subjob INTEGER, repaircommission TEXT,
#                     jobdescription TEXT, metal TEXT, stones TEXT, estimatedcost TEXT, actualcost TEXT, status TEXT,
#                     FOREIGN KEY(jobnumber) REFERENCES CustomerTable(jobnumber), PRIMARY KEY (jobnumber, subjob)) """)
    def delete_duplicate_subjobs(self):
        conn = sqlite3.connect('enki_sqlite_database.db')
        c = conn.cursor()
        c.execute("SELECT * FROM SubJobTable")
        subjob_table = c.fetchall()
        duplicates = []

        for i in subjob_table:
            numbers = []
            numbers.extend((i[0], i[1]))
            duplicates.append(numbers)

        just_dupes = [x for x in duplicates if duplicates.count(x) >= 2]
        just_dupes.sort()
        to_be_deleted = [just_dupes for just_dupes, _ in itertools.groupby(just_dupes)]

        for i in to_be_deleted:
            empty = ''
            with conn:
                c.execute(
                    "DELETE FROM SubJobTable WHERE jobnumber=(?) AND subjob=(?) AND repaircommission=(?) AND jobdescription=(?) AND metal=(?) AND stones=(?)",
                    (i[0], i[1], empty, empty, empty, empty))

        c.close()
        conn.close()

    def donut_plot(self):
        ''' create 2 donut charts 1) number of repairs vs commissions (over given time) 2) money accrued
        from repairs (sum actual cost) vs commissions (sum actual cost) (over given time)'''
        # get data
        def search_for_data(required_item):
            matches = []
            total_actual_cost = []
            conn = sqlite3.connect('enki_sqlite_database.db')
            c = conn.cursor()
            c.execute("SELECT jobnumber, repaircommission, actualcost FROM SubJobTable WHERE status='Returned' AND repaircommission=(?)", (required_item,))
            whole_subjob_table = c.fetchall()
            print(whole_subjob_table)
            for row, item in enumerate(whole_subjob_table):
                for i in item:
                    if required_item == i:
                        matches.append(item[0])
                        try:
                            total_actual_cost.append(float(item[2][1:]))
                        except:
                            total_actual_cost.append(0.0)
            return len(matches), sum(total_actual_cost)

        num_repairs, sum_repairs = search_for_data('Repair')
        num_commissions, sum_commissions = search_for_data('Commission')

        # create data
        names = 'Repairs' +'\n£' +str(sum_repairs), 'Commissions'+'\n£' +str(sum_commissions)
        size = [num_repairs, num_commissions]
        #
        # # Create a circle for the center of the plot
        # my_circle = plt.Circle((0, 0), 0.6, color='white')
        # # Custom colors --> colors will cycle
        # # Label distance: gives the space between labels and the center of the pie
        # plt.rcParams['text.color'] = 'red'
        # plt.pie(size, labels=names, colors=['firebrick', 'darkslategray'], labeldistance=1.2,
        #         wedgeprops={'linewidth': 4, 'edgecolor': 'white'}, autopct='%1.1f%%', shadow=False)
        # p = plt.gcf()
        # p.gca().add_artist(my_circle)
        # plt.savefig("foo.png", transparent=True)
        # #plt.show()
        #
        # # create data
        # names = 'Repairs' +'\n£' +str(sum_repairs), 'Commissions'+'\n£' +str(sum_commissions)
        # size = [sum_repairs, sum_commissions]
        #
        # # Create a circle for the center of the plot
        # my_circle = plt.Circle((0, 0), 0.6, color='white')
        #
        # # Custom colors --> colors will cycle
        # # Label distance: gives the space between labels and the center of the pie
        # plt.rcParams['text.color'] = 'red'
        # plt.pie(size, labels=names, colors=['firebrick', 'darkslategray'], labeldistance=1.2,
        #         wedgeprops={'linewidth': 4, 'edgecolor': 'white'}, autopct='%1.1f%%', shadow=False)
        # p = plt.gcf()
        # p.gca().add_artist(my_circle)
        # plt.savefig("bar.png", transparent=True)
        # #plt.show()
        #
        # # need a way of not producing a chart in ALL values == 0
        # produce a true Donut chart

        fig, ax = plt.subplots()
        fig.set_facecolor('#fff9c9')
        wedges, text, autotext = ax.pie([25, 40], colors=['limegreen', 'crimson'], labels=names, autopct='%1.1f%%')
        plt.setp(wedges, width=0.25)
        ax.set_aspect("equal")
        plt.savefig('foobar.png', transparent=True)
        plt.show()