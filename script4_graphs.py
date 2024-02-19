import pandas as pd
import mysql.connector
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import schedule
import time
import matplotlib.pyplot as plt
from datetime import datetime

# MySQL database connection details
db_config = {
    'host': 'tb-pact.cagz85g48hl7.us-west-2.rds.amazonaws.com',
    'user': 'cfl',
    'password': 'cfl2016',
    'database': 'motechdata',
}

# Queries to be executed
todaydate = datetime.now()
todaydatestr = todaydate.strftime('%Y-%m-%d %H:%M:%S')
queries = [
    {
        'name': 'Registered_Patients',
        'query': "SELECT c.name AS Facility, count(p.id) AS Registered_Patients "
                 "FROM cfl_patients p INNER JOIN cfl_clinics c ON c.id = p.clinic_id_OID "
                 "WHERE p.creationDate BETWEEN '2020-09-30 00:00:01' AND '" + todaydatestr + "' "
                 "AND c.name <> 'TB clinic' GROUP BY c.name"
    },
    {
        'name': 'Active_Patients',
        'query': "SELECT c.name AS Facility, count(p.id) AS Active_Patients "
                 "FROM cfl_patients p INNER JOIN cfl_clinics c ON c.id = p.clinic_id_OID "
                 "where p.creationDate between '2020-09-30 00:00:01' and '" + todaydatestr + "' "
                 "AND p.status = 'ACTIVE' AND c.name <> 'TB clinic' group by c.name"
    },
    {
        'name': 'Quaterly_Registered_Patients',
        'query': "SELECT c.name AS Facility, count(p.id) AS quarterly_Registered_Patients "
                 "FROM cfl_patients p INNER JOIN cfl_clinics c ON c.id = p.clinic_id_OID "
                 "where p.creationDate between '2024-01-01 00:00:00' and '" + todaydatestr + "' "
                 "AND c.name <> 'TB clinic' group by c.name"
    }
]

def run_queries_and_send_email():
    try:
        # Establish a connection to the MySQL database
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()

        for query_info in queries:
            query_name = query_info['name']
            query = query_info['query']
            cursor.execute(query)
            data = cursor.fetchall()
            column_names = [desc[0] for desc in cursor.description]
            df = pd.DataFrame(data, columns=column_names)
            generate_and_save_graph(df, query_name)

        # Close MySQL cursor and connection
        cursor.close()
        connection.close()

        # Send email
        send_email()

    except mysql.connector.Error as err:
        print(f"Error: {err}")

# def generate_and_save_graph(dataframe, name):
#     # Generate graph
#     plt.figure(figsize=(10, 8))
#     plt.bar(dataframe['Facility'], dataframe.iloc[:, 1])
#     plt.title(f'{name} Graph')
#     plt.xlabel('Facility')
#     plt.ylabel(name.replace('_', ' '))
#     plt.xticks(rotation=45)

#     # Save graph as image
#     graph_filename = f'{name}_Graph.png'
#     plt.savefig(graph_filename)
#     plt.close()

def generate_and_save_graph(dataframe, name):
    # Set style
    plt.style.use('seaborn-v0_8-darkgrid')

    # Generate graph
    plt.figure(figsize=(12, 8))
    bars = plt.bar(dataframe['Facility'], dataframe.iloc[:, 1], color='skyblue')

    # Add data labels
    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, yval, round(yval, 2), va='bottom')

    plt.title(f'{name} Graph', fontsize=18)
    plt.xlabel('Facility', fontsize=14)
    plt.ylabel(name.replace('_', ' '), fontsize=14)
    plt.xticks(rotation=45, ha='right', fontsize=12)
    plt.yticks(fontsize=12)
    plt.tight_layout()  # Adjust layout to prevent clipping of labels

    # Save graph as image
    graph_filename = f'{name}_Graph.png'
    plt.savefig(graph_filename, dpi=300)
    plt.close()

def send_email():
    # Email configuration
    sender_email = 'academysupport@idi.co.ug'
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

    # Attach graphs
    for query_info in queries:
        query_name = query_info['name']
        graph_filename = f'{query_name}_Graph.png'
        attachment = open(graph_filename, 'rb')
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f'attachment; filename= {graph_filename}')
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
schedule.every().day.at("12:59").do(run_queries_and_send_email)
# Schedule script to run every Thursday at 11:00 AM
#schedule.every().thursday.at("11:00").do(run_queries_and_send_email)

while True:
    schedule.run_pending()
    time.sleep(1)