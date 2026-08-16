CHAPTER THREE
SYSTEM ANALYSIS AND DESIGN
## 3.1 Introduction
This chapter presents the analysis and design of the proposed machine learning-based decision support system for predicting child malnutrition among children under five years of age using the Central African Republic Multiple Indicator Cluster Survey (MICS6) dataset (UNICEF, n.d.). The chapter describes the existing system used to assess child malnutrition, identifies its limitations, and proposes a machine learning-based decision support system to improve prediction and support evidence-based decision-making. It further presents the system requirements, feasibility analysis, system architecture, process models, database design, and user interface design. These design components provide the blueprint for the implementation presented in Chapter Four.
## 3.2 System Analysis
### 3.2.1 Overview
System analysis is the process of studying an existing system to understand how it operates, identify its strengths and weaknesses, and determine user requirements for developing an improved system. In this study, system analysis focuses on understanding the current methods used to assess child malnutrition and identifying opportunities where machine learning can improve prediction accuracy and support health professionals in decision-making.
The proposed system is designed to analyse child, maternal, household, and environmental factors obtained from the Central African Republic MICS6 dataset and predict the likelihood of child malnutrition. The prediction results will assist healthcare workers, nutrition officers, researchers, and policy makers in identifying children at risk and planning timely interventions.
### 3.2.2 Existing System
Currently, the assessment of child malnutrition in many developing countries, including the Central African Republic, primarily relies on anthropometric measurements and statistical analyses. Health professionals collect information such as a child's age, weight, height, sex, breastfeeding status, and other health indicators during household surveys or health facility visits. These measurements are then compared with the World Health Organization (WHO) Child Growth Standards, which classify children as stunted, wasted, underweight, overweight, or normal based on height-for-age, weight-for-height, and weight-for-age z-scores (World Health Organization, 2006).
Although national surveys such as the Multiple Indicator Cluster Survey (MICS) provide valuable information on the nutritional status of children, the analysis is largely descriptive and focuses on estimating prevalence rates at national or regional levels. Traditional statistical techniques, including frequency distributions, cross-tabulations, chi-square tests, and logistic regression, are commonly used to identify significant factors associated with child malnutrition.
While these approaches provide useful insights, they generally explain relationships between variables rather than generating individual-level predictions. As a result, healthcare providers may find it difficult to identify children who are at high risk before malnutrition becomes severe. Decision-making often depends on manual interpretation of statistical outputs, which can be time-consuming and may not fully capture the complex interactions among multiple risk factors.
### 3.2.3 Limitations of the Existing System
Despite the usefulness of current assessment methods, several limitations remain:
The system relies heavily on descriptive statistical analysis, which provides limited predictive capability.
Manual analysis of survey data is time-consuming and requires specialized statistical expertise.
The existing approach cannot automatically identify children who are at high risk of malnutrition before the condition develops.
Traditional statistical models may not effectively capture complex, non-linear relationships among socioeconomic, demographic, health, and environmental factors.
Decision-makers often receive retrospective reports rather than real-time predictive information.
There is limited integration of machine learning techniques into routine nutritional assessment and decision support.
These limitations highlight the need for an intelligent prediction system capable of analysing multiple risk factors simultaneously and providing accurate predictions to support healthcare professionals.
### 3.2.4 Proposed System
To address the identified limitations, this study proposes a Machine Learning-Based Decision Support System (ML-DSS) for predicting child malnutrition using the Central African Republic MICS6 dataset. The system will integrate statistical analysis with supervised machine learning algorithms to support evidence-based nutritional assessment.
The proposed system will allow authorized users to enter or import child-related information, preprocess the data, and generate predictions regarding the nutritional status of a child. The system will compare the performance of four supervised machine learning algorithms:
Logistic Regression
Decision Tree
Random Forest
Support Vector Machine (SVM)
The model that achieves the best predictive performance based on evaluation metrics such as accuracy, precision, recall, F1-score, and ROC-AUC will be selected as the final prediction model.
These four algorithms were selected because they represent the range of approaches most commonly and successfully applied to MICS- and DHS-based child malnutrition prediction in the literature, and together they balance interpretability against predictive power. Logistic Regression provides a transparent, coefficient-based baseline that is easy for non-technical health professionals to interpret (Rahman et al., 2021). Decision Tree offers a rule-based structure that mirrors clinical decision-making, while Random Forest, an ensemble of decision trees, has consistently achieved among the highest reported accuracies for stunting and malnutrition classification on MICS/DHS data, including in Zambia (Chilyabanyama et al., 2022), sub-Saharan Africa (Khan & Yunus, 2023), and Bangladesh (Rahman et al., 2021; Talukder & Ahammed, 2020). Support Vector Machine was included for its strength on the mixed categorical-numeric, moderate-dimensional feature sets typical of household survey data, and has performed competitively with Random Forest in comparable studies (Ndagijimana et al., 2023; Shen et al., 2023). A 2025 meta-analysis of eleven studies using DHS data across Bangladesh and sub-Saharan Africa found that ensemble and tree-based models such as Random Forest generally outperformed single linear models for stunting, wasting, and underweight prediction, which supports evaluating all four algorithms rather than committing to one in advance (Rao et al., 2025).
The proposed system will provide healthcare professionals with timely, accurate, and data-driven predictions, enabling early identification of children at risk of malnutrition and supporting informed intervention strategies. In addition, the system will present prediction results through a user-friendly interface, making it accessible to users with limited technical expertise.
## 3.3 Requirements Analysis
### 3.3.1 Introduction
Requirements analysis is a critical phase in system development that involves identifying and documenting the needs and expectations of users and stakeholders. It provides a clear understanding of what the system should accomplish and establishes the foundation for designing and implementing an effective solution. In this study, the requirements analysis focuses on identifying the functional and non-functional requirements of the proposed Machine Learning-Based Decision Support System for predicting child malnutrition using the Central African Republic MICS6 dataset.
The proposed system is intended to support healthcare professionals, nutrition officers, researchers, and policy makers by providing accurate predictions of child malnutrition based on demographic, health, household, and environmental characteristics. Therefore, the system requirements were defined to ensure that the system is reliable, efficient, secure, user-friendly, and capable of supporting evidence-based decision-making.
### 3.3.2 Functional Requirements
Functional requirements describe the specific services and operations that the system must perform. They define how the system should respond to user inputs and how it processes information to produce meaningful outputs.
The proposed system shall provide the following functions:
1. User Authentication
The system shall allow authorized users to log into the application using a valid username and password before accessing system resources. Authentication ensures that only authorized personnel can access sensitive prediction information.
2. Child Information Management
The system shall enable users to enter child-related information required for prediction. These data include demographic, maternal, household, health, and environmental characteristics that influence child nutritional status.
Examples include:
Child age
Sex
Mother's education
Household wealth status
Drinking water source
Sanitation facility
Vitamin A supplementation
Breastfeeding status
3. Data Validation
Before prediction, the system shall validate all user inputs to ensure completeness, consistency, and correctness. Invalid or incomplete records shall generate appropriate error messages requesting users to correct the information.
4. Data Preprocessing
The system shall automatically preprocess the entered data by performing tasks such as:
Handling missing values
Encoding categorical variables
Normalizing numerical variables
Selecting relevant predictor variables
These preprocessing activities prepare the dataset for machine learning prediction.
5. Statistical Analysis
The system shall support descriptive statistical analysis to summarize the characteristics of the dataset. It shall generate:
Frequency distributions
Percentages
Summary statistics
Charts and graphs
The system shall also support inferential statistical analysis, including:
Chi-square tests
Binary Logistic Regression
These analyses will identify statistically significant determinants of child malnutrition.
6. Machine Learning Prediction
The system shall train and evaluate multiple supervised machine learning algorithms using the prepared dataset.
The algorithms include:
Logistic Regression
Decision Tree
Random Forest
Support Vector Machine (SVM)
The trained models shall predict whether a child is at risk of malnutrition based on the selected input variables.
7. Model Evaluation
The system shall compare the performance of different machine learning models using standard evaluation metrics such as:
Accuracy
Precision
Recall
F1-score
ROC-AUC
Confusion Matrix
The model with the best performance shall be selected as the final prediction model.
8. Prediction Results
After processing the input data, the system shall display prediction results indicating the nutritional status or risk level of the child.
The results shall include:
Predicted nutritional status
Prediction probability
Risk category
Recommended interpretation
9. Report Generation
The system shall allow users to generate prediction reports that can be viewed, printed, or exported for documentation and decision-making purposes.
10. Data Storage
The system shall securely store user information, prediction history, and generated reports in a database for future reference.
### 3.3.3 Non-Functional Requirements
Non-functional requirements describe the quality attributes of the proposed system. These requirements determine how efficiently and reliably the system performs its intended functions.
Performance
The system should generate a single prediction result within 3 seconds of receiving complete, validated input data on the minimum-specification hardware described in Section 3.3.5.
Reliability
The system should consistently produce accurate predictions using validated machine learning models, targeting at least 95% successful prediction requests without failure or interruption during normal operation.
Usability
The system should provide an intuitive and user-friendly interface that enables healthcare workers and researchers with limited technical expertise to use it effectively.
Security
The system should protect sensitive information through user authentication and secure data storage mechanisms.
Scalability
The system should be capable of handling at least 50,000 child records, consistent with the scale of a national MICS6 dataset, and support future updates without significantly affecting system performance.
Maintainability
The system should be modular and well documented to facilitate future maintenance, updates, and improvements.
Availability
The system should be accessible whenever authorized users need to perform nutritional assessment and prediction.
Compatibility
The system should operate correctly on commonly used web browsers and modern computer systems without requiring specialized hardware.
### 3.3.4 User Requirements
The proposed system is intended for different categories of users. Each category has specific responsibilities and interactions with the system.
### 3.3.5 System Requirements
The implementation of the proposed system requires both hardware and software resources.
Hardware Requirements
Software Requirements
## 3.4 Feasibility Study
### 3.4.1 Introduction
A feasibility study is conducted to determine whether a proposed system can be successfully developed and implemented. It evaluates the practicality of the project by examining technical, operational, economic, legal, and schedule aspects. Conducting a feasibility study helps identify potential challenges early and ensures that the proposed system can effectively meet user needs within the available resources.
For this study, the feasibility analysis was carried out to determine whether the proposed Machine Learning-Based Decision Support System for predicting child malnutrition using the Central African Republic MICS6 dataset can be implemented successfully.
### 3.4.2 Technical Feasibility
Technical feasibility assesses whether the required technologies, software, hardware, and technical expertise are available to develop and operate the proposed system.
The proposed system is technically feasible because it utilizes widely available open-source technologies and software tools. The machine learning models will be developed using Python, while data preprocessing and statistical analysis will be performed using libraries such as Pandas, NumPy, and Scikit-learn. Flask will be used to develop the web-based application, allowing users to interact with the prediction model through an intuitive graphical interface.
The system can operate on standard personal computers without requiring specialized hardware. The Central African Republic MICS6 dataset is already available in SPSS format and can be processed using Python after appropriate data preparation.
Furthermore, the researcher possesses the necessary knowledge in data science, machine learning, Python programming, statistical analysis, and web application development acquired through academic coursework and practical projects. Therefore, the technical requirements for developing the proposed system are available.
### 3.4.3 Operational Feasibility
Operational feasibility evaluates whether the proposed system will function effectively within its intended environment and whether users will be willing and able to use it.
The proposed system is designed to support healthcare workers, nutrition officers, researchers, and policy makers by providing a user-friendly platform for predicting child malnutrition. The system simplifies data analysis by automating preprocessing, prediction, and result generation, thereby reducing the need for advanced statistical expertise.
Because the system presents prediction results through an easy-to-understand interface, users can make informed decisions without directly interacting with complex machine learning algorithms. The system also supports evidence-based planning by identifying children at risk of malnutrition before severe conditions develop.
Therefore, the proposed system is considered operationally feasible.
### 3.4.4 Economic Feasibility
Economic feasibility examines whether the expected benefits of the proposed system justify the costs associated with its development and implementation.
The proposed system is economically feasible because it relies primarily on open-source software, eliminating the need for expensive software licenses. Python, Flask, Scikit-learn, Pandas, NumPy, Matplotlib, and SQLite are freely available and widely supported.
The primary costs associated with the project include:
Computer hardware
Internet connectivity
Electricity
Research expenses
Time required for system development and testing
Since the project is developed as part of an undergraduate research study, no additional commercial infrastructure or specialized equipment is required. The expected benefits, including improved prediction accuracy, faster analysis, and better decision support, outweigh the relatively low development costs.
### 3.4.5 Legal and Ethical Feasibility
Legal and ethical feasibility evaluates whether the proposed system complies with applicable laws, ethical standards, and data protection principles.
The proposed study utilizes secondary data obtained from the publicly available Central African Republic Multiple Indicator Cluster Survey (MICS6). The dataset contains anonymized records that do not reveal the identities of individual participants. Consequently, the use of the dataset presents minimal privacy risks.
The researcher will ensure that the data are used strictly for academic purposes and that all findings are reported responsibly without attempting to identify survey participants. Appropriate acknowledgment of UNICEF and the institutions responsible for the MICS programme will be provided in accordance with data usage guidelines.
Additionally, the developed prediction system will serve as a decision-support tool rather than replacing professional medical judgment. Healthcare professionals will remain responsible for interpreting prediction results and making final clinical decisions.
### 3.4.6 Schedule Feasibility
Schedule feasibility assesses whether the proposed system can be completed within the available project timeframe.
The project is considered schedule feasible because the researcher has already completed the problem identification, literature review, and dataset acquisition phases. The remaining activities include system design, implementation, model training, system testing, evaluation, and documentation.
A structured project schedule has been developed to guide the timely completion of each phase, ensuring that the dissertation requirements can be fulfilled within the allocated academic period.
### 3.4.7 Summary of Feasibility Analysis
Table 3.1: Summary of Feasibility Analysis
## 3.5 System Design
### 3.5.1 Introduction
System design is the process of transforming user requirements identified during system analysis into a detailed blueprint for system implementation. It specifies the architecture, components, workflows, and interactions that enable the system to perform its intended functions. A well-designed system ensures that functional and non-functional requirements are satisfied while maintaining efficiency, reliability, and scalability.
The proposed Machine Learning-Based Decision Support System (ML-DSS) was designed to assist healthcare professionals, nutrition officers, researchers, and policy makers in predicting child malnutrition using data from the Central African Republic Multiple Indicator Cluster Survey (MICS6). The system integrates statistical analysis and supervised machine learning techniques to generate prediction results that support evidence-based decision-making.
The design of the proposed system consists of the following components:
System Architecture
Use Case Diagram
Activity Diagram
Sequence Diagram
Data Flow Diagram (Context Diagram)
Data Flow Diagram (Level 1)
Machine Learning Pipeline
Decision Support Workflow
User Interface Design
Each component describes a different aspect of the proposed system and collectively provides a comprehensive blueprint for implementation.
### 3.5.2 System Architecture
The system architecture illustrates the overall structure of the proposed machine learning-based decision support system and shows how different components interact to produce prediction results.
The proposed architecture consists of five major components:
User Interface
Allows healthcare workers, nutrition officers, researchers, and administrators to interact with the system by entering child information and viewing prediction results.
Application Layer
Handles user authentication, data validation, preprocessing, and communication between the interface and the machine learning models.
Machine Learning Engine
Implements Logistic Regression, Decision Tree, Random Forest, and Support Vector Machine algorithms.
Trains, evaluates, and selects the best-performing prediction model.
Data Layer
Stores the MICS6 dataset, processed data, trained models, prediction history, and generated reports in a SQLite database, which is sufficient for the single-instance, moderate-concurrency deployment scope of this study; a networked engine such as MySQL would only be warranted if the system were later scaled to concurrent multi-facility use.
Output Layer
Displays prediction results, model performance metrics, reports, and recommendations for decision-making.
The interaction among these components enables efficient processing of child health information, prediction of nutritional status, and presentation of results through a user-friendly interface.
Figure 3.1: Proposed System Architecture
### 3.5.3 Use Case Diagram
Introduction
A use case diagram is a Unified Modeling Language (UML) diagram that illustrates how different users interact with a system to achieve specific objectives. It identifies the actors that use the system and the services or functions available to them. Use case diagrams provide a high-level view of the system's functionality and help define the system boundaries.
For the proposed Machine Learning-Based Decision Support System, the use case diagram illustrates the interactions between system users and the main functions provided by the application. The system is intended to support healthcare professionals, nutrition officers, researchers, and system administrators in predicting child malnutrition and managing system operations.
Actors
The proposed system consists of four primary actors.
Administrator
The administrator is responsible for managing the overall system. The administrator authenticates users, manages system settings, maintains the database, and monitors system performance.
The administrator can:
Log into the system
Manage user accounts
View prediction history
Manage datasets
Update machine learning models
Generate reports
Healthcare Worker
Healthcare workers are the primary users of the system. They enter child information, request predictions, and use the prediction results to support nutritional assessment.
Healthcare workers can:
Log in
Enter child information
Validate data
Request prediction
View prediction results
Generate reports
Nutrition Officer
Nutrition officers use the system to monitor nutritional trends and support intervention planning.
They can:
Log in
View prediction reports
Analyze prediction statistics
Export reports
Researcher
Researchers evaluate model performance and analyse prediction outcomes for research purposes.
Researchers can:
Log in
Upload datasets
Train machine learning models
Compare algorithm performance
View evaluation metrics
Export analytical reports
System Use Cases
The proposed system provides the following major use cases:
User Login
Manage Users
Enter Child Information
Validate Input Data
Preprocess Dataset
Train Machine Learning Models
Predict Child Malnutrition
Evaluate Model Performance
Generate Reports
View Prediction History
Export Results
Logout
These use cases represent the main functionalities required to support child malnutrition prediction using machine learning techniques.
Description of the Use Case Diagram
The use case diagram illustrates how each actor interacts with the proposed system. Healthcare workers primarily use the system for entering child information and obtaining prediction results. Nutrition officers focus on reviewing reports and analysing nutritional trends. Researchers are responsible for model training, evaluation, and exporting analytical results. The administrator oversees user management, dataset management, and overall system maintenance.
The interactions among these actors ensure that the system supports both operational use and research activities while maintaining secure access through user authentication.
Figure 3.2: Use Case Diagram
### 3.5.4 Activity Diagram
Introduction
An activity diagram is a Unified Modeling Language (UML) behavioral diagram that illustrates the sequence of activities performed within a system to accomplish a specific task. It describes the workflow of business processes by showing how activities are connected through decision points, sequential operations, and parallel processes. Activity diagrams help stakeholders understand how information flows through the system and how different operations interact during execution.
In the proposed Machine Learning-Based Decision Support System, the activity diagram describes the complete process followed when a user predicts child malnutrition. It begins with user authentication, continues through data entry and preprocessing, executes the machine learning prediction model, and finally presents the prediction results and recommendations to the user.
Workflow Description
The prediction process consists of the following activities:
Step 1: User Login
The user accesses the system by entering valid login credentials. The system authenticates the user before granting access to the prediction dashboard.
Step 2: Enter Child Information
After successful authentication, the user enters the child's demographic, health, maternal, household, and environmental information into the prediction form.
Examples include:
Child age
Child sex
Mother's education
Household wealth index
Drinking water source
Sanitation facility
Vitamin A supplementation
Step 3: Validate Data
The system checks whether all required information has been entered correctly.
If any required information is missing or invalid, the system prompts the user to correct the data before continuing.
Step 4: Data Preprocessing
After successful validation, the system automatically prepares the data for prediction using the same preprocessing operations defined as a functional requirement in Section 3.3.2 (missing-value handling, categorical encoding, numerical scaling, and predictor selection), applied here to the specific child record just entered rather than to the full dataset.
Step 5: Machine Learning Prediction
The processed data are submitted to the trained machine learning model.
The system applies the selected prediction model to estimate whether the child is likely to be malnourished.
Step 6: Generate Prediction Results
The system displays:
Predicted nutritional status
Risk level
Prediction probability
Recommendation for intervention
Step 7: Save Prediction
The prediction result is stored in the system for reporting and future reference.
Step 8: Logout
After completing the prediction process, the user logs out of the system, ending the session.
Description of the Activity Diagram
The activity diagram illustrates a logical sequence of operations beginning with user authentication and ending with logout. Decision nodes are included during authentication and data validation to ensure that only valid users and complete records proceed to the prediction stage. The preprocessing and machine learning stages operate automatically without requiring user intervention, improving efficiency and minimizing human error. The workflow concludes with the presentation of prediction results and storage of the prediction record in the database.
Figure 3.3: Activity Diagram
### 3.5.5 Sequence Diagram
Introduction
A sequence diagram is a behavioral UML diagram that illustrates how different components of a system interact over time to accomplish a specific task. Unlike the activity diagram, which focuses on workflow, the sequence diagram emphasizes the order in which messages are exchanged between system components.
In the proposed Machine Learning-Based Decision Support System, the sequence diagram illustrates the communication between the user, the web application, the machine learning engine, and the database during the prediction of child malnutrition. It demonstrates how user requests are processed, how the machine learning model generates predictions, and how results are returned to the user.
Participants
The sequence diagram consists of four major participants.
User
The user initiates the prediction process by logging into the system, entering child information, and requesting a prediction. After processing is complete, the user receives the prediction results.
Web Application
The web application serves as the interface between the user and the machine learning engine. It validates user input, coordinates system processes, communicates with the database, and presents the prediction results.
Machine Learning Engine
The machine learning engine performs data preprocessing, applies the trained prediction model, and generates the nutritional status prediction. It also computes the prediction probability, the model's estimated likelihood that the child is malnourished, which is used to derive the reported risk level.
Database
The database stores user information, processed datasets, trained machine learning models (or references to them), and prediction records. It provides the required information to the application and stores prediction results for reporting and future analysis.
Sequence of Interactions
The prediction process follows the sequence below:
Step 1: User Authentication
The user enters login credentials into the web application.
The application verifies the credentials with the database.
If authentication is successful, access to the prediction dashboard is granted.
Step 2: Data Entry
The user enters child information required for prediction.
The web application validates the completeness and correctness of the entered data.
Step 3: Data Preprocessing
The validated information is forwarded to the machine learning engine.
The engine applies the same preprocessing operations described in Section 3.3.2 and illustrated in Section 3.5.4 (Step 4) to the single incoming record: data cleaning, categorical encoding, feature selection, and normalization.
Step 4: Prediction
The processed data are passed to the trained prediction model.
The machine learning engine predicts whether the child is likely to be malnourished.
Step 5: Return Prediction
The prediction result is returned to the web application.
The application formats the result for presentation.
Step 6: Save Prediction
The prediction and relevant information are stored in the database for future reporting.
Step 7: Display Results
The web application presents the prediction result, risk level, and recommendations to the user.
Description of the Sequence Diagram
The sequence diagram illustrates the chronological exchange of messages among the four system components. The user initiates the prediction request through the web application, which validates the input and communicates with the machine learning engine. The machine learning engine preprocesses the data, applies the trained prediction model, and returns the prediction results. The application stores the prediction in the database before displaying the results to the user. This interaction ensures efficient processing while maintaining data integrity and supporting evidence-based decision-making.
Figure 3.4: Sequence Diagram
### 3.5.6 Data Flow Diagram (Context Diagram)
Introduction
A Data Flow Diagram (DFD) is a graphical representation of how data move through a system. It illustrates the sources of data, the processes that transform the data, the data stores, and the outputs generated by the system. Unlike UML diagrams, which emphasize system behavior and interactions, DFDs focus on the movement of information between different components.
The Context Diagram, also referred to as DFD Level 0, provides a high-level overview of the proposed Machine Learning-Based Decision Support System by representing the entire application as a single process and showing how external entities interact with it.
External Entities
The context diagram consists of the following external entities:
User
Provides child information to the system and receives prediction results.
Administrator
Manages users, updates system configurations, monitors prediction records, and generates reports.
Main Process
The proposed system is represented by one central process:
Machine Learning-Based Decision Support System for Predicting Child Malnutrition
This process accepts child information, performs data validation and prediction, and generates prediction reports.
Data Flows
The major data flows include:
From User to System
Login information
Child demographic data
Household information
Health information
Prediction request
From System to User
Prediction results
Risk level
Recommendations
Reports
From Administrator to System
User management information
System updates
Dataset updates
From System to Administrator
System reports
User activity reports
Model performance reports
Description of the Context Diagram
The context diagram demonstrates that all user interactions occur through the proposed Machine Learning-Based Decision Support System. Users provide the required child information for prediction, while administrators manage system operations and monitor system performance. The system processes all incoming data, executes the prediction model, and returns prediction results and reports to the respective users.
Figure 3.5: Context Diagram (DFD Level 0)
### 3.5.7 Data Flow Diagram (Level 1)
Introduction
The Level 1 Data Flow Diagram (DFD Level 1) expands the Context Diagram by decomposing the proposed Machine Learning-Based Decision Support System into its major internal processes. It illustrates how data move between users, system processes, the database, and the machine learning engine during the prediction of child malnutrition.
Unlike the Context Diagram, which represents the entire system as a single process, the Level 1 DFD provides a detailed view of the internal operations that transform user input into prediction results.
Processes
The proposed system consists of six major processes.
Process 1: User Authentication
The authentication process verifies user credentials before granting access to the application. Valid users are redirected to the dashboard, while invalid users are denied access and prompted to re-enter their login information.
Input:
Username
Password
Output:
Access granted
Access denied
Process 2: Child Data Entry
After authentication, the user enters child information into the prediction form.
The information includes:
Child characteristics
Maternal characteristics
Household characteristics
Health indicators
Environmental factors
These data serve as input for statistical analysis and machine learning prediction.
Process 3: Data Validation and Preprocessing
The system validates the entered information and prepares it for prediction.
The preprocessing stage performs the following operations:
Missing value handling
Data cleaning
Encoding categorical variables
Feature selection
Data transformation
The processed dataset is then forwarded to the machine learning engine.
Process 4: Machine Learning Prediction
The prediction engine applies the trained machine learning model to the processed data.
The system evaluates the input variables and predicts whether the child is at risk of malnutrition.
The selected prediction model may be one of the following:
Logistic Regression
Decision Tree
Random Forest
Support Vector Machine
Process 5: Report Generation
After prediction, the system generates reports summarizing:
Predicted nutritional status
Risk level
Model prediction
Recommendations
Reports may be viewed on-screen or exported for documentation.
Process 6: Data Storage
The system stores:
User accounts
Prediction history
Generated reports
Trained machine learning model (or model reference)
The stored information supports future analysis and reporting.
Data Stores
The proposed system contains three primary data stores.
D1 – User Database
Stores:
User accounts
Login credentials
User roles
D2 – Child Dataset
Stores:
Central African Republic MICS6 dataset
Processed datasets
Predictor variables
D3 – Prediction Records
Stores:
Prediction history
Generated reports
Model evaluation results
Description of the Level 1 DFD
The Level 1 Data Flow Diagram demonstrates the detailed flow of information through the proposed system. User credentials are first verified during authentication before allowing access to the application. Child information entered by the user undergoes validation and preprocessing before being submitted to the machine learning engine. The prediction model analyzes the processed data and generates prediction results, which are presented to the user and stored in the database for future reporting and analysis. This workflow ensures secure, accurate, and efficient prediction of child malnutrition.
Figure 3.6: Data Flow Diagram (Level 1)
### 3.5.8 Machine Learning Pipeline
Introduction
The Machine Learning Pipeline illustrates the sequence of activities involved in transforming raw survey data into a trained prediction model capable of identifying children at risk of malnutrition. The pipeline ensures that data are systematically prepared, analysed, and evaluated before deployment within the decision support system.
The proposed pipeline follows standard machine learning practices and is adapted to the Central African Republic MICS6 dataset used in this study.
Pipeline Stages
The pipeline consists of the following stages:
Data Collection
The system uses the Central African Republic MICS6 Child Dataset, which contains demographic, socioeconomic, maternal, health, nutrition, and environmental variables relevant to child malnutrition.
Data Preprocessing
The collected data are prepared using the same categories of operation defined as functional requirements in Section 3.3.2: cleaning inconsistent records, handling missing values, encoding categorical variables, scaling numerical variables where required, and selecting predictor variables. Here, these operations are applied once to the full MICS6 dataset prior to model training, rather than to a single record at prediction time.
Exploratory Data Analysis
The prepared dataset is explored through descriptive statistics and visualizations to understand the distribution of variables and identify potential relationships.
Statistical Analysis
The system performs:
Frequency analysis
Cross-tabulations
Chi-square tests
Binary Logistic Regression
These analyses identify statistically significant determinants of child malnutrition.
Machine Learning Model Training
The processed dataset is divided into training and testing subsets.
The following supervised learning algorithms are trained:
Logistic Regression
Decision Tree
Random Forest
Support Vector Machine
Model Evaluation
The trained models are evaluated using:
Accuracy
Precision
Recall
F1-score
ROC-AUC
Confusion Matrix
The best-performing model is selected for prediction.
Prediction
The selected model predicts whether a child is at risk of malnutrition based on the entered characteristics.
Decision Support
Prediction results are presented to users through the web application to support nutritional assessment and evidence-based decision-making.
Description of the Machine Learning Pipeline
The machine learning pipeline provides a structured framework for transforming raw MICS6 survey data into meaningful prediction results. Each stage builds upon the previous one, ensuring that only validated and properly processed data are used for model training and prediction. This systematic approach improves model reliability and supports accurate decision-making.
Figure 3.7: Machine Learning Pipeline
### 3.5.9 User Interface Design
This section presents the graphical user interface (GUI) of the proposed Machine Learning-Based Decision Support System. The interface is designed to be simple, intuitive, and user-friendly, enabling healthcare workers and nutrition officers to perform child malnutrition prediction efficiently. The system consists of four main interfaces: the login screen, dashboard, prediction form, and prediction results page. These interfaces support secure access, data entry, prediction, visualization of results, and report generation, thereby enhancing usability and supporting evidence-based decision-making.
Figure 3.8: User Interface Mockups
Description of Figure 3.8
Figure 3.8 illustrates the main interfaces of the proposed system:
Login Screen: Allows authorized users to securely access the system.
Dashboard: Displays system statistics, navigation menus, and recent prediction activities.
Prediction Form: Enables users to enter child demographic, health, household, and nutritional information required for prediction.
Prediction Results: Presents the predicted malnutrition risk, probability score, and recommendations, with options to download reports or return to the dashboard
## 3.6 Chapter Summary
This chapter presented the system analysis and design of the proposed Machine Learning-Based Decision Support System for predicting child malnutrition among children under five years of age using the Central African Republic MICS6 dataset. The chapter began by analysing the existing methods used to assess child malnutrition, identifying their limitations, and justifying the need for an intelligent machine learning-based approach. It then defined the functional and non-functional requirements, user requirements, and hardware and software requirements necessary for the successful development of the proposed system.
The chapter further evaluated the feasibility of implementing the proposed system from technical, operational, economic, legal, ethical, and schedule perspectives, demonstrating that the project is practical and achievable using available resources and open-source technologies. In addition, the system design was presented through a series of diagrams, including the system architecture, use case diagram, activity diagram, sequence diagram, context diagram, Level 1 data flow diagram, machine learning pipeline, and user interface design. These design models describe the structure, functionality, workflows, and interactions within the proposed decision support system and provide a clear blueprint for its implementation.
REFERENCES
Bitew, F. H., Sparks, C. S., & Nyarko, S. H. (2022). Machine learning algorithms for predicting undernutrition among under-five children in Ethiopia. Public Health Nutrition, 25(2), 269–280. https://doi.org/10.1017/S1368980021004262
Chilyabanyama, O. N., Chilengi, R., Simuyandi, M., Chisenga, C. C., Chirwa, M., Hamusonde, K., Saroj, R. K., Iqbal, N. T., Ngaruye, I., & Bosomprah, S. (2022). Performance of machine learning classifiers in classifying stunting among under-five children in Zambia. Children, 9(7), Article 1082. https://doi.org/10.3390/children9071082
Khan, M. N. A., & Yunus, R. M. (2023). A hybrid ensemble approach to accelerate the classification accuracy for predicting malnutrition among under-five children in sub-Saharan African countries. Nutrition, 108, Article 111947. https://doi.org/10.1016/j.nut.2022.111947
Ndagijimana, S., Kabano, I. H., Masabo, E., & Ntaganda, J. M. (2023). Prediction of stunting among under-5 children in Rwanda using machine learning techniques. Journal of Preventive Medicine and Public Health, 56(1), 41–49. https://doi.org/10.3961/jpmph.22.388
Rahman, S. M. J., Ahmed, N. A. M. F., Abedin, M. M., Ahammed, B., Ali, M., Rahman, M. J., & Maniruzzaman, M. (2021). Investigate the risk factors of stunting, wasting, and underweight among under-five Bangladeshi children and its prediction based on machine learning approach. PLOS ONE, 16(6), Article e0253172. https://doi.org/10.1371/journal.pone.0253172
Rao, B., Rashid, M., Hasan, M. G., & Thunga, G. (2025). Machine learning in predicting child malnutrition: A meta-analysis of demographic and health surveys data. International Journal of Environmental Research and Public Health, 22(3), Article 449. https://doi.org/10.3390/ijerph22030449
Shen, H., Zhao, H., & Jiang, Y. (2023). Machine learning algorithms for predicting stunting among under-five children in Papua New Guinea. Children, 10(10), Article 1638. https://doi.org/10.3390/children10101638
Sommerville, I. (2016). Software engineering (10th ed.). Pearson Education.
Talukder, A., & Ahammed, B. (2020). Machine learning algorithms for predicting malnutrition among under-five children in Bangladesh. Nutrition, 78, Article 110861. https://doi.org/10.1016/j.nut.2020.110861
UNICEF. (2023). UNICEF-WHO-The World Bank: Joint child malnutrition estimates (JME)—Levels and trends—2023 edition. UNICEF.
UNICEF. (n.d.). Multiple Indicator Cluster Surveys. Retrieved August 9, 2026, from https://mics.unicef.org/
World Health Organization. (2006). WHO child growth standards: Length/height-for-age, weight-for-age, weight-for-length, weight-for-height and body mass index-for-age: Methods and development. World Health Organization.

| User | Responsibilities |
| --- | --- |
| Administrator | Manage users, monitor system activities, maintain the database, update machine learning models. |
| Healthcare Worker | Enter child information, generate predictions, view reports, assist caregivers. |
| Nutrition Officer | Analyze prediction reports, monitor malnutrition trends, support intervention planning. |
| Researcher | Analyze prediction outcomes, evaluate model performance, conduct further research. |

| Component | Minimum Specification |
| --- | --- |
| Processor | Intel Core i5 or higher |
| RAM | 8 GB |
| Storage | 256 GB SSD |
| Internet | Stable internet connection |
| Display | 1366 × 768 resolution or higher |

| Software | Purpose |
| --- | --- |
| Windows 10/11 | Operating System |
| Python 3.x | Programming language |
| Jupyter Notebook / VS Code | Development environment |
| Flask | Web framework |
| Pandas | Data manipulation |
| NumPy | Numerical computation |
| Scikit-learn | Machine learning |
| Matplotlib | Visualization |
| Joblib | Model serialization |
| HTML/CSS/Bootstrap | User Interface |
| SQLite | Database management |

| Feasibility Aspect | Assessment | Justification |
| --- | --- | --- |
| Technical | Feasible | Open-source tools, available dataset, and required technical skills are available. |
| Operational | Feasible | The system supports healthcare workers and decision-makers through an easy-to-use interface. |
| Economic | Feasible | Development costs are low because open-source software is used. |
| Legal & Ethical | Feasible | Uses anonymized secondary MICS data and complies with ethical research practices. |
| Schedule | Feasible | The project can be completed within the university research timeline. |
