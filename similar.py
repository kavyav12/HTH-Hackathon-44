import streamlit as st
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import time
import random
import urllib.parse

# Generate broader search queries
def generate_related_queries(keyword):
    variations = [
        f"{keyword} court case news",
        f"{keyword} legal judgment pdf",
        f"{keyword} supreme court ruling",
        f"{keyword} lawsuit history",
        f"{keyword} government legal documents",
        f"{keyword} case law reference",
        f"{keyword} verdict and appeals",
        f"{keyword} high court decision",
        f"{keyword} latest legal updates",
        f"{keyword} legal case study",
        f"{keyword} legal precedents",
        f"{keyword} litigation process",
        f"{keyword} law enforcement cases",
        f"{keyword} judicial decisions",
        f"{keyword} supreme court review",
        f"{keyword} appeals court ruling",
    ]
    return random.sample(variations, min(len(variations), 7))  # Select 7 queries randomly

# Function to scrape links for multiple queries
def scrape_links(keyword, max_results=15):
    queries = generate_related_queries(keyword)
    all_links = set()

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    for query in queries:
        search_url = f"https://www.bing.com/search?q={urllib.parse.quote(query)}"
        driver.get(search_url)
        time.sleep(2)

        search_results = driver.find_elements(By.CSS_SELECTOR, "li.b_algo")
        for result in search_results:
            try:
                link_element = result.find_element(By.TAG_NAME, "a")
                link = link_element.get_attribute("href")
                if link:
                    all_links.add(link)
                if len(all_links) >= max_results:
                    break
            except Exception:
                continue  
        if len(all_links) >= max_results:
            break

    driver.quit()
    return list(all_links)[:max_results]

# Streamlit UI with dark theme
st.set_page_config(page_title="Legal Case Finder", layout="wide")

st.markdown(
    """
    <style>
        body { background-color: black; color: white; }
        .stTextInput label, .stButton button { color: white !important; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("🔍 Legal Case & News Finder")

keyword = st.text_input("Enter a keyword to find related legal cases & news:")

if st.button("Search"):
    if keyword:
        st.write(f"🔎 Searching for articles and cases related to '{keyword}'...")
        links = scrape_links(keyword)

        if links:
            st.subheader("📜 Related Legal Cases & News")

            cols = st.columns(3)  # 3-column layout
            for i, link in enumerate(links):
                domain = urllib.parse.urlparse(link).netloc  # Extract website domain

                # Styled box for each result
                with cols[i % 3]:
                    st.markdown(
                        f"""
                        <div style="
                            border: 2px solid #ffffff;
                            padding: 10px;
                            margin-bottom: 10px;
                            border-radius: 8px;
                            background-color: #222;
                            color: white;
                            text-align: center;
                        ">
                            <p><strong>Source:</strong> {domain}</p>
                            <p><a href="{link}" target="_blank" style="color: #4CAF50;">🔗 Open Link</a></p>
                        </div>
                        """, 
                        unsafe_allow_html=True
                    )
        else:
            st.warning("No relevant pages found. Try another keyword.")
    else:
        st.warning("Please enter a keyword.")