from datetime import datetime, timezone

def get_token():


  # Corrected schedule dictionary
  schedule = {
      "monday": {
          "quato_folder": "acc1_quato_based",
          "project_folder": "p2"
      },
      "tuesday": {
          "quato_folder": "acc2_quato_based",
          "project_folder": "p2"
      },
      "wednesday": {  # Fixed spelling
          "quato_folder": "acc3_quato_based",
          "project_folder": "p2"
      },
      "thursday": {
          "quato_folder": "acc1_quato_based",
          "project_folder": "p2"
      },
      "friday": {
          "quato_folder": "acc2_quato_based",
          "project_folder": "p2"
      },
      "saturday": {
          "quato_folder": "acc3_quato_based",
          "project_folder": "p2"
      },
      "sunday": {
          "quato_folder": "acc2_quato_based",
          "project_folder": "p2"
      }
  }



  # Get today's day name (e.g., "monday", "tuesday")
  today = datetime.today().strftime("%A").lower()

  # Get quato_folder and project_folder based on today's schedule
  quato_folder = schedule[today]["quato_folder"]
  project_folder = schedule[today]["project_folder"]

  YT_TOKEN_FILE = rf"/{quato_folder}/{project_folder}/06_token.json"
  return YT_TOKEN_FILE
