###Robin Tan############################################################################################################
###Piazza Checker Program###############################################################################################
###November 2019########################################################################################################

###Imports##############################################################################################################
import numpy as np
import pandas as pd
import csv

###Parameters###########################################################################################################
path = r'C:\Users\Robin\Documents\Robin\Penn\Penn Other\Piazza Checker Program\data_processed.csv'

###Functions############################################################################################################
def process_name(name):
    if name == 'John':
        return 'John Ta'
    if name == 'Adam':
        return 'Adam Alghalith'
    if name == 'Nicha t':
        return 'Nicha Thongtanakul'
    if name == 'Jeewon Rebecca Lee':
        return 'Jeewon Lee'
    return name

def byLastName(name):
    return name.split(" ")[1]

def process_folder(folder):
    answerer_list = []
    if type(folder) == float:
        return answerer_list
    folder_split = folder.split('; ')
    for answerer in folder_split:
        if 'misc' not in answerer:
            answerer_split = answerer.split('_')
            answerer = answerer_split[1].capitalize() + ' ' + answerer_split[0].capitalize()
            if answerer == 'Sabrina Dasilva':
                answerer = 'Sabrina DaSilva'
            if answerer == 'John Lee':
                answerer = 'Jonathan Lee'
            answerer_list.append(answerer)
    return answerer_list

def answered_on_time(time_of_question, time_of_response):
    question_time_split = time_of_question.split(' ')
    response_time_split = time_of_response.split(' ')

    question_time_day_split = question_time_split[0].split('-')
    question_time_day = int(''.join(question_time_day_split))
    response_time_day_split = response_time_split[0].split('-')
    response_time_day = int(''.join(response_time_day_split))

    if response_time_day - question_time_day < 2 \
            or (response_time_day == 20191001 and question_time_day == 20190930) \
            or (response_time_day == 20191101 and question_time_day == 20191031) \
            or (response_time_day == 20191201 and question_time_day == 20191130): #If response is less than 2 days
        return True
    elif (response_time_day - question_time_day == 2) \
            or (response_time_day == 20191001 and question_time_day == 20190929) \
            or (response_time_day == 20191002 and question_time_day == 20190930) \
            or (response_time_day == 20191101 and question_time_day == 20191030) \
            or (response_time_day == 20191102 and question_time_day == 20191031) \
            or (response_time_day == 20191201 and question_time_day == 20191129) \
            or (response_time_day == 20191202 and question_time_day == 20191130): #If response takes 2 days
        question_time_hour_split = question_time_split[1].split(':')
        question_time_hour = int(''.join(question_time_hour_split))
        response_time_hour_split = response_time_split[1].split(':')
        response_time_hour = int(''.join(response_time_hour_split))
        if (response_time_hour <= 160000): #If response hour is less than/equal to 3PM (okay)
            return True
        else: #If response hour is greater than question hour (late)
            return False
    else: #If response takes more than 2 days
        return False

def isCurrentSession(time_of_question):
    question_time_split = time_of_question.split(' ')
    question_time_day_split = question_time_split[0].split('-')
    question_time_day = int(''.join(question_time_day_split))
    return question_time_day >= 20191030

###Body#################################################################################################################

###Load Data
# all_data = pd.read_csv(path, encoding='cp1252')
all_data = pd.read_csv(path, encoding='utf8')
students_list = []
dict_indices = {}

###Create dictionary of students' indices
for name in all_data['Name']:
    name = process_name(name)
    if name not in students_list:
        students_list.append(name)
students_list.sort()

count = 0
students_list.sort(key = byLastName)
for student in students_list:
    dict_indices[student] = count
    count += 1

###Create 2D Matrix of correspondences, Array of asked, Array of answered
size = len(students_list)
correspondences = np.zeros((size, size))
questioned_array = np.zeros(size) #denominator
responded_array = np.zeros(size) #numerator

###Iterate through rows of all_data
currentPost = '0'
answerer_list = []
responded = []
time_of_question = ''
skip_row = False

for index, row in all_data.iterrows():
    if row['Post Number'] != currentPost: #New Post Number
        # Skip this entire Post Number if any of the following conditions hold:
        if row['Name'] == 'John':
                # or int(''.join(row['Created At'].split(' ')[1].split(':'))) >= 160000:
            skip_row = True
            continue
        if type(row['Submission']) is not float:
            if '$skip123$' in row['Submission']:
                skip_row = True
                continue
        responded = []
        currentPost = row['Post Number']
        skip_row = False
        asker = process_name(row['Name'])
        answerer_list = process_folder(row['Folders'])
        asker_index = dict_indices[asker]

        # Updates time_of_question
        time_of_question = row['Created At']

        #Updates questioned_array and correspondences
        for answerer in answerer_list:
            answerer_index = dict_indices[answerer]

            #Updates questioned_array
            if isCurrentSession(time_of_question):
                #Updates only if during current session
                questioned_array[answerer_index] += 1

            #Updates correspondences
            correspondences[asker_index, answerer_index] += 1

    else: #Post Number has been seen before
        if skip_row:
            continue
        responder = process_name(row['Name'])
        if responder not in responded: #Have not seen this responder
            responded.append(row['Name'])

            #Checking if responder is answering a question directed toward him/her
            if responder in answerer_list:
                answered_timely = answered_on_time(time_of_question, row['Created At'])
                if answered_timely:
                    #Update responded_array if responder answered on time
                    responder_index = dict_indices[responder]
                    if isCurrentSession(time_of_question):
                        # Updates only if during current session
                        responded_array[responder_index] += 1

dict_percentages = {}
for index in range(len(students_list)):
    if questioned_array[index] > 0:
        percentage = round(float(responded_array[index])/questioned_array[index], 2)
    else:
        percentage = 'N/A'
    dict_percentages[students_list[index]] = percentage

###Export to files######################################################################################################
with open('Percentage of Timely Responses.txt', 'w') as txt_file:
    txt_file.write('Percentages of Timely Responses\n--------------------------------\n')
    for key in students_list:
        txt_file.write('\n' + str(key) + ': ' + str(dict_percentages[key]) + '. '
                       + str(int(responded_array[dict_indices[key]])) + '/'
                       + str(int(questioned_array[dict_indices[key]])) + '.')

with open ('Matrix of Correspondences.csv', 'w') as csv_file:
    wr = csv.writer(csv_file)
    correspondences_df = pd.DataFrame(correspondences)
    correspondences_df.columns = students_list
    correspondences_df.index = students_list
    correspondences_df.to_csv(csv_file)