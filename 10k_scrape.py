import requests
import pandas as pd
from bs4 import BeautifulSoup


base_url = r"https://www.sec.gov"

normal_url = r"https://www.sec.gov/Archives/edgar/data/1265107/0001265107-19-000004.txt"
normal_url = normal_url.replace('-', '').replace('.txt', '/index.json')

documents_url = r"https://www.sec.gov/Archives/edgar/data/1265107/000126510719000004/index.json"

content = requests.get(documents_url).json()

for file in content['directory']['item']:

    if file['name'] == 'FilingSummary.xml':

        xml_summary = base_url + \
            content['directory']['name'] + '/' + file['name']

        # print('-'*100)
        # print('File Name: ' + file['name'])
        # print('File Path: ' + xml_summary)


base_url = xml_summary.replace('FilingSummary.xml', '')

content = requests.get(xml_summary).content
soup = BeautifulSoup(content, 'lxml')

reports = soup.find('myreports')

master_reports = []

for report in reports.find_all('report')[:-1]:

    report_dict = {}
    report_dict['name_short'] = report.shortname.text
    report_dict['name_long'] = report.longname.text
    report_dict['position'] = report.position.text
    report_dict['category'] = report.menucategory.text
    report_dict['url'] = base_url + report.htmlfilename.text

    master_reports.append(report_dict)

    # print('-'*100)
    # print(base_url + report.htmlfilename.text)
    # print(report.longname.text)
    # print(report.shortname.text)
    # print(report.menucategory.text)
    # print(report.position.text)


statement_urls = []

for report_dict in master_reports:

    item1 = r"Consolidated Balance Sheets"
    item2 = r"Consolidated Statements of Operations and Comprehensive Income (Loss)"
    item3 = r"Consolidated Statements of Cash Flows"
    item4 = r"Consolidated Statements of Stockholder's (Deficit) Equity"

    report_list = [item1, item2, item3, item4]

    if report_dict['name_short'] in report_list:

        print('-'*100)
        print(report_dict['name_short'])
        print(report_dict['url'])

        statement_urls.append(report_dict['url'])

statements_data = []

for statement in statement_urls:

    statement_data = {}
    statement_data['headers'] = []
    statement_data['sections'] = []
    statement_data['data'] = []

    content = requests.get(statement).content
    report_soup = BeautifulSoup(content, features='lxml')

    for index, row in enumerate(report_soup.table.find_all('tr')):

        cols = row.find_all('td')

        if (len(row.find_all('th')) == 0 and len(row.find_all('strong')) == 0):
            reg_row = [ele.text.strip() for ele in cols]
            statement_data['data'].append(reg_row)

        elif (len(row.find_all('th')) == 0 and len(row.find_all('strong')) != 0):
            sec_row = cols[0].text.strip()
            statement_data['sections'].append(sec_row)

        elif (len(row.find_all('th')) != 0):
            hed_row = [ele.text.strip() for ele in row.find_all('th')]
            statement_data['headers'].append(hed_row)

        else:
            print('We encountered an error.')

    statements_data.append(statement_data)

income_header = statements_data[1]['headers'][1]
income_data = statements_data[1]['data']

income_df = pd.DataFrame(income_data)


# print('-'*100)
# print('Before Reindexing')
# print('-'*100)
# print(income_df.head())

income_df.index = income_df[0]
income_df.index.name = 'Category'
income_df = income_df.drop(0, axis=1)

# print('-'*100)
# print('Before Regex')
# print('-'*100)
# print(income_df.head())

income_df = income_df.replace('[\$,)]', '', regex=True)
income_df = income_df.replace('[(]', '-', regex=True)
income_df = income_df.replace('', 'NaN', regex=True)

# print('-'*100)
# print('Before type conversion')
# print('-'*100)
# print(income_df.head())

income_df = income_df.astype(float)

income_df.columns = income_header

# print('-'*100)
# print('Final Product')
# print('-'*100)

print(income_df)

# drop the data in a CSV file
# income_df.to_csv('income state.csv')
