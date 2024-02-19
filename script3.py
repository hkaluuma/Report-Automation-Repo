import pandas as pd
import mysql.connector
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import schedule
import time

# MySQL database connection details
db_config = {
    'host': 'tb-pact.cagz85g48hl7.us-west-2.rds.amazonaws.com',
    'user': 'cfl',
    'password': 'cfl2016',
    'database': 'motechdata',
}

# Queries to be executed
todaydate = now()
queries = [
    {
        'name': 'Registered_Patients',
        'query': "SELECT c.name AS Facility, count(p.id) AS Registered_Patients "
                 "FROM cfl_patients p INNER JOIN cfl_clinics c ON c.id = p.clinic_id_OID "
                 "WHERE p.creationDate BETWEEN '2020-09-30 00:00:01' AND '" + todaydate + "' "
                 "AND c.name <> 'TB clinic' GROUP BY c.name"
    },
    {
        'name': 'Active_Patients',
        'query': "SELECT c.name AS Facility, count(p.id) AS Active_Patients "
                 "FROM cfl_patients p INNER JOIN cfl_clinics c ON c.id = p.clinic_id_OID "
                 "where p.creationDate between '2020-09-30 00:00:01' and '" + todaydate + "' "
                 "AND p.status = 'ACTIVE' AND c.name <> 'TB clinic' group by c.name"
    },
    {
        'name': 'Quaterly_Registered_Patients',
        'query': "SELECT c.name AS Facility, count(p.id) AS quarterly_Registered_Patients "
                 "FROM cfl_patients p INNER JOIN cfl_clinics c ON c.id = p.clinic_id_OID "
                 "where p.creationDate between '2024-01-01 00:00:00' and '" + todaydate + "' "
                 "AND c.name <> 'TB clinic' group by c.name"
    }
]

def run_queries_and_send_email():
    try:
        # Establish a connection to the MySQL database
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()

        # Create Excel writer
        excel_writer = pd.ExcelWriter('PACT_Report_data.xlsx', engine='xlsxwriter')

        for query_info in queries:
            query_name = query_info['name']
            query = query_info['query']
            cursor.execute(query)
            data = cursor.fetchall()
            column_names = [desc[0] for desc in cursor.description]
            df = pd.DataFrame(data, columns=column_names)
            df.to_excel(excel_writer, sheet_name=query_name, index=False)

        # Close MySQL cursor and connection
        cursor.close()
        connection.close()

        # Save Excel file
        excel_writer.close()

        # Send email
        send_email()

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        
def send_email():
    # Email configuration
    sender_email = 'academysupport@idi.co.ug'
    #receiver_emails = 'hkaluuma@idi.co.ug, fmusinguzi@idi.co.ug, sntale@idi.co.ug'
    receiver_emails = 'hkaluuma@idi.co.ug'
    subject = 'Automated PACT Weekly Report'
    body = 'Please find attached the PACT weekly report data.'

    # Create email message
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_emails
    msg['Subject'] = subject

    # Attach Excel file
    filename = 'PACT_Report_data.xlsx'
    attachment = open(filename, 'rb')
    part = MIMEBase('application', 'octet-stream')
    part.set_payload(attachment.read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', f'attachment; filename= {filename}')
    msg.attach(part)

    # Add body to email
    msg.attach(MIMEText(body, 'plain'))

    # Send email
    smtp_server = smtplib.SMTP('smtp.office365.com', 587)
    smtp_server.starttls()
    smtp_server.login(sender_email, '1234Uganda*')
    smtp_server.sendmail(sender_email, receiver_emails.split(', '), msg.as_string())
    smtp_server.quit()

# Schedule script to run daily at a specific time (e.g., 8:00 AM)
schedule.every().day.at("16:37").do(run_queries_and_send_email)

while True:
    schedule.run_pending()
    time.sleep(1)