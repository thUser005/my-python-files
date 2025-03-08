
import sys
import fitz
import os
import re
import asyncio,time
import shutil
import edge_tts
import nest_asyncio

# Allow nested event loops in Google Colab
nest_asyncio.apply()


def extract_text_from_pdf(pdf_path):
    """Extracts text from each page of a PDF, ensuring non-empty text for speech."""
    print(f"Opening PDF: {pdf_path}")
    try:
        doc = fitz.open(pdf_path)
    except Exception as e:
        print(f"Error opening PDF: {e}")
        return []

    total_pages = len(doc)
    print(f"Total pages in PDF: {total_pages}")
    warning_word = "[Content Warning: word got censored]"

    inappropriate_words = {
        # Profanity
        "fuck": warning_word, "shit": warning_word, "bitch": warning_word, "asshole": warning_word,
        "bastard": warning_word, "damn": warning_word, "dick": warning_word, "piss": warning_word,
        "crap": warning_word, "cunt": warning_word, "slut": warning_word, "whore": warning_word,
        "bollocks": warning_word, "bugger": warning_word, "wanker": warning_word, "prick": warning_word,
        "twat": warning_word, "arse": warning_word, "motherfucker": warning_word, "jackass": warning_word,

        # Explicit Anatomy Terms (For Moderation)
        "boob": warning_word, "boobs": warning_word, "nipple": warning_word, "nipples": warning_word,
        "penis": warning_word, "vagina": warning_word, "clitoris": warning_word, "testicle": warning_word,
        "testicles": warning_word, "scrotum": warning_word, "breasts": warning_word, "butt": warning_word,
        "buttocks": warning_word, "cock": warning_word, "dildo": warning_word, "pussy": warning_word,
        "cum": warning_word, "ejaculate": warning_word, "orgasm": warning_word, "anus": warning_word,

        # Other Inappropriate Words
        "porn": warning_word, "porno": warning_word, "erotic": warning_word, "fetish": warning_word,
        "nude": warning_word, "naked": warning_word, "stripper": warning_word, "escort": warning_word,
        "prostitute": warning_word, "brothel": warning_word, "seduction": warning_word, "sensual": warning_word,
        "affair": warning_word, "lust": warning_word, "bondage": warning_word, "dominatrix": warning_word,

        "fuck": warning_word,"shit": warning_word,"asshole": warning_word,"bitch": warning_word,"cunt": warning_word,"dick": warning_word,"prick": warning_word,"piss": warning_word,"cock": warning_word,"twat": warning_word,"fucker": warning_word,"motherfucker": warning_word,"bullshit": warning_word,"ass": warning_word,"crap": warning_word,"douche": warning_word,"wanker": warning_word,"arse": warning_word,

        # Nudity/Sexual Content (20 samples)
        "nude": warning_word,"naked": warning_word,"porn": warning_word,"sex": warning_word,"erotic": warning_word,"strip": warning_word,"boobs": warning_word,"tits": warning_word,"pussy": warning_word,"penis": warning_word,"vagina": warning_word,"assfuck": warning_word,"blowjob": warning_word,"cum": warning_word,"orgasm": warning_word,"seduce": warning_word,"fuckme": warning_word,"horny": warning_word,"slutty": warning_word,"whorehouse": warning_word,

        # Violence/Gore (20 samples)
        "blood": warning_word,"gore": warning_word,"kill": warning_word,"murder": warning_word,"stab": warning_word,"shoot": warning_word,"behead": warning_word,"torture": warning_word,"slaughter": warning_word,"execute": warning_word,"dismember": warning_word,"bruise": warning_word,"maim": warning_word,"bleed": warning_word,"gut": warning_word,"slash": warning_word,"smash": warning_word,"bash": warning_word,"decapitate": warning_word,"rip": warning_word,

        # Hate Speech/Discrimination (20 samples)
        "racist": warning_word,"slut": warning_word,"whore": warning_word,"fag": warning_word,"nigger": warning_word,"chink": warning_word,"spic": warning_word,"kike": warning_word,"retard": warning_word,"cripple": warning_word,"tranny": warning_word,"dyke": warning_word,"paki": warning_word,"gook": warning_word,"wetback": warning_word,"coon": warning_word,"jap": warning_word,"homo": warning_word,"mongoloid": warning_word,"bimbo": warning_word,

        # Drugs/Alcohol (20 samples)
        "cocaine": warning_word,"heroin": warning_word,"meth": warning_word,"weed": warning_word,"pot": warning_word,"crack": warning_word,"lsd": warning_word,"ecstasy": warning_word,"stoned": warning_word,"junkie": warning_word,
    }

    text_pages = []
    for page_num in range(total_pages):
        try:
            text = doc[page_num].get_text("text").strip()
            text = re.sub(r'\s+', ' ', text)  # Normalize whitespace
            # Remove special characters
            remove_chars = '@#$%^&*()+=<>/\\|[]}{;:"\'-_'
            text = text.translate(str.maketrans('', '', remove_chars))
            text = text.replace(".",", ")

            # Check for inappropriate words
            occurrences = {word: 0 for word in inappropriate_words}
            words = text.split()
            for i, word in enumerate(words):
                word = word.translate(str.maketrans('', '', remove_chars))
                lower_word = word.lower()
                if lower_word in inappropriate_words:
                    occurrences[lower_word] += 1
                    if occurrences[lower_word] > 0:
                        words[i] = inappropriate_words[lower_word]
                        for j in range(i):
                            if words[j].lower() == lower_word:
                                words[j] = inappropriate_words[lower_word]
            text = " ".join(words)
            for word, count in occurrences.items():
                if count > 3:
                    text = re.sub(rf'\b{word}\b', inappropriate_words[word], text, flags=re.IGNORECASE)


            # # Special conditions
            # if "copyright" in text.lower() or ".com" in text or (1 <= page_num <= 5):
            #     text = "this page seems to be does not read on illustrations or empty page, Audiobook reading does not read on illustrations or empty page"
            #     if page_num>3:
            #         text +=   "following platform policies we notify viewrs, when inappropriate words got replaced, For the complete version without content moderation or unsensored,  please join our Telegram channel, where we will post full version in future, "

            # elif page_num <= 5:
            #     text = "Page seems to be an image or text not available."
            # # special condtions ended
            
            if not text.strip():
                text = f"Page {page_num + 1} completed."

            # Optimized advertisement placement
            if page_num % 20 == 0 and page_num != 0:
                text += " Quick reminder! If you're enjoying this audiobook, consider supporting our channel by liking, commenting, and subscribing. Your support helps us bring you more great content! Now, back to the story!"

            if page_num == total_pages-1:
                text += (
                " As this video content comes to an end, we would like to remind you that the continuation of every video will be made available exclusively on our Telegram channel. "
                "However, if our channel gains sufficient engagement and support through your feedback in the comments, likes, and shares, we will consider making all videos publicly accessible. "
                "Our goal is to produce a vast collection of three thousand videos in coming time period covering light novels, manhwa, and webtoons—an ambitious project that requires significant computational resources. "
                "Your support is crucial in helping us sustain and expand this initiative. So, if you enjoy our content, please take a moment to like, share, and comment. "
                "Your engagement not only motivates us but also ensures that we can continue bringing high-quality content to the community. Thank you for being a valued part of our journey!"

            )
            if page_num == 0:
                text = f"This video presents an audiobook version of the light novel {pdf_path.replace('.pdf','')}" + text


            text_pages.append((page_num + 1, text))
        except Exception as e:
            print(f"Error processing page {page_num + 1}: {e}")
            text_pages.append((page_num + 1, f"Error on page {page_num + 1}"))

    doc.close()  # Clean up
    return text_pages




import asyncio
import edge_tts
import shutil
import time



FALLBACK_AUDIO_PATH = "fallback_audio.mp3"

async def generate_fallback_audio():
    """Generate a single fallback audio file if it doesn't exist."""
    if not os.path.exists(FALLBACK_AUDIO_PATH):
        fallback_text = "This page audio could not be generated, due to technical problem so this page will be skipped,"
        voice = "en-AU-NatashaNeural"
        communicate = edge_tts.Communicate(fallback_text, voice)
        await communicate.save(FALLBACK_AUDIO_PATH)

async def text_to_speech(text, output_audio_path, retry_attempts=3):
    """Converts text to speech using edge-tts and saves as an MP3 file.
       Uses a fallback audio file if generation fails."""
    
    await generate_fallback_audio()  # Ensure fallback audio exists
    
    if not text.strip():
        text = "No content available for this page."

    # Remove special characters
    remove_chars = '@#$%^&*()+=<>/\\|[]{};:"\'-_'
    text = text.translate(str.maketrans('', '', remove_chars))

    voice = "en-AU-NatashaNeural"
    temp_mp3_path = output_audio_path.replace(".mp3", "_temp.mp3")

    for attempt in range(retry_attempts):
        try:
            # Generate audio for the provided text
            communicate = edge_tts.Communicate(text, voice)
            await communicate.save(temp_mp3_path)

            # Move file to final destination
            shutil.move(temp_mp3_path, output_audio_path)
            return output_audio_path  # Return output path on success

        except Exception as e:
            print(f"Error on attempt {attempt + 1}: {e}")
            if attempt < retry_attempts - 1:
                print("Retrying after 30 seconds...")
                time.sleep(30)  # Wait before retrying
            else:
                print("Max retries reached. Using fallback audio.")

    # If all retries fail, use the fallback audio
    shutil.copy(FALLBACK_AUDIO_PATH, output_audio_path)
    return output_audio_path


def pdf_to_audio(pdf_path, output_folder="audio_pages_01"):
    """Processes PDF and generates an audio file for each page."""
    print("Starting PDF to Audio Conversion...")

    # Extract text from PDF
    text_pages = extract_text_from_pdf(pdf_path)

    # Ensure output folder exists
    os.makedirs(output_folder, exist_ok=True)

    # Convert each page's text to an individual audio file
    for page_num, text in text_pages:
               # Print progress in the same line
      sys.stdout.write(f"\rProcessing text page: {page_num}/{len(text_pages)}")
      sys.stdout.flush()
      output_audio_path = f"{output_folder}/page{page_num}.mp3"

      asyncio.run(text_to_speech(text, output_audio_path))


    print("\nAll pages processed! Audio files saved inside:", output_folder)

