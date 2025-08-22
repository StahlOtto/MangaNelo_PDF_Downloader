import requests
from bs4 import BeautifulSoup
import os
import urllib.parse
import threading
from PIL import Image, UnidentifiedImageError
from fpdf import FPDF
import shutil
import re
import time

DIR = os.getcwd()

# Create a new folder to store the manga PDFs
MANGA_DIR = os.path.join(DIR, 'manga')
if not os.path.exists(MANGA_DIR):
    os.mkdir(MANGA_DIR)


def sanitize_directory_name(name):
    # Replace invalid characters with an underscore or another valid character
    return re.sub(r'[<>:"/\\|?*]', '_', name)


def extract_chapter_number(chapter_name):
    # Normalize chapter numbers like "95-5" to "95.5" and then extract
    normalized_name = chapter_name.replace('-', '.')
    match = re.search(r'Chapter (\d+(\.\d+)?)', normalized_name, re.IGNORECASE)
    if match:
        number = match.group(1)
        # Add .0 if the number is a whole number (no decimal or dash)
        if '.' not in number:
            number += '.0'
        return number
    return chapter_name


def page_links(url) -> list:
    retry_attempts = 5
    for attempt in range(retry_attempts):
        try:
            r = requests.get(url)
            soup = BeautifulSoup(r.content, 'html.parser')
            div = str(soup.find("div", {"class": "container-chapter-reader"}))
            imgs = BeautifulSoup(div, 'html.parser').find_all("img")
            page_urls = [i['src'] for i in imgs]
            return page_urls
        except requests.exceptions.RequestException as e:
            print(f"Error fetching page links: {e}")
            if attempt < retry_attempts - 1:
                time.sleep(2 ** attempt)
            else:
                raise


def download_image(name, url):
    retry_attempts = 5
    for attempt in range(retry_attempts):
        try:
            domain = urllib.parse.urlparse(url).netloc
            HEADERS = {
                'Accept': 'image/png,image/svg+xml,image/*;q=0.8,video/*;q=0.8,*/*;q=0.5',
                'Accept-Encoding': 'gzip, deflate, br',
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:141.0) Gecko/20100101 Firefox/141.0',
                'Host': domain, 'Accept-Language': 'en-US,en;q=0.5', 'Referer': 'https://www.nelomanga.net/',
                'Connection': 'keep-alive'
            }
            r = requests.get(url, headers=HEADERS, stream=True)

            if r.status_code != 200:
                raise Exception(f"HTTP error: {r.status_code}")

            content_type = r.headers.get('Content-Type')
            if not content_type or 'image' not in content_type:
                raise Exception(f"Invalid content type: {content_type}")

            # Save the response content to a file
            with open(name, 'wb') as f:
                f.write(r.content)

            # Verify if the image is valid
            with Image.open(name) as img:
                img.verify()

            inputimage = Image.open(name).convert("RGBA")
            image = Image.new("RGB", inputimage.size, "WHITE")
            image.paste(inputimage, (0, 0), inputimage)
            image.save(name)
            break  # Break the loop if download is successful
        except (requests.exceptions.RequestException, UnidentifiedImageError, Exception) as e:
            print(f"Error downloading image {name} from {url}: {e}")
            if os.path.exists(name):
                os.remove(name)
            if attempt < retry_attempts - 1:
                time.sleep(2 ** attempt)
            else:
                # Save error response for analysis
                error_filename = f"error_{name}.html"
                with open(error_filename, 'wb') as f:
                    f.write(r.content)
                print(f"Saved error response content to {error_filename}")


def download_all_images(urls):
    threads = []
    for i in range(len(urls)):
        t = threading.Thread(target=download_image, args=(str(i + 1) + ".jpg", urls[i]))
        threads.append(t)
        t.start()
    for thread in threads:
        thread.join()


def calculate_aspect_ratio(width, height):
    return width / height


def resize_image_to_fit_width(image, max_width):
    img_width, img_height = image.size
    if img_width > max_width:
        scale = max_width / img_width
        new_width = int(img_width * scale)
        new_height = int(img_height * scale)
        resized_image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        return resized_image
    return image


def convert_to_pdf(name, imgs, path):
    print("Starting PDF Conversion: " + name + " with " + str(len(imgs)) + " pages")
    pdf = FPDF('P', 'mm', 'A4')
    pdf.set_auto_page_break(auto=False)

    page_width_mm, page_height_mm = 210, 297
    page_width_px = int(page_width_mm * 96 / 25.4)
    page_height_px = int(page_height_mm * 96 / 25.4)

    for img_path in imgs:
        if os.path.exists(img_path):
            try:
                cover = Image.open(img_path)
                # First, resize the image to fit within the page width
                cover = resize_image_to_fit_width(cover, page_width_px)
                img_width, img_height = cover.size

                # Continue with the aspect ratio check and segmentation as before...
                pdf_aspect_ratio = calculate_aspect_ratio(page_width_px, page_height_px)
                img_aspect_ratio = calculate_aspect_ratio(img_width, img_height)

                ratio_difference = abs(img_aspect_ratio - pdf_aspect_ratio) / pdf_aspect_ratio

                if ratio_difference > 0.15:

                    current_top = 0
                    while current_top < img_height:
                        crop_bottom = min(current_top + page_height_px, img_height)
                        new_image_part = cover.crop((0, current_top, img_width, crop_bottom))
                        current_top = crop_bottom

                        img_part_width, img_part_height = new_image_part.size

                        temp_img_path = os.path.join(path, f"temp_cropped_{img_path[:-4]}_{current_top}.jpg")
                        new_image_part.save(temp_img_path)

                        img_width_mm = img_part_width * 25.4 / 96
                        img_height_mm = img_part_height * 25.4 / 96

                        pdf.add_page()
                        pdf.set_fill_color(0, 0, 0)  # Black background
                        pdf.rect(0, 0, page_width_mm, page_height_mm, 'F')  # Fill the entire page

                        pdf.image(temp_img_path, 0, 0, img_width_mm, img_height_mm)

                        os.remove(temp_img_path)

                else:
                    img_width_mm = img_width * 25.4 / 96
                    img_height_mm = img_height * 25.4 / 96

                    scale = min(page_width_mm / img_width_mm, page_height_mm / img_height_mm)
                    new_width = img_width_mm * scale
                    new_height = img_height_mm * scale

                    # For normal images, each image starts on a new page
                    pdf.add_page()
                    pdf.set_fill_color(0, 0, 0)  # Black background
                    pdf.rect(0, 0, page_width_mm, page_height_mm, 'F')  # Fill the entire page

                    x_offset = (page_width_mm - new_width) / 2
                    y_offset = (page_height_mm - new_height) / 2

                    pdf.image(img_path, x_offset, y_offset, new_width, new_height)

                cover.close()  # Ensure the image file is closed before trying to delete it
                os.remove(img_path)
            except UnidentifiedImageError as e:
                print(f"Error processing image {img_path}: {e}")
                continue  # Skip the problematic image
        else:
            print(f"File not found: {img_path}, skipping.")

    if not os.path.exists(MANGA_DIR):
        os.makedirs(MANGA_DIR)

    pdf_filename = os.path.join(MANGA_DIR, f"{name}.pdf")

    try:
        pdf.output(pdf_filename, "F")
        print(f"Downloaded {name} successfully")
    except FileNotFoundError as e:
        print(f"Failed to save PDF: {e}")

    os.chdir(DIR)

    time.sleep(1)

    if os.path.exists(path):
        try:
            shutil.rmtree(path)
        except Exception as e:
            print(f"Failed to delete directory {path}: {e}")
    else:
        print(f"Directory {path} does not exist, skipping deletion.")


def download_manga(chapter_name, url):
    print(f"Downloading {chapter_name} from {url}")

    chapter_number = extract_chapter_number(chapter_name)

    pages = page_links(url)
    num = len(pages)
    print(f"Downloading {num} pages")

    sanitized_name = sanitize_directory_name(chapter_number)
    path = os.path.join(DIR, sanitized_name)

    if not os.path.exists(path):
        os.mkdir(path)
    os.chdir(path)

    download_all_images(pages)
    imgs = [str(i + 1) + ".jpg" for i in range(num)]
    convert_to_pdf(chapter_number, imgs, path)


def chapter_links(URL) -> dict:
    retry_attempts = 5
    for attempt in range(retry_attempts):
        try:
            r = requests.get(URL)
            soup = BeautifulSoup(r.content, 'html.parser')
            chapters = soup.find_all("a", {})
            links = {}
            for chapter in chapters:
                if URL in chapter["href"] and chapter.text.strip().startswith("Chapter"):
                    links[chapter.text.strip()] = chapter["href"]
            return links
        except requests.exceptions.RequestException as e:
            print(f"Error fetching chapter links: {e}")
            if attempt < retry_attempts - 1:
                time.sleep(2 ** attempt)
            else:
                raise


def sort_chapters(chapters):
    def extract_chapter_number(chapter_name):
        # Extracting chapter number considering possible decimal points
        normalized_name = chapter_name.replace('-', '.')
        match = re.search(r'Chapter (\d+(?:\.\d+)?)', normalized_name)
        return float(match.group(1)) if match else float('inf')

    sorted_chapters = dict(sorted(chapters.items(), key=lambda x: extract_chapter_number(x[0])))
    return sorted_chapters


def main():
    URL = input("Enter the URL of the manga: ")
    print("URL: " + URL)
    chapters = chapter_links(URL)

    # Filter out volume chapters

    chapters = {k: v for k, v in chapters.items() if "Chapter" in k}

    chapters = sort_chapters(chapters)

    while True:
        print("Choose an option:")
        print("1. Download all chapters at once")
        print("2. Download chapters sequentially")
        print("3. Download a particular chapter")
        print("4. Quit (q)")

        choice = input("Enter your choice (1/2/3/4): ")

        if choice == '1':
            progress = 0
            length = len(chapters)
            for chapter in chapters:
                download_manga(chapter, chapters[chapter])
                progress += 1 / length
                print("Progress: " + str(round(progress * 100, 2)) + "%")
        elif choice == '2':
            for chapter in chapters:
                print(chapter + ": " + chapters[chapter])
                y = input("Download? (Y/n/q): ")
                if y.lower() == 'y':
                    download_manga(chapter, chapters[chapter])
                elif y.lower() == 'q':
                    print("Exiting...")
                    return
        elif choice == '3':
            print("Available chapters:")
            for chapter in chapters:
                print(chapter + ": " + chapters[chapter])
            chap_name = input("Enter the name of the chapter to download: ")
            if chap_name in chapters:
                download_manga(chap_name, chapters[chap_name])
            else:
                print("Chapter not found.")
        elif choice.lower() == '4' or choice.lower() == 'q':
            print("Exiting...")
            break
        else:
            print("Invalid choice, please try again.")


if __name__ == "__main__":
    main()