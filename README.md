# PiHealth Monitoring System

The PiHealth Monitoring System is designed to capture, store, and analyze patient health metrics and practitioner interactions in a healthcare environment.

## Overview

PiHealth Monitoring System provides a secure, traceable system for tracking patient vital signs and health assessments. The system leverages RFID authentication for practitioners to ensure secure data entry while maintaining comprehensive records of patient health metrics over time.

## Key Features

- **Secure Authentication**: RFID-based provider identification for traceable data entry
- **Comprehensive Health Tracking**: Captures vital signs including heart rate, blood pressure, temperature, and oxygen saturation
- **Health Assessment**: Automated evaluation of patient health status based on predefined thresholds
- **Real-time Display**: Physical computing system that connects to the database and displays patient assessments in real-time
- **Analytics & Reporting**: Generate insights on patient health trends, practitioner patterns, and intervention effectiveness
- **Real-time Decision Support**: Enables clinical staff to make informed decisions based on structured health data

## System Architecture

This project combines database design with physical computing systems:

### Database Component

The system is built around four core tables:

- **provider**: Stores practitioner information with RFID-based authentication
- **patient**: Maintains patient demographic and identification data
- **metrics**: Records vital signs and health measurements (heart rate, blood pressure, temperature, oxygen saturation)
- **assessment**: Stores evaluated health status (e.g., healthy/unhealthy) based on predefined thresholds

### Physical Computing Component

As part of the systems design integration, a physical computing device connects directly to the database to:
- Query patient assessment data in real-time
- Display current patient health status and vital signs
- Provide immediate visual feedback on patient assessments as they are recorded
- Serve as an on-site monitoring station for clinical environments

## Use Cases

- Chronic condition monitoring and long-term trend analysis
- Early warning systems for deteriorating patient health
- Patient health overview dashboards for clinical staff
- Predictive modeling for health risk classification
- Anomaly detection in patient vitals
- Practitioner performance and case volume analysis

## Analytics Capabilities

- Time-series tracking of patient vital signs
- Practitioner-specific input pattern analysis
- Frequency analysis of abnormal readings
- Trend visualization for patient health over time
- Identification of practitioners handling high volumes of critical cases
- Evaluation of intervention effectiveness

