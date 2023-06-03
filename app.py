from  flask import Flask,render_template,url_for,request
import numpy as np
import pandas as pd
# from scipy.stats import mode
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, confusion_matrix

app = Flask(__name__)

@app.route('/')
def login():
    return render_template('login.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/predict', methods=['POST'])
def predict():
    # %matplotlib inline

    DATA_PATH = "Data/Training.csv"
    data = pd.read_csv(DATA_PATH).dropna(axis = 1)
    
    # Checking whether the dataset is balanced or not
    disease_counts = data["prognosis"].value_counts()
    temp_df = pd.DataFrame({
        "Disease": disease_counts.index,
        "Counts": disease_counts.values
    })
    
    encoder = LabelEncoder()
    data["prognosis"] = encoder.fit_transform(data["prognosis"])

    X = data.iloc[:,:-1]
    y = data.iloc[:, -1]
    X_train, X_test, y_train, y_test =train_test_split(
    X, y, test_size = 0.2, random_state = 24)

    
    # Initializing Models
    models = {
        "Random Forest":RandomForestClassifier(random_state=18)
    }
    
    
    # Training and testing Random Forest Classifier
    rf_model = RandomForestClassifier(random_state=18)
    rf_model.fit(X_train, y_train)
    preds = rf_model.predict(X_test)
        
    final_rf_model = RandomForestClassifier(random_state=18)
    final_rf_model.fit(X, y)
    
    # Reading the test data
    test_data = pd.read_csv("Data/Testing.csv").dropna(axis=1)
    
    test_X = test_data.iloc[:, :-1]
    test_Y = encoder.transform(test_data.iloc[:, -1])
    
    symptoms = X.columns.values
 
    # Creating a symptom index dictionary to encode the
    # input symptoms into numerical form
    symptom_index = {}
    for index, value in enumerate(symptoms):
        symptom_index[value] = index
    
    data_dict = {
        "symptom_index":symptom_index,
        "predictions_classes":encoder.classes_
    }
    
    # Defining the Function
    # Input: string containing symptoms separated by commas
    # Output: Generated predictions by models
    def predictDisease(symptoms):
        symptoms = symptoms.split(",")
        
        # creating input data for the models
        input_data = [0] * len(data_dict["symptom_index"])
        for symptom in symptoms:
            symptom_transformed = "_".join([i.lower() for i in symptom.split(" ")])
            index = data_dict["symptom_index"][symptom_transformed]
            input_data[index] = 1
   
        input_data = np.array(input_data).reshape(1,-1)
        
        # generating individual outputs
        rf_prediction = data_dict["predictions_classes"][final_rf_model.predict(input_data)[0]]
        return rf_prediction
    #  
    # Testing the function
    result = predictDisease()
    return render_template('predict.html', prediction = result)

if __name__ == '__main__':
    app.run(host="127.0.0.1", port=8000, debug=True)