import pandas as pd
from datetime import datetime, timedelta
import streamlit as st
from apify_client import ApifyClient
import gspread
from google.oauth2.service_account import Credentials
import os

# Google Sheets Auth
def get_gsheet_client():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_info(st.secrets["SERVICE_ACCOUNT_JSON"], scopes=scope)
    return gspread.authorize(creds)

# --- MAIN DISCOVERY FUNCTION ---
def run_ig_discovery(days_back: int, skip_if_scraped_hours: int = 8):
    log = []
    try:
        log.append(f"🔎 IG Discovery (Apify) — {days_back} days back, skip if scraped {skip_if_scraped_hours}h")
        cutoff_date = datetime.utcnow() - timedelta(days=days_back)
        scrape_cutoff = datetime.utcnow() - timedelta(hours=skip_if_scraped_hours)
        APIFY_TOKEN = st.secrets["APIFY_TOKEN"]

        # Load Google Sheet Profiles
        SHEET_NAME = st.secrets["GOOGLE_SHEET_NAME"]
        INPUT_TAB = "IG Input Pages"
        client = get_gsheet_client()
        sh = client.open(SHEET_NAME)
        ws_profiles = sh.worksheet(INPUT_TAB)
        profile_urls = [row[0] for row in ws_profiles.get_all_values()[1:] if row and row[0].startswith("https://")]
        hashtags = [
            "lpulife", "lpuplacements", "lovelyprofessionaluniversity",
            "lpuvlogs", "lifeatlpu", "lpu", "lpucampus", "lpuhostel"
        ]

        # Cache
        CACHE_FILE = "scraped_cache.csv"
        if os.path.exists(CACHE_FILE):
            scrape_cache = pd.read_csv(CACHE_FILE)
            scrape_cache["last_scraped"] = pd.to_datetime(scrape_cache["last_scraped"])
        else:
            scrape_cache = pd.DataFrame(columns=["type", "value", "last_scraped"])
        
        client_apify = ApifyClient(APIFY_TOKEN)

        def run_apify_scraper(direct_urls, search_type):
            run_input = {
                "directUrls": direct_urls if search_type == "user" else [],
                "hashtag": direct_urls[0].replace("#", "") if search_type == "hashtag" else "",
                "resultsType": "posts",
                "resultsLimit": 50,
                "searchType": search_type,
                "searchLimit": 1,
                "addParentData": True
            }
            actor = client_apify.actor("shu8hvrXbJbY3Eb9W")
            run = actor.call(run_input=run_input)
            return list(client_apify.dataset(run["defaultDatasetId"]).iterate_items())

        def should_scrape(source_type, value):
            recent = scrape_cache[
                (scrape_cache["type"] == source_type) &
                (scrape_cache["value"] == value)
            ]
            if recent.empty:
                return True
            return recent["last_scraped"].iloc[0] < scrape_cutoff

        profile_results, hashtag_results = [], []
        for url in profile_urls:
            if should_scrape("profile", url):
                try:
                    st.info(f"Scraping profile: {url}")
                    profile_results.extend(run_apify_scraper([url], "user"))
                    scrape_cache = scrape_cache[scrape_cache["value"] != url]
                    scrape_cache = pd.concat([scrape_cache, pd.DataFrame([{
                        "type": "profile", "value": url, "last_scraped": datetime.utcnow()
                    }])], ignore_index=True)
                except Exception as e:
                    st.warning(f"⚠️ Profile scrape failed: {url} — {e}")
            else:
                st.info(f"⏩ Skipped profile (already scraped): {url}")
        for tag in hashtags:
            tag_id = f"#{tag}"
            if should_scrape("hashtag", tag_id):
                try:
                    st.info(f"Scraping hashtag: {tag_id}")
                    hashtag_results.extend(run_apify_scraper([tag_id], "hashtag"))
                    scrape_cache = scrape_cache[scrape_cache["value"] != tag_id]
                    scrape_cache = pd.concat([scrape_cache, pd.DataFrame([{
                        "type": "hashtag", "value": tag_id, "last_scraped": datetime.utcnow()
                    }])], ignore_index=True)
                except Exception as e:
                    st.warning(f"⚠️ Hashtag scrape failed: {tag_id} — {e}")
            else:
                st.info(f"⏩ Skipped hashtag (already scraped): {tag_id}")

        def parse_apify_data(raw_items):
            rows = []
            for item in raw_items:
                try:
                    dt = datetime.fromisoformat(item.get("timestamp").replace("Z", ""))
                    if dt >= cutoff_date:
                        rows.append({
                            "Reel URL": item.get("url"),
                            "Username": item.get("ownerUsername"),
                            "Caption": item.get("caption"),
                            "Date": dt.date().isoformat(),
                            "Likes": item.get("likesCount", 0),
                            "Comments": item.get("commentsCount", 0),
                            "Views": item.get("videoPlayCount", 0),
                            "Assigned Type": "",
                            "Theme": "",
                            "Influencer Name": "",
                            "Tag Usernames": "",
                            "Commercials": "",
                            "Remarks": "",
                            "Followers": "",
                            "Platform": "Instagram",
                            "Email Address": "",
                            "Mobile Number": "",
                            "Registration Number": "",
                            "Type of Content": "",
                            "Points": "",
                            "Shortcode": "",
                            "ID": "",
                            "Type of Influencer": "",
                            "Account Status": "",
                            "Payment Status": "",
                            "Number of Reels": ""
                        })
                except Exception:
                    continue
            return pd.DataFrame(rows)

        df_profiles = parse_apify_data(profile_results)
        df_hashtags = parse_apify_data(hashtag_results)
        df_all = pd.concat([df_profiles, df_hashtags], ignore_index=True)
        df_all = df_all.drop_duplicates(subset=["Reel URL"]).reset_index(drop=True)

        def write_to_sheet(sheet_name, dataframe):
            try:
                sh.del_worksheet(sh.worksheet(sheet_name))
            except:
                pass
            worksheet = sh.add_worksheet(sheet_name, rows="1000", cols="30")
            worksheet.update([dataframe.columns.tolist()] + dataframe.fillna("").values.tolist())

        write_to_sheet("Discovered IG Reels", df_all)
        log.append(f"✅ {len(df_all)} new reels saved to 'Discovered IG Reels'. Token usage optimized.")

        # Save cache
        scrape_cache.to_csv("scraped_cache.csv", index=False)
    except Exception as e:
        log.append(f"❌ Error: {str(e)}")
    finally:
        for entry in log:
            st.write(entry)
