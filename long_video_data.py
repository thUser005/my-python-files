import os,re
import random
import shutil
import json



def get_seo_title(bs_name):

    keywords_list = [
        "Audiobook",
        "FullLengthHistoricalFiction",
        "Audiobooks",
        "NewManhwaExplained",
        "JapaneseLightNovelAudiobook",
        "CompletedFantasyManhwa",
        "LightNovelAudiobookEnglish",
        "ProgressionFantasyAudiobooks",
        "AnimeAudiobooks",
        "FullLengthAnimeRecap",
        "EnglishDub",
        "FullMovie",
        "TimeForTheStarsAudiobook",
        "mangareview",
        "manhwareview",
        "animerecommendation",
        "murim",
        "mangaka",
        "wuxia",
        "animenews",
        "mangaupdate"
    ]

        # List of SEO keywords

    seo_keywords = [
        "English Audiobook", "Fantasy Audiobook", "Historical Fiction Audiobook",
        "Full-Length Audiobook", "Light Novel Audiobook", "Epic Adventure Audiobook"
    ]

    seo_keywords = keywords_list + seo_keywords

    # Split the title into words
    words = bs_name.split()

    # Handle cases where the title has only 1 or 2 words
    if len(words) == 1:
        title_main = words[0]
        volume_info = ""
    elif len(words) == 2:
        title_main = " ".join(words)
        volume_info = ""
    else:
        # Extract the main title (First few words, stopping before "-")
        if "-" in words:
            title_main = " ".join(words[:words.index("-")])
        else:
            title_main = " ".join(words[:-3])  # Assuming last 3 words are volume/chapter

    # Extract volume/chapter details (Last few words)
    volume_info = " ".join(words[-3:]) if len(words) > 3 else ""

    # Pick a random keyword from the list
    random_keyword = random.choice(seo_keywords)


    # Construct the new title
    new_title = f"{title_main} - {random_keyword} {volume_info}"
    remove_chars = r"[@#$%^&*()+=<>/\\|[\]{};:\"',_]"
    new_title = re.sub(remove_chars, '', new_title)  # Remove special characters
    new_title = re.sub(r'\s+', ' ', new_title).strip()

    return [new_title,seo_keywords]



def extract_video_data(video_name):

    bs_name = video_name.replace(".mp4","").title()

    img_full_path  = "img.jpg"
    video_full_path = video_name

    seo_name,seo_keywords = get_seo_title(bs_name)
    # Format video description
    video_description = f"""
#anime, #animeedit, #animefan, #lightnovel, #novelrecommendation, #manhwa, #manhwarecommendation,
# #manga, #mangarecommendation, #webtoon, #isekai
📚 Light Novel: {bs_name}
🎬 Video Title: {seo_name}

\t\t{45 * '-'}
Welcome to TimeForEpics!

We bring you daily videos on light novels from various genres, covering all volumes to keep you immersed in epic stories!
Whether you're a fantasy lover, a sci-fi enthusiast, or a romance fan, we've got something for everyone!
If you're searching for a specific video and can't find it, or if you're looking for more great content, be sure to check out our other channels:

----------------------------------------------------------------------------
👉 Telegram Channel - https://t.me/TimeForEpics
----------------------------------------------------------------------------

👉 https://www.youtube.com/@TimeForEpics_01
👉 https://www.youtube.com/@TimeForEpics_02
👉 https://www.youtube.com/@TimeForEpics

Stay tuned for the latest updates on anime, light novels, manhwa, manga, and more! 🚀🎥
💖 Support us by liking, sharing, and subscribing!
🔔 Turn on notifications so you never miss an update!

🌟 Follow our collaborator on Instagram: [@solo.posting.b7](https://instagram.com/solo.posting.b7) for more awesome content!

Join us on this journey through the world of light novels!
#Audiobook #FullLengthHistoricalFiction #Audiobooks #NewManhwaExplained
#JapaneseLightNovelAudiobook #CompletedFantasyManhwa #Audiobook With Subtitles In English
#LightNovelAudiobookEnglish #ProgressionFantasyAudiobooks #AnimeAudiobooks #FullLengthAnimeRecap
#EnglishDub #FullMovie #ClassroomOfTheEliteAudiobook #TimeForTheStarsAudiobook
#mangareview, #manhwareview,@@TimeForEpics_01,@TimeForEpics_02,@TimeForEpics
# #animerecommendation, #murim, #mangaka, #wuxia, #animenews, #mangaupdate.
\t\t{45 * '-'}
"""


    return [seo_name,video_description,video_full_path,img_full_path,seo_keywords]


