import pandas as pd
import mysql.connector

# Replace the following with your MySQL database connection details
db_config = {
    'host': 'tb-pact.cagz85g48hl7.us-west-2.rds.amazonaws.com',
    'user': 'cfl',
    'password': 'cfl2016',
    'database': 'motechdata',
}

# Define queries
queries = [
    ("SELECT count(p.id) AS Registered_Patients, c.name AS Facility "
     "FROM cfl_patients p INNER JOIN cfl_clinics c ON c.id = p.clinic_id_OID "
     "WHERE p.creationDate BETWEEN '2020-09-30 00:00:01' AND '2024-02-06 23:59:59' "
     "AND c.name <> 'TB clinic' GROUP BY c.name"),
    # Add more queries here if needed
]

# Establish a connection to the MySQL database
try:
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()

    # Create a Pandas Excel writer using XlsxWriter as the engine
    excel_writer = pd.ExcelWriter('output_data.xlsx', engine='xlsxwriter')

    for i, query in enumerate(queries, start=1):
        cursor.execute(query)
        data = cursor.fetchall()
        column_names = [desc[0] for desc in cursor.description]
        df = pd.DataFrame(data, columns=column_names)
        # Write each DataFrame to a separate worksheet
        df.to_excel(excel_writer, sheet_name=f'Sheet{i}', index=False)

    # Close the cursor and connection
    cursor.close()
    connection.close()

    # Save the Excel file
    excel_writer.save()

    print("Data has been successfully exported to output_data.xlsx")

except mysql.connector.Error as err:
    print(f"Error: {err}")

finally:
    if connection.is_connected():
        connection.close()
        print("MySQL connection is closed")