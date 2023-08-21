import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.linear_model import LogisticRegression
from tkinter import Tk, Label, Button, Text, END, StringVar, ttk

# قراءة ملف CSV وتجهيز البيانات
data = pd.read_csv('data.csv')
encoder = LabelEncoder()
encoded_data = data.apply(lambda col: encoder.fit_transform(col))
X = encoded_data.drop('تصنيف التضاريس', axis=1)
y = encoded_data['تصنيف التضاريس']
X_train, _, y_train, _ = train_test_split(X, y, test_size=0.2, random_state=42)

# تدريب النموذج باستخدام الانحدار اللوجستي مع تنعيم L2
model = LogisticRegression(max_iter=1000)
model.fit(X_train, y_train)

# قائمة الفئات الممكنة والقيم المقابلة لها
possible_classes = encoder.classes_

# قائمة القيم الممكنة دون تشفير
label_texts = ["نسبة الماء:", "نسبة الرطوبة:", "درجة الحرارة:", "تربة:"]
possible_values = [data[label_text[:-1]].unique() for label_text in label_texts]

def classify_new_data():
    features = [feature_var.get() for feature_var in feature_vars]
    
    # تحويل القيم إلى معادلها المشفرة باستخدام قاموس
    features_encoded = [possible_values[i].tolist().index(value) for i, value in enumerate(features)]
    
    prediction = model.predict([features_encoded])
    class_index = int(prediction[0])
    predicted_class = possible_classes[class_index]
    result_text.config(state='normal')
    result_text.delete('1.0', END)
    result_text.insert(END, f'التصنيف: {predicted_class}')
    result_text.config(state='disabled')

# إعداد نافذة Tkinter
root = Tk()
root.title("تصنيف البيانات")

feature_vars = []

for i, text in enumerate(label_texts):
    label = Label(root, text=text)
    label.grid(row=i, column=0, padx=10, pady=10)
    
    feature_var = StringVar()
    feature_combo = ttk.Combobox(root, textvariable=feature_var)
    feature_combo.grid(row=i, column=1, padx=10, pady=10)
    
    # Remove unwanted characters and create a new list of cleaned values
    cleaned_values = [value.replace("'", "").replace("[", "").replace("]", "") for value in possible_values[i]]
    feature_combo['values'] = cleaned_values
    
    feature_vars.append(feature_var)

classify_button = Button(root, text="تصنيف", command=classify_new_data)
classify_button.grid(row=len(label_texts), columnspan=2, padx=10, pady=10)

result_text = Text(root, height=2, width=30, state='disabled')
result_text.grid(row=len(label_texts) + 1, columnspan=2, padx=10, pady=10)

root.mainloop()

