# Smart Waste Classification System

An image classification system that uses machine learning to identify and categorize waste from images, with the goal of supporting automated waste segregation.

## Overview

Manual waste segregation is time-consuming and prone to human error. This project explores the use of computer vision and machine learning to automatically classify waste items into predefined categories.

## Objective

Build a machine learning model that:

* Accepts an image of a waste item
* Identifies its waste category
* Returns the predicted category with confidence
* Provides a simple interface for users to test images

## Dataset

The initial implementation will use a publicly available waste-image dataset such as **TrashNet**.

Expected categories include:

* Cardboard
* Glass
* Metal
* Paper
* Plastic
* Trash

## Approach

```text
Input Image
     ↓
Image Preprocessing
     ↓
Data Augmentation
     ↓
Pretrained CNN
     ↓
Model Training
     ↓
Classification
     ↓
Predicted Waste Category
```

The project will primarily explore **transfer learning**, using a pretrained computer-vision model and adapting it to the waste-classification task.

## Tech Stack

* Python
* PyTorch / Torchvision
* Scikit-Learn
* NumPy
* Flask
* React & Vite (Frontend)
* Docker & Docker Compose

## Project Structure

```text
smart-waste-classification/
│
├── data/
├── models/
├── src/
│   ├── preprocessing/
│   ├── models/
│   └── api.py
│
├── app/                  # React/Vite Frontend
├── tests/
├── pyproject.toml
├── compose.yaml          # Docker Compose configuration
└── README.md
```

## Team Workflow

Development will follow a collaborative Git workflow:

```text
Feature Branch
      ↓
Development
      ↓
Commit
      ↓
Pull Request
      ↓
Code Review
      ↓
Merge → main
```

Each major component will be developed in a separate feature branch to practice collaborative development, code review, merging, and conflict resolution.

## Current Status

✅ **Full-stack integration complete**

The data pipeline, model training logic, Flask backend API, and React frontend are implemented. The entire application can be launched locally for development and preview using Docker Compose.
