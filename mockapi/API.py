import pandas as pd
from flask import Flask, request, jsonify
import api_utils

print("Outside")
messages = pd.read_excel('MockUnpaidTransactions.xlsx').dropna(how='any')

payload_df, json_responses = api_utils.generate_payload_and_response(messages)

app = Flask(__name__)




# Example usage
@app.route('/GenericRTPS/DownloadUnpaidTrans', methods=['POST'])
def end_point():
    print(type(messages))
    agent_code_input = request.get_json()


    try:
        print(agent_code_input['AgentCode'])
        stored_instance = api_utils.process_agent_code(agent_code_input, payload_df, json_responses)
        print("Stored Instance:")
        print(stored_instance.response)
        if stored_instance:
            return stored_instance
        else:
            return jsonify({"error": "No matching agent_code found"})
    except Exception as e:
        print(f"Error: {e}")
        if KeyError:
            return jsonify({"error": f"KeyError {str(e)}"})
        else:
            return jsonify({"error": str(e)})


if __name__ == '__main__':
    app.run('0.0.0.0',debug=True, port=8001)