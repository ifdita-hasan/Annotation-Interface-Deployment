import streamlit as st
import streamlit.components.v1 as components
import json
from data_utils import *
import os
import streamlit_survey as ss

survey = ss.StreamlitSurvey()

BUCKET_NAME = st.secrets.filenames["bucket_name"]
DATASET_FILE = st.secrets.filenames["dataset_file"]

st.set_page_config(layout="wide")

# Change it to True when you want to store on Google Cloud
save_on_cloud = True

# st.markdown(
#     """
#     <style>
#     .stSelectbox > div[data-baseweb="select"] > div {
# 		background-color: white;
#         color: black;
#     	        padding: 10px;
# 	}
#     </style>
#     """,
#     unsafe_allow_html=True
# )

# Updates the global dictionary
def update_global_dict(keys, dump = False):
    for key in keys:
        global_dict[key] = st.session_state[key]

    if not dump:
        return

    if "logged_in" in st.session_state and st.session_state["logged_in"]:
        if save_on_cloud:
            save_dict_to_gcs(BUCKET_NAME, f"data/state_eval_g4_{st.session_state['logged_in']}.json", global_dict)
        else:
            json.dump(global_dict, open(f"data/state_eval_g4_{st.session_state['logged_in']}.json", 'w'))
    elif "pid" in st.session_state and st.session_state["pid"]:
        if save_on_cloud:
            client = get_gc_client()
            bucket = client.get_bucket(BUCKET_NAME)
            if storage.Blob(bucket=bucket, name=f"data/state_eval_g4_{st.session_state['pid']}.json").exists(client):
                return
        else:
            if os.path.exists(f"data/state_eval_g4_{st.session_state['pid']}.json"):
                # load
                return
        if save_on_cloud:
            save_dict_to_gcs(BUCKET_NAME, f"data/state_eval_g4_{st.session_state['pid']}.json", global_dict)
        else:
            json.dump(global_dict, open(f"data/state_eval_g4_{st.session_state['pid']}.json", 'w'))
    else:
        if save_on_cloud:
            save_dict_to_gcs(BUCKET_NAME, f"data/state_eval.json", global_dict)
        else:
            json.dump(global_dict, open(f'data/state_eval.json', 'w'))

def select_main_option():
    st.session_state.selected_main_option = st.session_state.main_option

def example_finished_callback():
    for _ in st.session_state:
        global_dict[_] = st.session_state[_]
    global_dict["current_example_ind"] += 1

    if "logged_in" in st.session_state and st.session_state["logged_in"]:
        if save_on_cloud:
            save_dict_to_gcs(BUCKET_NAME, f"data/state_eval_g4_{st.session_state['logged_in']}.json", global_dict) 
        else:
            json.dump(dict(global_dict), open(f"data/state_eval_g4_{st.session_state['logged_in']}.json", 'w'))
    else:
        if save_on_cloud:
            save_dict_to_gcs(BUCKET_NAME, f"data/state_eval.json", global_dict)
        else:
            json.dump(dict(global_dict), open(f'data/state_eval.json', 'w'))
    st.session_state["reload"] = True
    js = '''
    <script>
        function scrollToTop() {
            var body = window.parent.document.querySelector(".main");
            body.scrollTop = 0;
        }
        setTimeout(scrollToTop, 300);  // 300 milliseconds delay
    </script>
    '''
    # st.markdown(js, unsafe_allow_html=True)
    components.html(js)


# Function takes in the unique user login and consent
def get_id():
    """Document Prolific ID"""

    if "logged_in" in st.session_state and st.session_state["logged_in"]:
        return True

    col1, col2, col3 = st.columns([2,3,2])
    with col2:
        # Checks if the id is in session, if true it marks the user as logged in
        if "pid" in st.session_state and st.session_state["pid"]:
            st.session_state["logged_in"] = st.session_state["pid"]
            st.session_state["reload"] = True
            return True
        # Otherwise asks the user to enter user login
        else:
            st.markdown(f'## Annotation Interface')
            st.warning("""Before you log in and begin annotating data,
                        please ensure you have read and fully understood our research information sheet.
                        :red[**By providing your Prolific ID, you are providing your informed consent**] to
                       participate in this research project. Please note that this study may contain
                       conversations related to distressing topics. If you have any questions or 
                       concerns about the research or your role in it, please reach out to our team before proceeding.""", icon="⚠️")
            st.text_input("Enter your Prolific ID", key="pid", on_change=update_global_dict, args=[["pid"], "True"])
            st.session_state["reload"] = True
            return False


if __name__ == "__main__":

    # st.set_page_config(layout="wide")

    # global styles for horizontal radio buttons
    st.write('<style>div.row-widget.stRadio > div{flex-direction:row;justify-content: center;} </style>', unsafe_allow_html=True)
    st.write('<style>div.st-bf{flex-direction:column;} div.st-ag{font-weight:bold;padding-left:2px;}</style>', unsafe_allow_html=True)

    if "reload" not in st.session_state or st.session_state["reload"]:
        if "logged_in" in st.session_state and st.session_state["logged_in"]:
            if save_on_cloud:
                global_dict = read_or_create_json_from_gcs(BUCKET_NAME, f"data/state_eval_g4_{st.session_state['logged_in']}.json")
            else:
                global_dict = json.load(open(f"data/state_eval_g4_{st.session_state['logged_in']}.json", 'r'))
        elif "pid" in st.session_state and st.session_state["pid"]:
            if save_on_cloud:
                global_dict = read_or_create_json_from_gcs(BUCKET_NAME, f"data/state_eval_g4_{st.session_state['pid']}.json")
            else:
                global_dict = json.load(open(f"data/state_eval_g4_{st.session_state['pid']}.json", 'r'))
        else:
            if save_on_cloud:
                global_dict = read_or_create_json_from_gcs(BUCKET_NAME, f"data/state_eval.json")
            else:
                global_dict = json.load(open(f'data/state_eval.json', 'r'))
        st.session_state["reload"] = False
        st.session_state["testcases"] = global_dict["testcases"]
        st.session_state["current_example_ind"] = global_dict["current_example_ind"]
    else:
        global_dict = st.session_state

    
    if "testcases_text" not in st.session_state:
        if save_on_cloud:
            testcases = read_or_create_json_from_gcs(BUCKET_NAME, DATASET_FILE)
            eval_info = read_or_create_json_from_gcs(BUCKET_NAME, f"data/session_level_definitions.json") 
        else:
            testcases = json.load(open('processed_dict_g1.json', 'r'))
            eval_info = json.load(open('data/session_level_definitions.json', 'r'))
        st.session_state["testcases_text"] = testcases
        st.session_state["eval_text"] = eval_info

    # print_dict = {}
    # for _ in st.session_state:
    #     if _ != "testcases_text":
    #         print_dict[_] = st.session_state[_]
    # print(print_dict)

    testcases = st.session_state["testcases_text"]
    #total_conv = len(testcases)
    eval_info = st.session_state["eval_text"]

    if get_id():

        example_ind = global_dict["current_example_ind"]


# - You have been provided a conversation between a simulated client and a simulated therapist, along with the change goal of the simulated client.
# - Please rate the simulated client in each conversation for realism along the 3 dimensions provided, while following the given instructions. :grey[**A more realistic conversation is assigned a higher score for all of the dimension.**]
# - Please also rate the simulated therapist in these conversations on the 4 dimensions provided, following the accompanying instructions.
# """)

        c1, c2 = st.columns(2)
        for key in global_dict:
            st.session_state[key] = global_dict[key]

        if example_ind >= len(global_dict["testcases"]):
            st.title("Thank you!")
            st.balloons()
            st.success("You have annotated all the examples! 🎉")
            st.success("Here is your completion code: C17FE3ZT")
        else:
            testcase = testcases[global_dict["testcases"][example_ind]]

            count_required_feedback = 0
            count_done_feedback = 0
            # for t in range(len(testcases)):
            with c1.container(height=1000):
                c_index = testcase['conv_index']
                h_index = testcase['helper_index']
                st.subheader(f"Case {example_ind + 1} of {len(global_dict['testcases'])}")
                st.markdown(f"""Instructions: Below is a :blue[conversation context] for psychotherapy conversation {c_index}. 
                                The helper response in red has been identified as a flawed response. 
                                You are also given a better response and feedback. We provide you what skill requires improvement.
                                Your task is to read through the conversation to identify the subareas of the skill that need improvement in the :red[flawed response].""")
                st.markdown(f"""Disclaimer: The conversations might contain grammatical or structural errors. Please ignore them when annotating.""")

                conv = testcase["input"]
                better_response = testcase["response"]["alternative"]
                feedback = testcase["response"]["feedback"]
                st.markdown(f'### **Conversation History**')
                for i in range(len(conv) - 1):
                    st.markdown(f':blue[{conv[i]}]')
                st.markdown(f':red[{conv[-1]}]')
                # st.subheader("Feedback")
                # st.markdown(f':green[{feedback}]')
                        
            with c2.container(height=1000):
                with st.container():
                    st.header("Evaluate Helper Response")
                    st.markdown(f"""Questions below assess the different aspects of the flawed response""")
                    bad_areas = testcase['response']['badareas']
                    subskill_options = [["The helper is asking questions that are too focused with closed-questions instead of exploring with open-ended questions.", 
                        "The helper is exploring the details of the seeker's situation.", 
                        "The helper is asking questions with a clear intention/goal.", 
                        "The helper is encouraging expression of feelings.", 
                        "There is a question in the flawed response.",
                        "The helper is focusing on the seeker instead of turning the attention to other people when asking questions. (i.e., asking what person X did, instead of asking how the seeker felt about X's behavior)", 
                        "The helper is asking questions with empathy.", 
                        "The helper is asking lengthy or multiple questions at once.", 
                        "When asking questions, the helper is focusing on one aspect instead of trying to cover everything.",
                        "The helper is asking questions that come off as mistrusting, or asking questions to fact check."], 
                        ["The helper is giving too much premature advice, answers, or solutions. This could be giving suggestions without first understanding the situation to know if it is applicable.", 
                        "The helper is telling seeker what to do or giving direct advice “you should”.", 
                        "The helper is imposing beliefs or personal values on the seeker."]]
                   
                    with st.container():
                        if "Questions" in bad_areas and "Suggestions" in bad_areas:
                            st.markdown(f"#### **Skill areas that need improvement: :red[Questions] and :red[Suggestions]**")
                            subskills = subskill_options[0] + subskill_options[1]
                        elif "Questions" in bad_areas and "Suggestions" not in bad_areas:
                            st.markdown(f"#### **Skill area that need improvement: :red[Questions]**")
                            subskills = subskill_options[0]
                        elif "Suggestions" in bad_areas and "Questions" not in bad_areas:
                            st.markdown(f"#### **Skill area that need improvement: :red[Suggestions]**")
                            subskills = subskill_options[1]
                        for j, option in enumerate(subskills):
                            count_required_feedback += 1
                            slider_key = f"case_{example_ind + 1}_subskill_{j + 1}"
                            st.write(f"**{j+1}. {option}**")
                            # default_value = " " if subskills else "None"
                            selection = survey.select_slider(" ", options=["Strongly Disagree", "Disagree", "Neutral", "Agree", "Strongly Agree"], kwargs = (slider_key), key= slider_key)
                            if slider_key in st.session_state and st.session_state[slider_key] != "None":
                                count_done_feedback += 1
                    st.checkbox('I have finished annotating', key=f"finished_{example_ind}", on_change=update_global_dict, args=[[f"finished_{example_ind}"]])
                

                if f"finished_{example_ind}" in st.session_state and st.session_state[f"finished_{example_ind}"]:
                    if count_done_feedback != count_required_feedback:
                        st.error('Some annotations seem to be missing. Please annotate all fields', icon="❌")
                    else:
                        st.success('We got your annotations!', icon="✅")
                        st.button("Submit final answers and go to next testcase", type="primary", on_click=example_finished_callback)
                        st.session_state["reload"] = True
