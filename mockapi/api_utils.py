import json
import pandas as pd
# import matplotlib.pyplot as plt
from flask import jsonify


# Custom Exception
class EmptyDataFrameError(Exception):
    pass

# Custom Exception
class AgentCodeNotFoundError(Exception):
    pass

def generate_payload_and_response(messages):
    print("RequestIn: generate_payload_and_response")

    # Ensure 'Messages' column exists in the DataFrame
    if 'Messages' not in messages.columns:
        print("Error: 'Messages' column not found in input DataFrame.")
        raise KeyError("'Messages' column not found in input DataFrame.")
    
    list_json = []

    # Iterate over rows and process each message
    for index, rows in messages.iterrows():
        # Print the current message being processed
        print(f"Processing message {index}: {rows['Messages'][rows['Messages'].find('PAYLOAD'):rows['Messages'].find(', RESPONSE BODY')]}")

        # Split message on ' , ', starting from the 'PAYLOAD' part
        sub_message = rows['Messages'][rows['Messages'].find('PAYLOAD'):].split(' , ')

        # Ensure the message is in the expected format
        if len(sub_message) == 2 and 'PAYLOAD' in sub_message[0]:
            try:
                # Split payload and response by ' : '
                payload = sub_message[0].split(" : ")
                response = sub_message[1].split(" : ")

                # Ensure keys and values are properly cleaned and formatted
                json_data = json.loads('{"'+str(payload[0]).strip()+'" : '+str(payload[1]).strip().replace("'","\"") + ', "'+str(response[0]).strip()+'" : ' + str(response[1]).strip().replace("'","\"")+'}')


                # Check if the payload and response are correctly formatted
                if 'PAYLOAD' in json_data and 'RESPONSE BODY' in json_data:
                    list_json.append(json_data)
            except Exception as e:
                # print(f"Error processing message {index}: {e}")
                pass
        else:
            print(f"Invalid message format at index {index}: {sub_message}")
            pass

    # Check if list_json contains data
    if not list_json:
        print("No valid data found.")
        raise Exception("No valid data found.")

    # Extract payload and response into separate lists for DataFrame creation
    list_json_response = []

    temp_dict = {'RRN': [], 'AgentCode': [], 'TransferType': [], 'RequestType': []}

    for item in list_json:
        if 'PAYLOAD' in item and 'RESPONSE BODY' in item:
            temp_dict['RRN'].append(item['PAYLOAD']['RRN'])
            temp_dict['AgentCode'].append(item['PAYLOAD']['AgentCode'])
            temp_dict['TransferType'].append(item['PAYLOAD']['TransferType'])
            temp_dict['RequestType'].append(item['PAYLOAD']['RequestType'])
            list_json_response.append(item['RESPONSE BODY'])

    # If there is valid data, create a DataFrame for the payload
    try:
        if temp_dict:
            df = pd.DataFrame(temp_dict)
        else:
            print("No valid data to create DataFrame.")
            raise Exception("No valid data to create DataFrame.")
            # return None, None
    except Exception as e:
        print(f"Error creating DataFrame: {e}")
        raise Exception(f"Error creating DataFrame: {e}")
        # return None, None

    print('RequestOut: generate_payload_and_response')
    return df, list_json_response

# Example usage:
# Assuming you already have the DataFrame `messages` with a column 'Messages'
# messages = pd.read_excel('MockUnpaidTransactions.xlsx').dropna(how='any')  # Load the data
# payload_df, json_responses = generate_payload_and_response(messages)

# if payload_df is not None:
#     print(payload_df.head())



# payload_df['AgentCode'].unique()


# Function to process the DataFrame as per the steps
def process_agent_code(request_packet,payload_df, json_responses):
    print("RequestIn: process_agent_code")
    # df = pd.DataFrame(payload)
    print("Before Reading Agent_Code")
    agent_code = request_packet['AgentCode']
    print("After Reading Agent_Code")
    if agent_code:
        print("Step 1: Search for the first instance where 'agent_code' matches")
        matching_rows = payload_df[payload_df['AgentCode'] == agent_code]
        
        if not matching_rows.empty:
            try:
                print("Step 2: Store the first instance")
                first_instance = matching_rows.iloc[0]
                # print(first_instance.name)

                json_response = json_responses[first_instance.name]
                
                print("Step 3: Remove the first instance from the dataframe")
                payload_df.drop(matching_rows.index[0], inplace=True)
                
                print("Step 4: Check if DataFrame is empty after removal")
                if payload_df.empty:
                    print("No more instances in the DataFrame to process.")
                    # return None
                    raise EmptyDataFrameError("The DataFrame is empty after removal of the agent_code instance.")
                
                # Step 5: Return the stored instance
                return jsonify(json_response)
            except Exception as e:
                print(f"Error processing agent_code: {e}")
                raise Exception(f"Error processing agent_code: {e}")
        else:
            print("Error: No matching rows found for the given agent_code.")
            # If no matching row found, return None and the original dataframe
            raise AgentCodeNotFoundError("No matching rows found for the given agent_code.")
    else:
        print("Error: agent_code not found in request packet.")
        raise AgentCodeNotFoundError("agent_code not found in request packet.")