import pandas as pd
import mysql.connector

# Replace the following with your MySQL database connection details
# db_config = {
#     'host': '127.0.0.1',
#     'user': 'root',
#     'password': '',
#     'database': 'myschool',
# }

db_config = {
    'host': 'tb-pact.cagz85g48hl7.us-west-2.rds.amazonaws.com',
    'user': 'cfl',
    'password': 'cfl2016',
    'database': 'motechdata',
}

# Establish a connection to the MySQL database
try:
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()

    # Replace 'your_table_name' with the actual table name
    # query = "SELECT * FROM posts"
    query = "SELECT count(p.id) AS Registered_Patients, c.name AS Facility FROM cfl_patients p INNER JOIN cfl_clinics c ON c.id = p.clinic_id_OID where p.creationDate between '2020-09-30 00:00:01' and '2024-02-06 23:59:59' AND c.name <> 'TB clinic' group by c.name"
    cursor.execute(query)

    # Fetch all the data from the query result
    data = cursor.fetchall()

    # Get the column names
    column_names = [desc[0] for desc in cursor.description]

    # Create a DataFrame using pandas
    df = pd.DataFrame(data, columns=column_names)

    # Close the cursor and connection
    cursor.close()
    connection.close()

    # Write the DataFrame to an Excel file
    excel_file_path = 'output_data.xlsx'
    df.to_excel(excel_file_path, index=False)

    print(f"Data has been successfully exported to {excel_file_path}")

except mysql.connector.Error as err:
    print(f"Error: {err}")

finally:
    if connection.is_connected():
        connection.close()
        print("MySQL connection is closed")