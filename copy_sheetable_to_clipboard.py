import pyperclip

# read the csv file
with open("out.csv") as f:
    csv_content = f.read()

# remove the headers
csv_content = "\n".join(csv_content.split("\n")[1:])

# parse to be sheetable
parsedData = csv_content.replace(",", "	")

# save to clipboard
pyperclip.copy(parsedData)
