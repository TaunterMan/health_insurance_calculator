
import tabula
import pandas as pd

# Extract tables from a PDF
pdf_path = "example.pdf"
tables = tabula.read_pdf(pdf_path, pages='all', multiple_tables=True)

df = pd.concat(tables[0:34])

# df['Merged_Column'] = df.apply(lambda row: ' '.join([str(x) for x in row if pd.notna(x)]), axis=1)

# Display the DataFrame with the merged column
# print(df[['Merged_Column']].head())

df.dropna(axis=1, inplace=False)  # Drops columns with all NaN values

# Initialize an empty list to store the merged descriptions
merged_descriptions = []

# Temporary variable to hold accumulated text for each row
current_description = ""

for i, row in df.iterrows():
    # If the current row is not NaN, append it to the current description
    if pd.notna(row['Important Questions']):
        current_description += " " + row['Important Questions'] if current_description else row['Important Questions']
    if pd.notna(row['Unnamed: 0']):
        current_description += " " + row['Unnamed: 0'] if current_description else row['Unnamed: 0']
    # If the row is NaN and we have accumulated some text, store it
    if not(pd.notna(row['Important Questions']) or pd.notna(row['Unnamed: 0'])):
        if current_description:
            merged_descriptions.append(current_description)
            current_description = ""  # Reset for the next block

# After the loop, add any remaining text in current_description
if current_description:
    merged_descriptions.append(current_description)

# Create a new DataFrame with the merged descriptions
merged_df = pd.DataFrame(merged_descriptions, columns=['Merged_Description'])

print(df)
