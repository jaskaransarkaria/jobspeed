import sys
import os
from datetime import *
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.utils import formataddr
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.colors import red, black
from pathlib import Path
from subprocess import Popen
from twilio.rest import Client

class Enki:
    def __init__(self, job_number):
        self.job_number = job_number

    def generate_pdf(self, customer_name, contact_number, email_add, date_of_order, deposit, total_money_owed,
                     deadline, overall_status, sub_job_list):
        def apply_italics(height, text, indent):
            normal = ParagraphStyle('paragraph', fontName='Helvetica', fontSize=19)
            italic_text = "<i>" + text + "</i>"
            para_text = Paragraph(italic_text, normal)
            para_text.wrapOn(c, 530, 40)
            para_text.drawOn(c, indent, height)

        def customer_info(start_num):
            c.setFont("Helvetica", 20, leading=None)
            c.drawString(40, start_num, "Date of Order: " + date_of_order)
            c.drawString(40, start_num - 25, "Customer Name: " + customer_name)
            c.drawString(40, start_num - 50, "Contact Number: " + contact_number)
            c.drawString(40, start_num - 75, "Email: " + email_add)
            c.drawString(40, start_num - 100, "Deposit: " + deposit)
            c.setFillColor(red)
            c.drawString(40, start_num - 125, "Balance Due: " + total_money_owed)
            c.setFillColor(black)
            c.drawString(40, start_num - 150, "Deadline: " + deadline)
            c.drawString(40, start_num - 175, "Overall Status: " + overall_status)

        def subjob_info(subjob_index, subjob_start_num):
            c.setFont("Helvetica", 20, leading=None)
            if len(sub_job_list[subjob_index][1]) > 42:
                job_desc = sub_job_list[subjob_index][1][:42:].rsplit(' ', 1)
                job_desc2 = job_desc[1] + sub_job_list[subjob_index][1][42::]
                c.drawString(40, subjob_start_num, "Job Description: ")
                apply_italics(subjob_start_num + 8, job_desc[0], 185) # + 8
                apply_italics(subjob_start_num - 13, job_desc2, 40) # - 13
            else:
                c.drawString(40, subjob_start_num, "Job Description: ") # start num
                apply_italics(subjob_start_num + 8, sub_job_list[subjob_index][1], 185) # +8
            c.drawString(40, subjob_start_num - 40, "Metal: " + sub_job_list[subjob_index][2]) # -40
            c.drawString(40, subjob_start_num - 60, "Stones: " + sub_job_list[subjob_index][3]) # - 20
            c.drawString(40, subjob_start_num - 80, "Estimated Cost: " + sub_job_list[subjob_index][4])
            c.drawString(40, subjob_start_num - 100, "Actual Cost: " + sub_job_list[subjob_index][5])
            c.drawString(40, subjob_start_num -120, "Status: " + sub_job_list[subjob_index][6])
            c.rect(35, subjob_start_num - 130, 530, 150, fill=0) # - 10 last

        def header(vertical_start, height):
            logo = 'logo.jpg'
            enki_writing = "enki_writing.jpg"
            c.drawImage(logo, 95, vertical_start, width=50, height=height)  # width and height to re-size image
            c.drawImage(logo, 405, vertical_start, width=50, height=height)
            c.drawImage(enki_writing, 150, vertical_start, width=250, height=height)
            c.setFont("Helvetica", 14, leading=None)
            c.drawCentredString(50, 810, today) # meaning you give it a center point, 0 for y is at the bottom of the page
            c.setFont("Helvetica", 12, leading=None)
            c.drawString(460, 815, 'Job')
            c.drawString(460, 800, 'Number: ' + str(self.job_number))

        sub_jobs = 1
        c = canvas.Canvas(str(self.job_number) + '.pdf')
        today = date.today().strftime("%d/%m/%y") # switches date to uk format and converts to string
        c.setFont("Helvetica", 14, leading=None)
        c.drawCentredString(280, 645, "Unit 1, Kings Court, Kings Heath,")
        c.drawCentredString(280, 630, "Birmingham, B14 7JZ")
        header(675, 120)
        if len(sub_job_list) == 1:
            customer_info(565)
            c.setFont("Helvetica-Bold", 21, leading=None)
            c.drawString(20, 345, "Job")
            subjob_info(0, 315)
            c.showPage()  # renders the previous data completed and then starts a new page
            c.save()
            return

        elif len(sub_job_list) == 2:
            customer_info(590)
            c.setFont("Helvetica-Bold", 21, leading=None)
            c.drawString(20, 385, "Sub-Job " + str(sub_jobs) + ": " + sub_job_list[0][0])
            subjob_info(0, 360)
            sub_jobs += 1
            c.setFont("Helvetica-Bold", 21, leading=None)
            c.drawString(20, 195, "Sub-Job " + str(sub_jobs) + ": " + sub_job_list[1][0])
            subjob_info(1, 160)
            c.showPage()
            c.save()
            return

        elif len(sub_job_list) > 2:
            customer_info(590)
            #first 2 sub-jobs
            c.setFont("Helvetica-Bold", 21, leading=None)
            c.drawString(20, 390, "Sub-Job " + str(sub_jobs) + ": " + sub_job_list[0][0])
            subjob_info(0, 360)
            sub_jobs += 1
            c.setFont("Helvetica-Bold", 21, leading=None)
            c.drawString(20, 200, "Sub-Job " + str(sub_jobs) + ": " + sub_job_list[1][0])
            subjob_info(1, 170)
            c.showPage()
            counter = 2
            num_pages = (len(sub_job_list)-2)/3 #need to add a always round up function/ method
            num_pages_counter = 0
            while sub_jobs <= len(sub_job_list):
                header(685, 140)
                try:
                    sub_jobs += 1
                    c.setFont("Helvetica-Bold", 21, leading=None)
                    c.drawString(20, 660, "Sub-Job " + str(sub_jobs) + ": " + sub_job_list[counter][0])
                except IndexError:
                    c.save()
                    return
                subjob_info(counter, 630)
                counter += 1
                try:
                    sub_jobs += 1
                    c.setFont("Helvetica-Bold", 21, leading=None)
                    c.drawString(20, 470, "Sub-Job " + str(sub_jobs) + ": " + sub_job_list[counter][0])
                except IndexError:
                    c.showPage()
                    c.save()
                    return
                subjob_info(counter, 440)
                counter += 1
                try:
                    sub_jobs += 1
                    c.setFont("Helvetica-Bold", 21, leading=None)
                    c.drawString(20, 280, "Sub-Job " + str(sub_jobs) + ": " + sub_job_list[counter][0])
                except IndexError:
                    c.showPage()
                    c.save()
                    return
                subjob_info(counter, 250)
                counter += 1
                num_pages_counter += 1
                c.showPage()
                if num_pages_counter >= num_pages:
                    c.save()
                    return
            else:
                c.save()
                return

    def email(self, email_add, body, subject):
        job_number = str(self.job_number)
        COMMASPACE = ', '
        gmail_user = GMAIL_USER
        gmail_pass = GMAIL_PASSWORD
        reciepents = [email_add]
        msg = MIMEMultipart()
        msg['From'] = formataddr(('Enki', GMAIL_USER)) 
        msg['To'] = COMMASPACE.join(reciepents)
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        source_path = Path(os.path.realpath(sys.argv[0]))
        job_sheets_path = Path(source_path.parent / "job_sheets")
        file_name = job_number + '.pdf'
        filename = Path(job_sheets_path / file_name)
        attachment = open(str(filename), 'rb')
        part = MIMEApplication(attachment.read())
        part.add_header('Content-Disposition', 'attachment', filename=job_number +".pdf")
        msg.attach(part)
        text = msg.as_string()
        try:
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(gmail_user, gmail_pass)
            server.sendmail(gmail_user, reciepents, text)
            server.quit()
            print("Email Sent!")
        except:
            print("Something went wrong...")

    def delete_pdf(self):
        '''delete old pdf'''
        try:
            file_name = str(self.job_number) + ".pdf"
            source_path = Path(os.path.realpath(sys.argv[0]))
            # requires absolute path /home/jaskaran/PycharmProjects/enki
            dst_path = Path(source_path.parent / "job_sheets" / file_name)
            dst_path.unlink()
            #os.remove("/home/jaskaran/PycharmProjects/enki/job_sheets/" + str(self.job_number) + ".pdf") add pathfile
        except OSError as e:
            print("Error: {} {}".format(e.filename, e.strerror))

    def send_sms(self, contact_number, body):
        account_sid = ACCOUNT_SID
        auth_token = AUTH_TOKEN
        client = Client(account_sid, auth_token)
        client.messages.create(
            to=contact_number,
            from_="ENKI", 
            body=body)
        return

    def daily_backup(self):
        gmail_user = GMAIL_USER
        gmail_pass = GMAIL_PASSWORD
        reciepents = GMAIL_USER
        msg = MIMEMultipart()
        msg['From'] = formataddr(('Enki', GMAIL_USER))  
        msg['To'] = reciepents
        msg['Subject'] = 'Database Backup - ' + date.today().strftime("%d/%m/%y") + \
                         ' - ' + str(datetime.today().time())
        msg.attach(MIMEText('', 'plain'))

        file_name = 'enki_sqlite_database.db'
        attachment = open(str(file_name), 'rb')

        part = MIMEApplication(attachment.read())
        part.add_header('Content-Disposition', 'attachment', filename='enki_sqlite_database.db')
        msg.attach(part)
        text = msg.as_string()
        try:
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(gmail_user, gmail_pass)
            server.sendmail(gmail_user, reciepents, text)
            server.quit()
            print("Email Sent!")
        except:
            print("Something went wrong...")

    def print_pdf(self):
        try:
            if os.name == 'nt':
                source_path = os.path.dirname(os.path.abspath(__file__))
                filename = source_path + "\\job_sheets\\" + str(self.job_number) + '.pdf'
                Popen(source_path + "\\PDFtoPrinter.exe" + " " + filename, shell=True)  # to specific printer
                #leave blank to send to a default printer  + " " + '"HP Deskjet 2540 series"'
            else:
                source_path = os.path.dirname(os.path.abspath(__file__))
                filename = source_path + "/job_sheets/" + str(self.job_number) + '.pdf'
                with open(filename) as f:
                    # call the system's lpr command
                    p = Popen(["lpr"],
                              stdin=f)  # don't need shell=True for a simple command, sent to a specific printer
                    # , "-P", "HP-Deskjet-2540-series"
                    # need to test with a printer to see what the output is
                    # popup might work with if p.communicate() is None then printererror().open()
                    return p.communicate()[0]
                    # p = Popen(["lpr", "-P", "HP-Deskjet-2540-series"] to print to a specific printer
                    # ["lpr"] to print to default printer
                    # lpstat -a to see all available printers
        except:
            print("An error occurred when sending the document to printer")
