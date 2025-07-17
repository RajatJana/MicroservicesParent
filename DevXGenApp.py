import streamlit as st
import streamlit.components.v1 as components
import docx
import json
import pandas as pd
import re
from DevXGen import clone_repo, collect_key_files, detect_tech, generate_spec, cleanup, generate_pipeline
from AgentConnect import llm_rerun
from ExpertApp import show as expert_show

def render_text_progress_bar(current_step):
    steps = ["Extract Details","Review & Refine","Final Output"]

    step1_completed = bool(st.session_state.get('extracted_data'))
    step2_completed = bool(st.session_state.get('pipeline_code'))
    step3_completed = bool(st.session_state.get('final_code'))

    completed_steps = []
    if step1_completed:
        completed_steps.append(1)
    if step2_completed:
        completed_steps.append(2)
    if step3_completed:
        completed_steps.append(3)

    if not step1_completed:
        current_step = 1
    elif not step2_completed:
        current_step = 2
    elif not step3_completed:
        current_step = 3
    else:
        current_step = 3
    
    css = """
    <style>
       .progress-container {
           display: flex;
           align-items: flex-start;
           justify-content: space-between;
           width: 90%;
           margin: 30px auto;
           padding: 0;
       }
       .step-item {
           display: flex;
           flex-direction: column;
           align-items: center;
            text-align: center;
            flex: 1;
            position: relative;
            font-size: 12px;
        }
        .step-item:not(:last-child)::after {
            content: '';
            position: absolute;
            top: 17px;
            left: 50%;
            width: 100%;
            height: 3px;
            background-color: #e9ecef;
            z-index: 1;
        }
        .step-circle {
            width: 30px;
            height: 30px;
            border-radius: 50%;
            background-color: #ffffff;
            border: 3px solid #e9ecef;
            color: #000000 !important;
            display: flex;
            justify-content: center;
            align-items: center;
            font-weight: bold;
            font-size: 1rem;
            margin-bottom: 10px;
            position: relative;
            z-index: 2;
       }
       .step-label {
           margin-top: 3px;
           word-break: keep-all;
           font-weight: 500;

       }
       .step-item.completed .step-circle {
           background-color: #28a745;
           border-color: #28a745;
           color: white !important;
           font-size: 1rem;
       }
       .step-item.completed .step-label {
       }
       .step-item.completed::after {
           background-color: #28a745;
       }
       .step-item.active .step-circle {
           border-color: #1195CE;
           background-color: #1195CE;
           color: white !important;
       }
       .step-item.active .step-label {
           font-weight: bold;
       }
    </style>
    """
    
    html = '<div class="progress-container">'
    for i, step_name in enumerate(steps):
        step_num = i + 1
        status_class = "pending"
        circle_content = str(step_num)
        if step_num in completed_steps:
            status_class = "completed"
            circle_content = "✓"
        elif step_num == current_step:
            status_class = "active"

        html += f'<div class="step-item {status_class}">'
        html += f'  <div class="step-circle">{circle_content}</div>'
        html += f'  <div class="step-label">{step_name}</div>'
        html += '</div>'
    html += '</div>'
    st.markdown(css + html, unsafe_allow_html=True)

def render_file_progress_bar(current_step):
    steps = ["JSON Spec File Generation", "Review JSON Spec", "Jenkins File"]
    total_steps = len(steps)
    
    css = """
    <style>
       .progress-container {
           display: flex;
           align-items: flex-start;
           justify-content: space-between;
           width: 90%;
           margin: 30px auto;
           padding: 0;
       }
       .step-item {
           display: flex;
           flex-direction: column;
           align-items: center;
            text-align: center;
            flex: 1;
            position: relative;
            font-size: 12px;
        }
        .step-item:not(:last-child)::after {
            content: '';
            position: absolute;
            top: 17px;
            left: 50%;
            width: 100%;
            height: 3px;
            background-color: #e9ecef;
            z-index: 1;
        }
        .step-circle {
            width: 30px;
            height: 30px;
            border-radius: 50%;
            background-color: #ffffff;
            border: 3px solid #e9ecef;
            color: #000000 !important;
            display: flex;
            justify-content: center;
            align-items: center;
            font-weight: bold;
            font-size: 1rem;
            margin-bottom: 10px;
            position: relative;
            z-index: 2;
       }
       .step-label {
           margin-top: 3px;
           word-break: keep-all;
           font-weight: 500;
       }
       .step-item.completed .step-circle {
           background-color: #28a745;
           border-color: #28a745;
           color: white !important;
           font-size: 1rem;
       }
       .step-item.completed .step-label {
       }
       .step-item.completed::after {
           background-color: #28a745;
       }
       .step-item.active .step-circle {
           border-color: #1195CE;
           background-color: #1195CE;
           color: white !important;
       }
       .step-item.active .step-label {
           font-weight: bold;
       }
    </style>
    """
    
    html = '<div class="progress-container">'
    for i, step_name in enumerate(steps):
        step_num = i + 1
        status_class = "pending"
        circle_content = str(step_num)
        if step_num < current_step:
            status_class = "completed"
            circle_content = "✓"
        elif step_num == current_step:
            status_class = "active"
        html += f'<div class="step-item {status_class}">'
        html += f'  <div class="step-circle">{circle_content}</div>'
        html += f'  <div class="step-label">{step_name}</div>'
        html += '</div>'
    html += '</div>'
    st.markdown(css + html, unsafe_allow_html=True)

def is_generation_supported(tech):
    supported_generation = [
        "Azure DevOps YAML", "Jenkins"
        ]
    return (tech) in supported_generation

def show():
    if 'mod_chat_history' not in st.session_state:
        st.session_state.mod_chat_history = []
    if 'mod_pipeline_chat_open' not in st.session_state:
        st.session_state.mod_pipeline_chat_open = False
    if 'refine_chat' not in st.session_state:
        st.session_state.refine_chat = False
    if "project_path" not in st.session_state:
        st.session_state.project_path = None
    if "extracted_data" not in st.session_state:
        st.session_state.extracted_data = None
    if "user_additions" not in st.session_state:
        st.session_state.user_additions = ""
    if 'step' not in st.session_state:
        st.session_state.step = 1
    if 'input_method' not in st.session_state:
        st.session_state.input_method = "text"
    if 'repo_link' not in st.session_state:
        st.session_state.repo_link = ""
    if 'repo' not in st.session_state:
        st.session_state.repo = ""
    if 'extracted_details' not in st.session_state:
        st.session_state.extracted_details = None
    if 'extracted_data' not in st.session_state:
        st.session_state.extracted_data = None
    if 'specification' not in st.session_state:
        st.session_state.specification = None
    if 'pipeline_code' not in st.session_state:
        st.session_state.pipeline_code = None
    if 'active_step' not in st.session_state:
        st.session_state.active_step = 1
    if 'show_progress' not in st.session_state:
        st.session_state.show_progress = True
    if 'stages' not in st.session_state:
        st.session_state.stages = [{"stage": "", "tool": ""}]
    if 'user_validated' not in st.session_state:
        st.session_state.user_validated = False
    if 'feedback_mode' not in st.session_state:
        st.session_state.feedback_mode = False
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'current_feedback' not in st.session_state:
        st.session_state.current_feedback = ""

    st.markdown("<h2 style='color: #1195CE;'>✨ Pipeline Generator</h2>", unsafe_allow_html=True)
    if st.session_state.get('show_progress'):
        if st.session_state.input_method == "text":
            render_text_progress_bar(st.session_state.step)
        elif st.session_state.input_method == "file":
            render_file_progress_bar(st.session_state.step)

        disabled_select = st.session_state.active_step > 1

        with st.container(border=True):
            col1, col2 = st.columns(2)
            with col1:  
                tech = st.selectbox(
                    "**🧩 Pipeline Technology**", 
                    ["Azure DevOps YAML", "Jenkins", "AWS CodePipeline(⌛)"], 
                    index=None, 
                    placeholder="Select Pipeline Technology",
                    disabled=disabled_select,
                    help="The Desired CI/CD Pipeline Technology"
                ) 
            with col2:  
                os = st.selectbox(
                    "**🖥️ OS**", 
                    ["Linux", "Windows"], 
                    index=None, 
                    placeholder="Select Operating System",
                    disabled=disabled_select,
                    help="The operating system where pipeline will be running"
                )


    # Text input area (shown when text input method is selected)
    if st.session_state.input_method == "text":

        if tech is None or os is None:
            st.info("Please select Pipeline Technology & OS")
        elif not is_generation_supported(tech):
            st.error(f"{tech} generation is not supported yet")
        else:
            st.markdown('<div class="narrow-textarea">', unsafe_allow_html=True)
            text_area_key = f"pipeline_input_text_{st.session_state.get('text_reset_counter', 0)}"
            repo_key = f"repo_input_{st.session_state.get('text_reset_counter', 0)}"
       
            def on_text_change():
                if st.session_state.get(text_area_key, "") == "":
                    st.session_state.text_reset_counter = st.session_state.get('text_reset_counter', 0) + 1
                    st.session_state.repo_link = ""
                    st.session_state.extracted_data = None
                    st.session_state.extracted_details = None
                    st.session_state.specification = None
                    st.session_state.pipeline_code = None
                    st.session_state.active_step = 1
                    st.rerun()

            repo_link = st.text_input(
                "🔗 GitHub Repository URL:",
                placeholder="https://github.com/your/repo.git",
                value=st.session_state.repo_link,
                key=text_area_key,
                on_change=on_text_change
            )
            st.markdown('</div>', unsafe_allow_html=True)
       
            if repo_link and repo_link!= st.session_state.repo_link:
                st.session_state.repo_link = repo_link
                st.session_state.extracted_data = None
                st.session_state.extracted_details = None
                st.session_state.specification = None
                st.session_state.pipeline_code = None
                st.session_state.active_step = 1
                st.rerun()

    # Process steps based on current active step 
    if st.session_state.repo_link:
        # Step 1: Extraction
        if st.session_state.active_step == 1:
            st.subheader("1. Extract Details")
            
            if not st.session_state.extracted_data:
                with st.spinner("Cloning and analyzing repo..."):
                    project_path, error = clone_repo(repo_link)
                    if error:
                        st.error(f"Failed to clone repository: {error}")
                    elif not project_path:
                        st.warning("Something went wrong.")
                    else:
                        files_data = collect_key_files(project_path)
                        if not files_data:
                            st.warning("No valid config files found for analysis.")
                            cleanup(project_path)
                        else:
                            st.session_state.extracted_data = detect_tech(files_data, repo_link)
                            st.session_state.project_path = project_path
                            st.session_state.repo_link = repo_link
                            st.success("Technology analysis completed!")
                            st.rerun()

            if st.session_state.extracted_data:
                    st.markdown("### 🧾 Tech Stack Analysis")
                    st.code(st.session_state.extracted_data)

                    st.markdown("### ➕ Add Optional Custom CI/CD Instructions")
                    st.session_state.user_additions = st.text_area("Custom instructions (e.g., add SonarQube, secrets scan)", value= st.session_state.user_additions)


            cols = st.columns([1, 1, 1.2, 1, 1])
            with cols[4]:
                    if st.button("▶ Generate", key="next1", use_container_width=True):
                        st.session_state.active_step = 2
                        st.rerun()

            st.subheader("📘 Example Instructions for Common CI/CD Stages")

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("### 🔍 SonarQube Analysis")
                st.code("""Add SonarQube analysis using server URL http://sonarqube.mycompany.com with projectKey=my-app and loginToken=my-token. Publish report to target/sonar-report.""")

                st.markdown("**Required Inputs:**")
                st.markdown("""
            - SonarQube Server URL  
            - Project key  
            - Authentication token  
            - Report path (optional)
            """)

                st.markdown("### ✅ JUnit Testing")
                st.code("""Run JUnit tests after build using Maven Surefire Plugin. Test reports should be stored at target/surefire-reports.""")

                st.markdown("**Required Inputs:**")
                st.markdown("""
            - Test framework (e.g., JUnit, TestNG)  
            - Report directory (e.g., target/surefire-reports)  
            - Optional test parameters
            """)

            with col2:
                st.markdown("### ☁️ Deploy to AWS")
                st.code("""Deploy the application to AWS EC2 using SSH. Use private key stored in AWS Secrets Manager and deploy the WAR to /opt/tomcat/webapps.""")

                st.markdown("**Required Inputs:**")
                st.markdown("""
            - Deployment type (EC2, ECS, Lambda)  
            - Region & credentials method  
            - Artifact path  
            - Deployment location
            """)

                st.markdown("### ☁️ Deploy to Azure")
                st.code("""Deploy to Azure Web App using Azure DevOps publish profile. App name is myapp-azure, and resource group is my-rg.""")

                st.markdown("**Required Inputs:**")
                st.markdown("""
            - Deployment target (Web App, VM, AKS)  
            - App/service name  
            - Resource group  
            - Credentials or publish profile method
            """)

                st.markdown("### ☁️ Deploy to Google Cloud")
                st.code("""Deploy to Google Cloud Run using gcloud CLI. Container image is gcr.io/my-project/myapp:latest.""")

                st.markdown("**Required Inputs:**")
                st.markdown("""
            - Deployment type (Cloud Run, GKE, App Engine)  
            - Container/image path  
            - Project ID & region  
            - Authentication method
            """)

        # Step 2: Specification
        elif st.session_state.active_step == 2:
            st.subheader("Draft Pipeline:")           

            if not st.session_state.specification:
#                if st.button("Generate Specification"):
                with st.spinner("Generating Specification..."):
                    st.session_state.specification = generate_spec(
                    st.session_state.extracted_data,
                    st.session_state.repo_link,
                    st.session_state.user_additions
                )
                    st.rerun()

            if not st.session_state.pipeline_code and st.session_state.specification:
                # if st.button("Generate Pipeline Code"):
                 with st.spinner("Generating code..."):
                    st.session_state.pipeline_code = generate_pipeline(
                    st.session_state.extracted_data,
                    st.session_state.repo_link,
                    st.session_state.user_additions,
                    tech,
                    st.session_state.specification,
                    os
                )
                    st.rerun()


            if st.session_state.specification and st.session_state.pipeline_code:
                with st.expander("Specification", expanded= False):
                    st.markdown(st.session_state.specification)


            if st.session_state.pipeline_code:
                st.write("**Generated Code:**")
                st.code(st.session_state.pipeline_code, language='yaml')


                cols = st.columns([1, 1, 1, 1, 1, 1, 1])
                with cols[0]:
                    if st.button("◀ Back", key="back_btn_1", use_container_width=True):
                        st.session_state.active_step = 1
                        st.rerun()
                with cols[2]:
                    if st.button("🧠 Refine", use_container_width=True):
                        st.session_state.refine_chat = True
                        st.session_state.feedback_mode = False
                with cols[4]:
                    if st.button("💬 Request", key="feedback_btn", use_container_width=True):
                        st.session_state.feedback_mode = True
                        st.session_state.refine_chat = False
                        st.rerun()
                with cols[6]:
                    if st.button("✅ Confirm", type="primary", key="valid_btn", use_container_width=True):
                        st.session_state.user_validated = True
                        st.session_state.final_code = st.session_state.pipeline_code
                        st.session_state.active_step = 3
                        st.rerun()

                if st.session_state.refine_chat:
                    expert_show()

                if st.session_state.feedback_mode:
                    # Feedback mode - chat-like interface
 
                    
                    # Display chat history
                    with st.expander("**Conversation History**"):
                        #st.write("**Conversation History**")
                        if not st.session_state.chat_history:
                            st.write("No conversation history yet.")
                        else:
                            for msg in st.session_state.chat_history:
                                if msg['role'] == 'user':
                                    st.markdown(f"**🧑‍💻 You:** {msg['content']}")
                                else:
                                    st.markdown(f"**🤖 Assistant:** {msg['content']}")
                    
                    # Feedback input
                    with st.container(border=True):
                        feedback = st.text_area(
                            "Enter your request for changes:",
                            value=st.session_state.current_feedback,
                            key="feedback_input"
                        )
                        
                        cols =st.columns([4,1,1,1,1,1,2])
                        with cols[0]:

                            if st.button("Request"):
                                if feedback.strip():
                                    st.session_state.current_feedback = feedback
                                    
                                    with st.spinner("Processing your request..."):
                                        try:
                                            # Prepare the chat history in the format expected by llm_rerun
                                            chat_history = [
                                                {"user": msg["content"], "response": msg["content"] if msg["role"] == "assistant" else ""}
                                                for msg in st.session_state.chat_history
                                                if msg["role"] == "assistant"  # Only include assistant responses in history
                                            ]
                                            
                                            # Process feedback and update conversion
                                            response = llm_rerun(
                                                st.session_state.pipeline_code, 
                                                chat_history,
                                                feedback
                                            )
                                            
                                            # Extract the code from the response (assuming it contains markdown with code blocks)
                                            code_match = re.search(r"```(?:yaml|json|[\w]*)\n(.*?)```", response, re.DOTALL)
                                            updated_output = code_match.group(1).strip() if code_match else response
                                            
                                            # Update the conversion output
                                            st.session_state.pipeline_code = updated_output
                                            
                                            # Add to chat history
                                            st.session_state.chat_history.extend([
                                                {"role": "user", "content": feedback},
                                                {"role": "assistant", "content": response}
                                            ])
                                            
                                            st.rerun()
                                        except Exception as e:
                                            st.error(f"Error processing feedback: {str(e)}")
                        with cols[6]:
                            if st.button("Exit",use_container_width=True):
                                st.session_state.feedback_mode = False
                                st.rerun()
                    
        # Step 3: Code Generation
        elif st.session_state.active_step == 3:
            st.subheader("## Final Pipeline:")

            if st.session_state.final_code is None:  
                # For now just use the validated conversion output as final code
                st.session_state.final_code = st.session_state.pipeline_code
                st.rerun()  
            
            if st.session_state.final_code:  
                st.code(st.session_state.final_code, language="yaml") 
            
            match = re.search(r"```(?:yaml|json|[\w]*)\n(.*?)```", st.session_state.final_code, re.DOTALL)
            if match:
                 clean_code = match.group(1).strip()
            else:
                 clean_code = st.session_state.final_code

            if tech == "Azure DevOps YAML":
                file_name = "azure_pipeline.yml"
                mime_type = "text/yaml"
            elif tech == "Jenkins":
                file_name = "Jenkinsfile"
                mime_type = "text/plain"   


            cols = st.columns([1, 1, 1.2, 1, 1])  
            with cols[0]:  
                if st.button("◀ Back", use_container_width=True):
                    st.session_state.active_step = 2
                    st.rerun() 
            with cols[2]:  
                st.download_button(
                    label="💾 Download ",
                    data=clean_code,
                    file_name=file_name,
                    mime=mime_type,
                    use_container_width=True
                )

            with cols[4]:
                if st.button("✏️ Connect", use_container_width=True):
                    st.session_state.mod_pipeline_chat_open = True

            if st.session_state.mod_pipeline_chat_open:
                st.markdown("### ✨ Connect with the Assistant")

                # Suggestions
                suggestions = [
                    "Explain the pipeline",
                    "Give Setup Instructions",
                    "Explain each stage with comments",
                    "Review the pipeline"
                ]
                selected_suggestion = st.selectbox("Quick Suggestions", [""] + suggestions)
                user_mod_input = st.text_area("💬 Ask the Assistant about the code", value=selected_suggestion, key="user_mod_input_area")

                if st.button("🔁 Ask"):
                    original_code = st.session_state.final_code
                    #last_response = st.session_state.mod_chat_history[-1]['response'] if st.session_state.mod_chat_history else st.session_state.pipeline_code
                    chat_history = st.session_state.mod_chat_history
                    with st.spinner("Assistant is processing your input..."):
                        response = llm_rerun(original_code, chat_history, user_mod_input)
                        st.session_state.mod_chat_history.append({
                            "user": user_mod_input,
                            "response": response
                        })
                    st.rerun()

            for i, chat in enumerate(st.session_state.mod_chat_history):
                st.markdown(f"#### 🧑‍💻 You: {chat['user']}")
                with st.expander(f"🤖 Response {i+1}", expanded=True):
                        st.markdown(chat['response'])


