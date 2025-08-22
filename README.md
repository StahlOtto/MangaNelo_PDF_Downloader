## 📖 **Manga/Webtoon Downloader**

This project allows you to **download manga chapters** from a given URL and **convert them into PDF format**, including **support for webtoon-style long images**! The Python script automates the entire process—from fetching the manga images to organizing them into a neatly formatted PDF, ready for offline reading.

The project is based on an idea from [this repository](https://github.com/rishabhxchoudhary/Youtube---Manga-Downloader) by **Rishabh Choudhary**. In this fork, I've improved the **PDF conversion process** and added support for **long images** often found in webtoons, ensuring they fit neatly in the generated PDF.

### 📋 **Table of Contents**
- [Features](#features)
- [How It Works](#how-it-works)
- [Installation](#installation)
- [Usage](#usage)
- [Example](#example)
- [Credits](#credits)
- [Contributing](#contributing)

---

### ✨ **Features** <a name="features"></a>

- **Download Manga as PDFs**: Easily download manga chapters or entire series as PDF files.
- **Handles Webtoon-Style Images**: Automatically resizes and breaks long images (common in webtoons) to fit neatly across multiple PDF pages.
- **Multi-Chapter Download**: Choose to download all chapters at once or select specific chapters.
- **Retry Mechanism**: Implements retries for failed downloads to ensure robustness.

---

### ⚙️ **How It Works** <a name="how-it-works"></a>

1. **Chapter Links Extraction**: 
   - The script first extracts all the chapter links from a manga URL by parsing the HTML content of the page using `BeautifulSoup`.

2. **Page Links Extraction**:
   - For each chapter, it retrieves the individual image URLs that represent each manga page.

3. **Downloading Images**:
   - The script downloads each image from the given chapter URL and saves it locally while creating the pdf file for the chapter.

4. **Image to PDF Conversion**:
   - Images are resized and adjusted for the PDF format. For long webtoon-style images, the script intelligently crops them into smaller sections that fit the page size and maintains the image quality.

5. **Final PDF Output**:
   - All images are then compiled into a single PDF file per chapter. The background for each PDF page is filled with a black color in case there are gaps between images.

---

### 📥 **Installation** <a name="installation"></a>

#### Prerequisites
- Python 3.8 or higher
- `pip` for package management

#### Steps

1. Clone this repository:

    ```bash
    git clone https://github.com/StahlOtto/MangaNelo_PDF_Downloader.git
    cd manga_webtoon_pdf_reader
    ```

2. Install the dependencies:

    ```bash
    pip install -r requirements.txt
    ```

3. Make sure you have a stable internet connection as the script downloads images from the web.

---

### 🚀 **Usage** <a name="usage"></a>

To run the script, use the following command:

```bash
python manga.py
```

Once the script runs, it will prompt you for the URL of the manga you want to download. Simply copy the manga URL from the website and paste it when prompted. Use the website https://www.nelomanga.net/xyz as the code was built with this website in mind.

#### Usage Example

1. After starting the script, you'll see options like this:

    ```
    Choose an option:
    1. Download all chapters at once
    2. Download chapters sequentially
    3. Download a particular chapter
    4. Quit (q)
    ```

2. Choose the desired option:
    - **Option 1**: Downloads all chapters available from the URL.
    - **Option 2**: Sequentially downloads each chapter with a prompt for user confirmation.
    - **Option 3**: Lets you select and download a specific chapter.
    - **Option 4**: Quits the script.

3. The downloaded chapters are saved in the `manga/` directory, organized as PDF files in chapter order.

---

### 🖼️ **Example Output** <a name="example"></a>

The final output is a set of PDF files stored in the `manga/` directory, where each file corresponds to a manga chapter. Here's an example structure of the output:

```
/manga
  ├── 1.0.pdf
  ├── 1.5.pdf
  ├── 2.0.pdf
  └── ...
```

---

### 🎉 **Credits** <a name="credits"></a>

This project is based on a fork by RyuKaS of an original idea by [Rishabh Choudhary](https://github.com/rishabhxchoudhary/Youtube---Manga-Downloader). Significant improvements have been made to the PDF conversion logic, especially to handle long images for webtoon formats. It was forked again, so that it works with the new MangaNelo Website.

---

### 🤝 **Contributing** <a name="contributing"></a>

Contributions are welcome! If you find a bug or have a feature request, feel free to code your version. 

---

### 📝 **License**

This project is open-source and available under the MIT License. Feel free to modify and distribute the code.