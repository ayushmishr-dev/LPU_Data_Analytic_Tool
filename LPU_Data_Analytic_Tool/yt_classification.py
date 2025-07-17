import pandas as pd
from datetime import datetime
import streamlit as st
import isodate
from googleapiclient.discovery import build
import gspread
from google.oauth2.service_account import Credentials

def get_gsheet_client():
    import json
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    info = json.loads(st.secrets["SERVICE_ACCOUNT_JSON"]) 
    creds = Credentials.from_service_account_info(info, scopes=scope)
    return gspread.authorize(creds)

def fetch_video_durations(video_ids, youtube):
    durations = {}
    for i in range(0, len(video_ids), 50):
        response = youtube.videos().list(
            part="contentDetails",
            id=",".join(video_ids[i:i+50])
        ).execute()
        for item in response.get("items", []):
            video_id = item["id"]
            duration_str = item["contentDetails"]["duration"]
            duration = isodate.parse_duration(duration_str).total_seconds()
            durations[video_id] = duration
    return durations

def run_yt_classification(days_back: int):
    log = []
    try:
        log.append("📊 Running YouTube Classification...")
        YOUTUBE_API_KEY = st.secrets["YOUTUBE_API_KEY"]
        youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)
        client = get_gsheet_client()
        sheet_name = st.secrets["GOOGLE_SHEET_NAME"]
        sh = client.open(sheet_name)
        df = pd.DataFrame(sh.worksheet("Discovered Videos").get_all_records())

        required_cols = ["Video URL", "Video Title", "Channel Name", "Publish Date", "Views", "Likes", "Comments", "Assigned Type"]
        for col in required_cols:
            if col not in df.columns:
                st.error(f"Missing column: {col}")
                return

        video_ids = [url.split("v=")[-1] for url in df["Video URL"]]
        durations = fetch_video_durations(video_ids, youtube)
        df["Seconds"] = df["Video URL"].apply(lambda url: durations.get(url.split("v=")[-1], 9999))
        df["IsShort"] = df["Seconds"] <= 60

        # --- Prepare Output DataFrames ---
        columns_student = ["S. No.", "Month", "Student Name", "Link", "Video Title", "Publish Date", "Channel", "Views", "Likes", "Comments", "Shares", "Commercials", "Theme"]
        columns_comm = ["S.No", "Month", "Influencer Name", "Instagram Reel/ Youtube shorts", "Video Title", "Publish Date", "Channel", "Views", "Likes", "Comments", "Total Engagement", "Remarks", "Commercials"]
        columns_noncomm = ["S.No", "Month", "Influencer Name", "Instagram Reel/ Youtube shorts", "Video Title", "Publish Date", "Channel", "Views", "Likes", "Comments", "Total Engagement"]
        columns_creatorverse = ["Link", "Caption", "Date", "Channel", "Views", "Likes", "Comments"]

        student_rows, comm_rows, noncomm_rows, creator_rows = [], [], [], []
        
        for i, row in df.iterrows():
            url, title, channel, date = row["Video URL"], row["Video Title"], row["Channel Name"], row["Publish Date"]
            views, likes, comments = row["Views"], row["Likes"], row["Comments"]
            assigned = str(row["Assigned Type"]).strip().lower()
            month = pd.to_datetime(date).strftime("%b")
            engagement = (int(likes) if pd.notnull(likes) else 0) + (int(comments) if pd.notnull(comments) else 0)

            if assigned == "student":
                student_rows.append([len(student_rows)+1, month, "", url, title, date, channel, views, likes, comments, "", "", ""])
            elif assigned == "influencer_commercial" and row["IsShort"]:
                comm_rows.append([len(comm_rows)+1, month, "", url, title, date, channel, views, likes, comments, engagement, row.get("Remarks", ""), row.get("Commercials", "")])
            elif assigned == "influencer_noncommercial" and row["IsShort"]:
                noncomm_rows.append([len(noncomm_rows)+1, month, "", url, title, date, channel, views, likes, comments, engagement])
            elif assigned == "creatorverse":
                creator_rows.append([url, title, date, channel, views, likes, comments])

        sheets_to_upload = [
            ("Student Youtube Video", columns_student, student_rows),
            ("Youtube Short with Commercials", columns_comm, comm_rows),
            ("Youtube Short without Commercials", columns_noncomm, noncomm_rows),
            ("CreatorVerse", columns_creatorverse, creator_rows)
        ]

        for name, columns, rows in sheets_to_upload:
            try:
                sh.del_worksheet(sh.worksheet(name))
            except:
                pass
            ws = sh.add_worksheet(title=name, rows="1000", cols="20")
            ws.update([columns] + rows)
            log.append(f"✅ Updated sheet: {name}")
        log.append("✅ All 4 sheets uploaded to 'YouTube Performance Report'")
    except Exception as e:
        log.append(f"❌ Error: {str(e)}")
    finally:
        for entry in log:
            st.write(entry)
