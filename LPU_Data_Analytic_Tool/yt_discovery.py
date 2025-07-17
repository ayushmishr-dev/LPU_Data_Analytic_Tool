import pandas as pd
from datetime import datetime, timedelta
import streamlit as st
from googleapiclient.discovery import build
import gspread
from google.oauth2.service_account import Credentials

def get_gsheet_client():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_info(st.secrets["SERVICE_ACCOUNT_JSON"], scopes=scope)
    return gspread.authorize(creds)

def run_yt_discovery(days_back: int):
    log = []
    try:
        log.append(f"🔎 Running YouTube Discovery for last {days_back} days...")

        # Auth YouTube
        YOUTUBE_API_KEY = st.secrets["YOUTUBE_API_KEY"]
        youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
        published_after = (datetime.utcnow() - timedelta(days=days_back)).isoformat("T") + "Z"
        
        # Keywords
        keywords = [
            '"Lovely Professional University"',
            '"LPU Campus Tour"',
            '"Life at LPU"',
            '"LPU Hostel Tour"',
            '"LPU Vlog"',
            '"LPU Student Review"',
            '"Why I chose LPU"',
            '"My Experience at LPU"',
            '"LPU Placement Story"',
            '"Studying at LPU"'
        ]

        # Search YouTube
        def search_youtube(keyword):
            results = []
            request = youtube.search().list(
                part="snippet",
                maxResults=25,
                q=keyword,
                type="video",
                order="relevance",
                publishedAfter=published_after
            )
            response = request.execute()
            for item in response["items"]:
                video_id = item["id"]["videoId"]
                video_url = f"https://www.youtube.com/watch?v={video_id}"
                snippet = item["snippet"]
                results.append({
                    "Video URL": video_url,
                    "Channel Name": snippet["channelTitle"],
                    "Video Title": snippet["title"],
                    "Publish Date": snippet["publishedAt"]
                })
            return results
        
        all_results = []
        for kw in keywords:
            all_results.extend(search_youtube(kw))
        
        df = pd.DataFrame(all_results).drop_duplicates(subset="Video URL")
        log.append(f"✅ Discovered {len(df)} unique videos.")

        # Stats
        def get_video_stats(video_ids):
            stats_data = []
            for i in range(0, len(video_ids), 50):
                request = youtube.videos().list(
                    part="statistics",
                    id=",".join(video_ids[i:i+50])
                )
                response = request.execute()
                for item in response["items"]:
                    stats = item.get("statistics", {})
                    stats_data.append({
                        "Video URL": f"https://www.youtube.com/watch?v={item['id']}",
                        "Views": int(stats.get("viewCount", 0)),
                        "Likes": int(stats.get("likeCount", 0)),
                        "Comments": int(stats.get("commentCount", 0))
                    })
            return pd.DataFrame(stats_data)

        video_ids = [url.split("v=")[-1] for url in df["Video URL"]]
        stats_df = get_video_stats(video_ids)
        df_final = df.merge(stats_df, on="Video URL", how="left")
        df_final["Assigned Type"] = ""
        df_final["Remarks"] = ""

        # Google Sheets
        client = get_gsheet_client()
        sheet_name = st.secrets["GOOGLE_SHEET_NAME"]
        sh = client.open(sheet_name)
        try:
            worksheet = sh.worksheet("Discovered Videos")
            sh.del_worksheet(worksheet)
        except Exception:
            pass
        worksheet = sh.add_worksheet(title="Discovered Videos", rows="1000", cols="20")
        worksheet.update([df_final.columns.tolist()] + df_final.values.tolist())
        log.append("✅ Sheet updated: 'YouTube Performance Report' > 'Discovered Videos'")

    except Exception as e:
        log.append(f"❌ Error: {str(e)}")
    finally:
        for entry in log:
            st.write(entry)
