🏛️ e-Courts Case Tracker
Project Description
The e-Courts Case Tracker is a powerful Python-based web application designed to automate the process of tracking case listings in Indian District and High Courts. It provides a crucial service to legal professionals and litigants by eliminating the manual, time-consuming process of searching daily court schedules (known as cause lists).

The application focuses on two key features: proactive alerting and data management. It ensures users are instantly notified of upcoming hearings and provides convenient, formatted access to historical and current court data.

🎯 Key Features
Feature	Description
Next-Day Case Alerts	Users can input a specific case number and the system will check the upcoming day's cause lists. It provides a simple, instant notification if the case is scheduled for a hearing tomorrow.
Cause List Scraping	Automatically fetches and extracts the raw daily schedules (cause lists) from designated District Courts and High Courts.
PDF Generation	Converts the raw, complex cause list data into clean, standardized, and easily downloadable PDF documents for archival and offline viewing.
Scalable Backend	Built with Flask and utilizing SQLAlchemy for robust data management, ensuring all scraped data is securely stored and quickly searchable.

🛠️ Technology Stack
Component	Technology	Purpose
Web Framework	Python / Flask	The core framework for the web application and API endpoints.
Database ORM	SQLAlchemy / Flask-SQLAlchemy	Manages the database connection and defines the structure for storing cause list data.
Frontend	HTML / CSS / JavaScript	Provides a simple, user-friendly interface for searching and viewing alerts.
Scraping	Custom Python Libraries	Handles the fetching and parsing of data from various court portals.
