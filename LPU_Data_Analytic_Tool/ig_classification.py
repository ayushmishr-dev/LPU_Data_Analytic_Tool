import pandas as pd
import streamlit as st
import gspread
from google.oauth2.service_account import Credentials

def get_gsheet_client():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    info = json.loads(st.secrets["SERVICE_ACCOUNT_JSON"])  
    creds = Credentials.from_service_account_info(info, scopes=scope)
    return gspread.authorize(creds)

def run_ig_classification():
    log = []
    try:
        log.append("🏷️ Running IG Classification/Segregation...")
        client = get_gsheet_client()
        sheet_name = st.secrets["GOOGLE_SHEET_NAME"]
        sh = client.open(sheet_name)
        df = pd.DataFrame(sh.worksheet("Discovered IG Reels").get_all_records())
        assignment_col = None
        for col in df.columns:
            if col.strip().lower() in ["assignment type", "assigned type"]:
                assignment_col = col
                break
        if assignment_col is None:
            st.error("No 'Assignment type' or 'Assigned Type' column found in your sheet!")
            return

        # --- STEP 4: Define Output Column Structures and Mapping (ALL SHEETS) ---
        sheet_columns = {
            "Influencer Reel with Commercials": [
                "S.No", "Month", "Influencer Name", "Theme", "Instagram Reel",
                "Views", "Likes", "Comments", "Shares", "Total Engagement", "Commercials", "Platform"
            ],
            "Influencer Reel without Commercials": [
                "S.No", "Month", "Influencer Name", "ID", "Instagram Reel",
                "Views", "Likes", "Comments", "Shares", "Total Engagement", "Platform"
            ],
            "Chancellor Sir PR": [
                "S.No", "Month", "Channel name", "Followers", "Live Reel Link", "Views", "Likes", "Comments",
                "share", "Amount to Be Paid (INR)", "Date Posted", "Payment Status", "Platform"
            ],
            "Campus Reel": [
                "S.No", "Month", "Account Name", "ID", "Link", "views", "Likes", "Comments", "Shares", "Platform"
            ],
            "Meme Marketing": [
                "S.No", "Month", "Page Name", "link", "Live Reel Link", "Views", "Likes", "Comments", "Shares", "followers", "Platform"
            ],
            "Student Profiles": [
                "Sr.No", "Name", "Platform", "Profile/Channel Link", "Followers", "Number of Reels", "Account Status"
            ],
            "LPU Confess": [
                "S.No", "Link", "Amount", "Status", "Platform"
            ],
            "Long Term Promotion": [
                "Sr.No", "Name", "Platform", "Profile/Channel Link", "Followers", "Number of Reels", "Commercials Per Reel"
            ],
            "Shoutout": [
                "S No.", "Month", "ShortCode", "ID", "Video Link", "Views", "Likes", "Comments", "Shares", "Platform"
            ],
            "InstaConfluence": [
                "S.No", "Month", "Name", "Platform", "Link", "Views", "Likes", "Comments", "Share", "Followers"
            ],
            "Diwali Competition": [
                "Timestamp", "Month", "Email Address", "Name", "Registration Number", "Mobile Number", "Type of Content", "Link", "From where you come to know", "shortcode", "ID", "Plays", "Likes", "Comments", "Shares", "Points", "Platform"
            ],
            "Olympics": [
                "S.No", "Month", "Influencer's Name", "Platform", "Link", "Views", "Likes", "Comments", "Share", "Type of Influencer", "Shortcode", "id"
            ],
            "Digital Star": [
                "Timestamp", "Month", "Email Address", "Name", "Registration Number", "Mobile Number", "Themes", "Type of Content", "Link (Reel or Post on Instagram)", "shortcode", "ID", "Plays", "Likes", "Comments", "Shares", "Platform"
            ],
            "Outcampus": [
                "S.No", "Month", "Link", "shortcode", "ID", "Views", "Likes", "Comment", "Share", "Platform"
            ]
        }
        assignment_to_sheet_map = {
            "influencer_commercial": "Influencer Reel with Commercials",
            "influencer_noncommercial": "Influencer Reel without Commercials",
            "chancellor_pr": "Chancellor Sir PR",
            "meme_marketing": "Meme Marketing",
            "campus_reel": "Campus Reel",
            "student_profile": "Student Profiles",
            "lpu_confess": "LPU Confess",
            "long_term_promotion": "Long Term Promotion",
            "shoutout": "Shoutout",
            "instaconfluence": "InstaConfluence",
            "diwali_competition": "Diwali Competition",
            "olympics": "Olympics",
            "digital_star": "Digital Star",
            "outcampus": "Outcampus"
        }
        df["Assigned Sheet"] = df[assignment_col].apply(lambda x: assignment_to_sheet_map.get(str(x).strip().lower(), None))

        def fill_output_row(sheet, row, idx):
            out = dict()
            # 1. Influencer Reel with Commercials
            if sheet == "Influencer Reel with Commercials":
                out["S.No"] = idx+1
                out["Month"] = pd.to_datetime(row.get("Date", ""), errors="coerce").strftime("%B-%Y") if row.get("Date") else ""
                out["Influencer Name"] = row.get("Username", "")
                out["Theme"] = row.get("Theme", "")
                out["Instagram Reel"] = row.get("Reel URL", "")
                out["Views"] = row.get("Views", "")
                out["Likes"] = row.get("Likes", "")
                out["Comments"] = row.get("Comments", "")
                out["Shares"] = row.get("Shares", "")
                try:
                    likes = int(row.get("Likes",0)) if str(row.get("Likes",0)).isdigit() else 0
                    comments = int(row.get("Comments",0)) if str(row.get("Comments",0)).isdigit() else 0
                    shares = int(row.get("Shares",0)) if str(row.get("Shares",0)).isdigit() else 0
                    out["Total Engagement"] = likes + comments + shares
                except:
                    out["Total Engagement"] = ""
                out["Commercials"] = row.get("Commercials", "")
                out["Platform"] = "Instagram"
            # 2. Influencer Reel without Commercials
            elif sheet == "Influencer Reel without Commercials":
                out["S.No"] = idx+1
                out["Month"] = pd.to_datetime(row.get("Date", ""), errors="coerce").strftime("%B-%Y") if row.get("Date") else ""
                out["Influencer Name"] = row.get("Username", "")
                out["ID"] = row.get("ID", "")
                out["Instagram Reel"] = row.get("Reel URL", "")
                out["Views"] = row.get("Views", "")
                out["Likes"] = row.get("Likes", "")
                out["Comments"] = row.get("Comments", "")
                out["Shares"] = row.get("Shares", "")
                try:
                    likes = int(row.get("Likes",0)) if str(row.get("Likes",0)).isdigit() else 0
                    comments = int(row.get("Comments",0)) if str(row.get("Comments",0)).isdigit() else 0
                    shares = int(row.get("Shares",0)) if str(row.get("Shares",0)).isdigit() else 0
                    out["Total Engagement"] = likes + comments + shares
                except:
                    out["Total Engagement"] = ""
                out["Platform"] = "Instagram"
            # 3. Chancellor Sir PR
            elif sheet == "Chancellor Sir PR":
                out["S.No"] = idx+1
                out["Month"] = pd.to_datetime(row.get("Date", ""), errors="coerce").strftime("%B-%Y") if row.get("Date") else ""
                out["Channel name"] = row.get("Username", "")
                out["Followers"] = row.get("Followers", "")
                out["Live Reel Link"] = row.get("Reel URL", "")
                out["Views"] = row.get("Views", "")
                out["Likes"] = row.get("Likes", "")
                out["Comments"] = row.get("Comments", "")
                out["share"] = row.get("Shares", "")
                out["Amount to Be Paid (INR)"] = row.get("Amount", "")
                out["Date Posted"] = row.get("Date", "")
                out["Payment Status"] = row.get("Payment Status", "")
                out["Platform"] = "Instagram"
            # 4. Campus Reel
            elif sheet == "Campus Reel":
                out["S.No"] = idx+1
                out["Month"] = pd.to_datetime(row.get("Date", ""), errors="coerce").strftime("%B-%Y") if row.get("Date") else ""
                out["Account Name"] = row.get("Username", "")
                out["ID"] = row.get("ID", "")
                out["Link"] = row.get("Reel URL", "")
                out["views"] = row.get("Views", "")
                out["Likes"] = row.get("Likes", "")
                out["Comments"] = row.get("Comments", "")
                out["Shares"] = row.get("Shares", "")
                out["Platform"] = "Instagram"
            # 5. Meme Marketing
            elif sheet == "Meme Marketing":
                out["S.No"] = idx+1
                out["Month"] = pd.to_datetime(row.get("Date", ""), errors="coerce").strftime("%B-%Y") if row.get("Date") else ""
                out["Page Name"] = row.get("Username", "")
                out["link"] = row.get("Reel URL", "")
                out["Live Reel Link"] = row.get("Reel URL", "")
                out["Views"] = row.get("Views", "")
                out["Likes"] = row.get("Likes", "")
                out["Comments"] = row.get("Comments", "")
                out["Shares"] = row.get("Shares", "")
                out["followers"] = row.get("Followers", "")
                out["Platform"] = "Instagram"
            # 6. Student Profiles
            elif sheet == "Student Profiles":
                out["Sr.No"] = idx+1
                out["Name"] = row.get("Username", "")
                out["Platform"] = "Instagram"
                out["Profile/Channel Link"] = row.get("Reel URL", "")
                out["Followers"] = row.get("Followers", "")
                out["Number of Reels"] = row.get("Number of Reels", "")
                out["Account Status"] = row.get("Account Status", "")
            # 7. LPU Confess
            elif sheet == "LPU Confess":
                out["S.No"] = idx+1
                out["Link"] = row.get("Reel URL", "")
                out["Amount"] = row.get("Amount", "")
                out["Status"] = row.get("Status", "")
                out["Platform"] = "Instagram"
            # 8. Long Term Promotion
            elif sheet == "Long Term Promotion":
                out["Sr.No"] = idx+1
                out["Name"] = row.get("Username", "")
                out["Platform"] = "Instagram"
                out["Profile/Channel Link"] = row.get("Reel URL", "")
                out["Followers"] = row.get("Followers", "")
                out["Number of Reels"] = row.get("Number of Reels", "")
                out["Commercials Per Reel"] = row.get("Commercials Per Reel", "")
            # 9. Shoutout
            elif sheet == "Shoutout":
                out["S No."] = idx+1
                out["Month"] = pd.to_datetime(row.get("Date", ""), errors="coerce").strftime("%B-%Y") if row.get("Date") else ""
                out["ShortCode"] = row.get("ShortCode", "")
                out["ID"] = row.get("ID", "")
                out["Video Link"] = row.get("Reel URL", "")
                out["Views"] = row.get("Views", "")
                out["Likes"] = row.get("Likes", "")
                out["Comments"] = row.get("Comments", "")
                out["Shares"] = row.get("Shares", "")
                out["Platform"] = "Instagram"
            # 10. InstaConfluence
            elif sheet == "InstaConfluence":
                out["S.No"] = idx+1
                out["Month"] = pd.to_datetime(row.get("Date", ""), errors="coerce").strftime("%B-%Y") if row.get("Date") else ""
                out["Name"] = row.get("Username", "")
                out["Platform"] = "Instagram"
                out["Link"] = row.get("Reel URL", "")
                out["Views"] = row.get("Views", "")
                out["Likes"] = row.get("Likes", "")
                out["Comments"] = row.get("Comments", "")
                out["Share"] = row.get("Shares", "")
                out["Followers"] = row.get("Followers", "")
            # 11. Diwali Competition
            elif sheet == "Diwali Competition":
                out["Timestamp"] = row.get("Date", "")
                out["Month"] = pd.to_datetime(row.get("Date", ""), errors="coerce").strftime("%B-%Y") if row.get("Date") else ""
                out["Email Address"] = row.get("Email Address", "")
                out["Name"] = row.get("Username", "")
                out["Registration Number"] = row.get("Registration Number", "")
                out["Mobile Number"] = row.get("Mobile Number", "")
                out["Type of Content"] = row.get("Type of Content", "")
                out["Link"] = row.get("Reel URL", "")
                out["From where you come to know"] = row.get("From where you come to know", "")
                out["shortcode"] = row.get("ShortCode", "")
                out["ID"] = row.get("ID", "")
                out["Plays"] = row.get("Views", "")
                out["Likes"] = row.get("Likes", "")
                out["Comments"] = row.get("Comments", "")
                out["Shares"] = row.get("Shares", "")
                out["Points"] = row.get("Points", "")
                out["Platform"] = "Instagram"
            # 12. Olympics
            elif sheet == "Olympics":
                out["S.No"] = idx+1
                out["Month"] = pd.to_datetime(row.get("Date", ""), errors="coerce").strftime("%B-%Y") if row.get("Date") else ""
                out["Influencer's Name"] = row.get("Username", "")
                out["Platform"] = "Instagram"
                out["Link"] = row.get("Reel URL", "")
                out["Views"] = row.get("Views", "")
                out["Likes"] = row.get("Likes", "")
                out["Comments"] = row.get("Comments", "")
                out["Share"] = row.get("Shares", "")
                out["Type of Influencer"] = row.get("Type of Influencer", "")
                out["Shortcode"] = row.get("ShortCode", "")
                out["id"] = row.get("ID", "")
            # 13. Digital Star
            elif sheet == "Digital Star":
                out["Timestamp"] = row.get("Date", "")
                out["Month"] = pd.to_datetime(row.get("Date", ""), errors="coerce").strftime("%B-%Y") if row.get("Date") else ""
                out["Email Address"] = row.get("Email Address", "")
                out["Name"] = row.get("Username", "")
                out["Registration Number"] = row.get("Registration Number", "")
                out["Mobile Number"] = row.get("Mobile Number", "")
                out["Themes"] = row.get("Theme", "")
                out["Type of Content"] = row.get("Type of Content", "")
                out["Link (Reel or Post on Instagram)"] = row.get("Reel URL", "")
                out["shortcode"] = row.get("ShortCode", "")
                out["ID"] = row.get("ID", "")
                out["Plays"] = row.get("Views", "")
                out["Likes"] = row.get("Likes", "")
                out["Comments"] = row.get("Comments", "")
                out["Shares"] = row.get("Shares", "")
                out["Platform"] = "Instagram"
            # 14. Outcampus
            elif sheet == "Outcampus":
                out["S.No"] = idx+1
                out["Month"] = pd.to_datetime(row.get("Date", ""), errors="coerce").strftime("%B-%Y") if row.get("Date") else ""
                out["Link"] = row.get("Reel URL", "")
                out["shortcode"] = row.get("ShortCode", "")
                out["ID"] = row.get("ID", "")
                out["Views"] = row.get("Views", "")
                out["Likes"] = row.get("Likes", "")
                out["Comment"] = row.get("Comments", "")
                out["Share"] = row.get("Shares", "")
                out["Platform"] = "Instagram"
            return out

        # --- STEP 6: Write to Output Sheets (all tabs) ---
        for sheet, columns in sheet_columns.items():
            df_out = []
            df_sheet = df[df["Assigned Sheet"] == sheet].reset_index(drop=True)
            for i, row in df_sheet.iterrows():
                df_out.append(fill_output_row(sheet, row, i))
            if not df_out:
                continue
            out_df = pd.DataFrame(df_out, columns=columns)
            try:
                sh.del_worksheet(sh.worksheet(sheet))
            except:
                pass
            worksheet = sh.add_worksheet(sheet, rows="1000", cols=str(len(columns)))
            worksheet.update([columns] + out_df.fillna("").values.tolist())
            log.append(f"✅ {len(out_df)} rows written to {sheet}")
        log.append("🏷️ IG Classification/Segregation complete!")
    except Exception as e:
        log.append(f"❌ Error: {str(e)}")
    finally:
        for entry in log:
            st.write(entry)

