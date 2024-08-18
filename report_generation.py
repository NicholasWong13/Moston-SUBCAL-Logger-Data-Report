import io
import re
import os
import pandas as pd
import matplotlib.pyplot as plt
from smbclient import ClientConfig, listdir, open_file
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Image
from reportlab.lib.styles import getSampleStyleSheet

def create_individual_report(csv_data, file_name, elements):
    # Normalize column names
    csv_data.columns = csv_data.columns.str.strip().str.lower().str.replace(' ', '_')

    # Ensure the 'date' column is in datetime format
    if 'date' in csv_data.columns:
        csv_data['date'] = pd.to_datetime(csv_data['date'], errors='coerce')

    # Create PDF content for this file
    styles = getSampleStyleSheet()
    
    # Add title for this file
    title = Paragraph(f"Report for {file_name}", styles['Title'])
    elements.append(title)
    elements.append(Spacer(1, 12))

    # Graph: Records over time (date)
    if 'date' in csv_data.columns:
        plt.figure(figsize=(14, 8))  # Increase the size of the graph
        date_range = pd.date_range(start=csv_data['date'].min(), end=csv_data['date'].max())
        date_counts = csv_data['date'].value_counts().sort_index().reindex(date_range, fill_value=0)
        date_counts.plot(kind='line', color='orange')
        plt.title(f'Records Over Time - {file_name}', fontsize=18)  # Increase title font size
        plt.xlabel('Date', fontsize=14)  # Increase label font size
        plt.ylabel('Count', fontsize=14)
        plt.xticks(rotation=45, ha='right', fontsize=12)
        plt.yticks(fontsize=12)  # Increase y-tick label font size
        plt.tight_layout()
        graph_image_path = f'records_over_time_{file_name}.png'
        plt.savefig(graph_image_path)
        plt.close()
        elements.append(Paragraph(f"Records Over Time (File: {file_name})", styles['Heading2']))
        elements.append(Image(graph_image_path, width=7.5 * inch, height=4.25 * inch))
        elements.append(Spacer(1, 12))
        
        # Clean up temporary image file
        if os.path.exists(graph_image_path):
            os.remove(graph_image_path)
    
    elements.append(PageBreak())

def generate_pdf_report():
    server_ip_list = [
        '172.16.7.8', '172.16.7.17', '172.16.7.73', '172.16.7.16', '172.16.7.111', 
        '172.16.7.237', '172.16.8.210', '172.16.8.16', '172.16.7.96', '172.16.7.246', 
        '172.16.8.84', '172.16.7.218', '172.16.7.26', '172.16.23.11', '172.16.22.164', 
        '172.16.22.55', '172.16.22.242'
    ]
    share_name = 'Avago.ATF.Common.x64'
    path_to_directory = 'SubCal.Logger'
    username = 'Admin'
    password = 'All4g00d'
    file_pattern = r'Cal_Logger_ACPF-9069-AP1_EIS.*\.csv'

    # Register the server with credentials
    ClientConfig(username=username, password=password)

    pdf_file_path = 'CSV_Data_Graphs_Report.pdf'
    elements = []
    
    for server_ip in server_ip_list:
        # Construct the full path to the directory for the current server
        full_directory_path = f"\\\\{server_ip}\\{share_name}\\{path_to_directory}"
        
        try:
            # List all files in the directory
            files = listdir(full_directory_path)
            
            # Filter files matching the pattern
            matched_files = [f for f in files if re.match(file_pattern, f)]
            
            if matched_files:
                # Sort matched files by name or modify as needed to select the most recent file
                matched_files.sort()
                for file_name in matched_files:
                    full_file_path = f"{full_directory_path}\\{file_name}"
                    
                    try:
                        # Open the file via smbclient and read its content
                        with open_file(full_file_path, mode='r', encoding='utf-8') as file:
                            csv_data = pd.read_csv(io.StringIO(file.read()))
                        
                        # Create individual report section
                        create_individual_report(csv_data, file_name, elements)
                    except Exception as e:
                        print(f"Error reading file {full_file_path}: {e}")

        except Exception as e:
            print(f"Error accessing directory {full_directory_path}: {e}")
    
    if elements:
        # Create the PDF document
        document = SimpleDocTemplate(pdf_file_path, pagesize=letter)
        document.build(elements)
        print(f"Graphical report saved to {pdf_file_path}")
        return pdf_file_path
    else:
        print("No matching files found on any server.")
        return None
