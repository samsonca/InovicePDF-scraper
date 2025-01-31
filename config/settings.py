import os

# SharePoint (Microsoft Teams) Configuration
SHAREPOINT_SITE = "https://rndesign.sharepoint.com/sites/RNDesign-AllTeamMembers-Finance-BlackFiles"
SHAREPOINT_FOLDER = "/Shared Documents/Documents/Finance - Black Files/Salefish Software"



# SharePoint Authentication (Use Environment Variables for Security)
CLIENT_ID = os.getenv("SHAREPOINT_CLIENT_ID", "your-client-id")
CLIENT_SECRET = os.getenv("SHAREPOINT_CLIENT_SECRET", "your-client-secret")

# Azure SQL Database Configuration
AZURE_DB_CONNECTION_STRING = os.getenv("AZURE_DB_CONNECTION", "DRIVER={ODBC Driver 17 for SQL Server};SERVER=your-server.database.windows.net;PORT=1433;DATABASE=your-database;UID=your-username;PWD=your-password")

# Logging Settings
LOGGING_LEVEL = os.getenv("LOGGING_LEVEL", "INFO")

# File Monitoring Settings
WATCH_FOLDER = os.getenv("WATCH_FOLDER", SHAREPOINT_FOLDER)
