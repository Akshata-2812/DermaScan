# DermaScan – Real-Time Diagnosis and Disease Detection

"DermaScan" is an intelligent, real-time skin disease detection system designed to provide early diagnosis and increase accessibility to dermatological care. Built using deep learning and web technologies, DermaScan classifies skin diseases from images and offers detailed information including symptoms and causes. It also generates downloadable reports for easy medical reference.

---

## Project Overview

Skin diseases affect millions globally, yet timely and accurate diagnosis remains limited by access to specialists. DermaScan bridges this gap by using a trained Convolutional Neural Network (CNN) to analyze skin images and identify possible conditions. The system is implemented as a responsive web interface with functionality for image upload or capture, real-time disease prediction, result storage and downloadable medical reports.

---

## Features

- Deep learning-based image classification (8 skin disease classes + 3 skin types).
- Real-time prediction from uploaded or captured skin images.
- Confidence score display with symptoms and possible causes.
- Save history and download detailed PDF reports.
- User authentication and user-specific storage.

---

## Tech Stack

- Frontend: HTML, CSS, JavaScript
- Backend: Python, Flask
- Model Training: TensorFlow / Keras
- Storage: Local filesystem (user-specific folders)


---

## Dataset

The model was trained using a curated dataset of skin disease images from Kaggle, organized into separate folders per class.

Dataset Link: [Click here to access the dataset](https://drive.google.com/drive/folders/1BObtriJM0I019vd6GU3uCotZN9iwCre8?usp=sharing)

---

## Colab Notebooks

- Model Training and Augmentation:  
  [Google Colab Notebook](https://colab.research.google.com/drive/1ne2v6hgMf9FnR32C2hrDrgw29DN7JS2U?usp=sharing)

- Confusion Matrix & Evaluation:  
  [Google Colab Notebook](https://colab.research.google.com/drive/1qCcFoMKYmD7XqFp-vbGQDKVWOB1-14bl?usp=sharing)

---

## Innovation Readiness Level

DermaScan is currently at "IRL 7 – Implementation". The model has been fully trained and validated and the system has been integrated into a working, user-ready web platform.

---


## License

This project is developed for academic purposes. Please contact the author for reuse or deployment.

---

## Authors

Akshata Ravichandran - akshataravi.chandran@gmail.com

---

