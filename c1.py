import os
import csv
from datetime import datetime



def SaveReport(program_no, test_datetime, pressure, pressure_unit,
               leak, leak_unit, result):

    folder_path = "C:/Reports/"

    # Create folder if it does not exist
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    # Today's CSV file
    current_date = datetime.now().strftime('%d-%m-%Y')
    filename = current_date + ".csv"
    full_file_path = os.path.join(folder_path, filename)

    # Default production count
    production_count = 1

    # Check existing file and get last ProductionCount
    if os.path.exists(full_file_path):

        try:
            with open(full_file_path, mode='r',
                      newline='', encoding='utf-8') as file:

                reader = csv.reader(file)
                rows = list(reader)

                if len(rows) > 1:
                    last_row = rows[-1]

                    if len(last_row) >= 8:
                        production_count = int(last_row[7]) + 1

        except Exception as ex:
            print("Error reading CSV:", ex)

    # Create new row
    new_row = [
        program_no,
        test_datetime,
        pressure,
        pressure_unit,
        leak,
        leak_unit,
        result,
        production_count
    ]

    # Check whether file already exists
    file_exists = os.path.exists(full_file_path)

    # Append data
    with open(full_file_path, mode='a',
              newline='', encoding='utf-8') as file:

        writer = csv.writer(file)

        # Write header for new file
        if not file_exists:
            writer.writerow([
                "ProgramNo",
                "TestDateTime",
                "Pressure",
                "PressureUnit",
                "Leak",
                "LeakUnit",
                "Result",
                "ProductionCount"
            ])

        # Write data
        writer.writerow(new_row)

    print("Data inserted into:", full_file_path)
    print("Production Count:", production_count)

    return production_count


count = SaveReport(
    "1",
    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "3",
    "4",
    "5",
    "6",
    "PASS"
)

