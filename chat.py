import streamlit as st
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import google.generativeai as genai
from langchain.vectorstores import FAISS
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
from googletrans import Translator
import io
import base64
from datetime import datetime
import json
import re

# Load environment variables
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    st.error("GOOGLE_API_KEY is not available. Please check your .env file.")
    st.stop()

genai.configure(api_key=api_key)
translator = Translator()

# Custom CSS
def load_css():
    st.markdown("""
    <style>
    /* Modern Legal App Styling */
    
    /* Base styling */
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700&display=swap');
    
    * {
        font-family: 'Roboto', sans-serif;
        transition: all 0.3s ease;
    }
    
    /* Main container styling with gradient */
    .main {
        background: linear-gradient(135deg, #f5f7fa 0%, #e4e8f0 100%);
        padding: 30px;
        color: #333;
        min-height: 100vh;
    }
    
    /* Header styling with shadow */
    .stApp header {
        background: linear-gradient(90deg, #0a2540 0%, #1a3c5a 100%) !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2) !important;
    }
    
    h1, h2, h3 {
        font-family: 'Playfair Display', serif;
        color: #0a2540;
    }
    
    /* App title with elegant animation */
    .app-title {
        text-align: center;
        background: linear-gradient(90deg, #0a2540, #2a5a85, #0a2540);
        background-size: 200% auto;
        color: #fff;
        padding: 20px;
        border-radius: 8px;
        margin-bottom: 30px;
        box-shadow: 0 6px 15px rgba(10, 37, 64, 0.2);
        animation: gradient 8s ease infinite;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    
    @keyframes gradient {
        0% {background-position: 0% 50%;}
        50% {background-position: 100% 50%;}
        100% {background-position: 0% 50%;}
    }
    
    .app-title h1 {
        color: white;
        margin: 0;
        font-size: 2.5rem;
    }
    
    .app-icon {
        font-size: 2.8rem;
        margin-right: 15px;
    }
    
    /* Custom animated card for chat messages */
    .chat-message {
        padding: 1.5rem;
        border-radius: 0.8rem;
        margin-bottom: 1.5rem;
        display: flex;
        flex-direction: column;
        animation: slideIn 0.3s ease-out;
        transition: transform 0.2s;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        width: 100%;
        overflow-wrap: break-word;
        word-wrap: break-word;
        word-break: break-word;
    }
    
    .message-content {
        width: 100%;
        padding: 0.5rem;
    }
    
    @keyframes slideIn {
        from {opacity: 0; transform: translateY(20px);}
        to {opacity: 1; transform: translateY(0);}
    }
    
    .chat-message:hover {
        transform: translateY(-5px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.15);
    }
    
    .chat-message.user {
        background: linear-gradient(to right, #e6f3ff, #d4e9fd);
        border-left: 5px solid #2e86de;
    }
    
    .chat-message.bot {
        background: linear-gradient(to right, #f0f7ff, #e1eefa);
        border-left: 5px solid #5cb85c;
    }
    
    /* Elegant sidebar styling with depth */
    .css-1d391kg, .css-hxt7ib {
        background: linear-gradient(180deg, #f1f3f8 0%, #e4e8f0 100%);
        box-shadow: inset -5px 0 10px -5px rgba(0,0,0,0.1);
    }
    
    /* Modern File uploader */
    .stFileUploader {
        padding: 20px;
        border: 2px dashed #1a3c5a;
        border-radius: 15px;
        text-align: center;
        background-color: rgba(26, 60, 90, 0.05);
        transition: all 0.3s;
    }
    
    .stFileUploader:hover {
        background-color: rgba(26, 60, 90, 0.1);
        border-color: #2a5a85;
    }
    
    /* Animated Buttons */
    .stButton>button {
        background: linear-gradient(90deg, #1a3c5a 0%, #2a5a85 100%);
        color: white;
        font-weight: 500;
        border: none;
        border-radius: 50px;
        padding: 0.7rem 1.5rem;
        transition: all 0.3s;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .stButton>button:hover {
        background: linear-gradient(90deg, #2a5a85 0%, #3a7ab5 100%);
        box-shadow: 0 6px 12px rgba(0,0,0,0.2);
        transform: translateY(-2px);
    }
    
    .stButton>button:active {
        transform: translateY(1px);
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    
    /* History section with scrolling effect */
    .history-container {
        max-height: 600px;
        overflow-y: auto;
        padding: 15px;
        background: linear-gradient(to bottom, #fff, #f8f9fa);
        border-radius: 8px;
        border: 1px solid #e9ecef;
        box-shadow: inset 0 0 10px rgba(0,0,0,0.05);
        scrollbar-width: thin;
    }
    
    .history-container::-webkit-scrollbar {
        width: 6px;
    }
    
    .history-container::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 10px;
    }
    
    .history-container::-webkit-scrollbar-thumb {
        background: #1a3c5a;
        border-radius: 10px;
    }
    
    .history-item {
        margin-bottom: 12px;
        padding: 20px;
        background-color: white;
        border-radius: 8px;
        border-left: 4px solid #1a3c5a;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        transition: all 0.2s;
        animation: fadeIn 0.5s ease-out;
        color: #333;
    }
    
    .history-question {
        font-weight: 500;
        color: #1a3c5a;
        margin-bottom: 12px;
        font-size: 1.1em;
    }
    
    .history-answer {
        color: #333;
        background-color: #f8f9fa;
        padding: 10px;
        border-radius: 4px;
        border-left: 3px solid #5cb85c;
        margin-top: 8px;
    }
    
    @keyframes fadeIn {
        from {opacity: 0;}
        to {opacity: 1;}
    }
    
    .history-item:hover {
        transform: scale(1.01);
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        background-color: #f9fbfd;
    }
    
    .history-timestamp {
        font-size: 0.8rem;
        color: #6c757d;
        margin-bottom: 5px;
    }
    
    .history-question {
        font-weight: 500;
        color: #1a3c5a;
        margin-bottom: 8px;
    }
    
    .history-answer {
        color: #495057;
    }
    
    /* Document tab with glass morphism effect */
    .document-tab {
        padding: 25px;
        background-color: rgba(255, 255, 255, 0.8);
        backdrop-filter: blur(10px);
        border-radius: 12px;
        box-shadow: 0 8px 32px rgba(31, 38, 135, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.18);
        margin-bottom: 30px;
        transition: all 0.3s;
    }
    
    .document-tab:hover {
        box-shadow: 0 8px 32px rgba(31, 38, 135, 0.2);
        transform: translateY(-5px);
    }
    
    /* Contract template with elegant styling */
    .contract-template {
        padding: 30px;
        background-color: #f8f8f8;
        background-image: linear-gradient(45deg, #f9f9f9 25%, transparent 25%, transparent 75%, #f9f9f9 75%, #f9f9f9), 
                        linear-gradient(45deg, #f9f9f9 25%, transparent 25%, transparent 75%, #f9f9f9 75%, #f9f9f9);
        background-size: 20px 20px;
        background-position: 0 0, 10px 10px;
        border: 1px solid #ddd;
        border-radius: 8px;
        font-family: 'Playfair Display', serif;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    }
    
    /* Timeline styling with 3D effect */
    .timeline-container {
        position: relative;
        margin: 40px 0;
        perspective: 1000px;
    }
    
    .timeline-container::after {
        content: '';
        position: absolute;
        width: 6px;
        background: linear-gradient(to bottom, #1a3c5a, #2a5a85);
        top: 0;
        bottom: 0;
        left: 50%;
        margin-left: -3px;
        border-radius: 3px;
        box-shadow: 0 0 10px rgba(26, 60, 90, 0.3);
    }
    
    .timeline-item {
        padding: 15px 50px;
        position: relative;
        background-color: inherit;
        width: 50%;
        perspective: 1000px;
        transform-style: preserve-3d;
        animation: timelineAppear 0.8s ease-out;
    }
    
    @keyframes timelineAppear {
        from {opacity: 0; transform: rotateY(-30deg) translateX(-50px);}
        to {opacity: 1; transform: rotateY(0) translateX(0);}
    }
    
    .timeline-item::after {
        content: '';
        position: absolute;
        width: 25px;
        height: 25px;
        right: -17px;
        background: linear-gradient(135deg, #ffffff 0%, #f1f3f8 100%);
        border: 4px solid #1a3c5a;
        top: 15px;
        border-radius: 50%;
        z-index: 1;
        box-shadow: 0 0 0 5px rgba(26, 60, 90, 0.2);
        transition: all 0.3s;
    }
    
    .timeline-item:hover::after {
        box-shadow: 0 0 0 8px rgba(26, 60, 90, 0.3);
        transform: scale(1.2);
    }
    
    .timeline-item.left {
        left: 0;
        animation-delay: 0.2s;
    }
    
    .timeline-item.right {
        left: 50%;
        animation-delay: 0.4s;
    }
    
    .timeline-item.right::after {
        left: -16px;
    }
    
    .timeline-content {
        padding: 20px 30px;
        background: linear-gradient(to bottom right, #ffffff, #f5f7fa);
        position: relative;
        border-radius: 12px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        transition: all 0.3s;
        transform: translateZ(0);
    }
    
    .timeline-content:hover {
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
        transform: translateY(-5px) translateZ(10px);
    }
    
    .timeline-date {
        font-weight: 700;
        color: #1a3c5a;
        margin-bottom: 10px;
        font-size: 1.1rem;
        border-bottom: 2px solid #1a3c5a;
        padding-bottom: 5px;
        display: inline-block;
    }
    
    /* Animated Download button */
    .download-button {
        display: inline-block;
        padding: 12px 24px;
        background: linear-gradient(90deg, #1a3c5a 0%, #2a5a85 100%);
        color: white;
        text-decoration: none;
        border-radius: 50px;
        font-weight: 500;
        margin-top: 15px;
        text-align: center;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        transition: all 0.3s;
        position: relative;
        overflow: hidden;
    }
    
    .download-button::before {
        content: "";
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.4), transparent);
        transition: all 0.6s;
    }
    
    .download-button:hover {
        background: linear-gradient(90deg, #2a5a85 0%, #3a7ab5 100%);
        box-shadow: 0 6px 12px rgba(0,0,0,0.2);
        transform: translateY(-3px);
        color: white;
        text-decoration: none;
    }
    
    .download-button:hover::before {
        left: 100%;
    }
    
    .download-button:active {
        transform: translateY(1px);
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    
    /* Tab navigation styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background-color: rgba(255, 255, 255, 0.7);
        backdrop-filter: blur(10px);
        padding: 10px;
        border-radius: 50px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }

    .stTabs [data-baseweb="tab"] {
        height: 50px;
        border-radius: 25px;
        margin-right: 5px;
        background-color: rgba(255, 255, 255, 0.5);
        color: #1a3c5a;
        transition: all 0.3s;
        font-weight: 500;
        border: 1px solid transparent;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    .stTabs [aria-selected="true"] {
        background-color: #1a3c5a !important;
        color: white !important;
        border: 1px solid #1a3c5a;
        box-shadow: 0 4px 10px rgba(26, 60, 90, 0.3);
        transform: translateY(-2px);
    }

    .stTabs [data-baseweb="tab"]:hover {
        background-color: rgba(26, 60, 90, 0.1);
        transform: translateY(-2px);
        box-shadow: 0 4px 10px rgba(0,0,0,0.1);
    }
    
    /* Animated text inputs */
    .stTextInput>div>div>input,
    .stTextArea>div>div>textarea, 
    .stSelectbox>div>div>div {
        border-radius: 8px;
        border: 2px solid #e1e5eb;
        padding: 12px 15px;
        transition: all 0.3s;
        background-color: rgba(255, 255, 255, 0.8);
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }

    .stTextInput>div>div>input:focus,
    .stTextArea>div>div>textarea:focus,
    .stSelectbox>div>div>div:focus {
        border-color: #1a3c5a;
        box-shadow: 0 0 0 2px rgba(26, 60, 90, 0.2);
        transform: translateY(-2px);
    }

    .stTextInput>div>div>input:hover,
    .stTextArea>div>div>textarea:hover,
    .stSelectbox>div>div>div:hover {
        border-color: #2a5a85;
    }
    
    /* Progress bar styling */
    .stProgress > div > div > div > div {
        background-color: #1a3c5a;
        background-image: linear-gradient(45deg, rgba(255, 255, 255, 0.15) 25%, transparent 25%, transparent 50%, rgba(255, 255, 255, 0.15) 50%, rgba(255, 255, 255, 0.15) 75%, transparent 75%, transparent);
        background-size: 1rem 1rem;
        animation: progress-bar-stripes 1s linear infinite;
    }
    
    @keyframes progress-bar-stripes {
        0% {background-position-x: 1rem;}
    }

    /* Loading spinner with animation */
    .stSpinner {
        border: 4px solid rgba(26, 60, 90, 0.1);
        border-radius: 50%;
        border-top: 4px solid #1a3c5a;
        width: 40px;
        height: 40px;
        animation: spinner 1s linear infinite;
        margin: 20px auto;
    }
    
    @keyframes spinner {
        0% {transform: rotate(0deg);}
        100% {transform: rotate(360deg);}
    }
    
    /* Custom checkboxes and radio buttons */
    .stCheckbox > div[role="checkbox"],
    input[type="radio"] {
        cursor: pointer;
        width: 20px;
        height: 20px;
        margin-right: 10px;
        position: relative;
        transition: all 0.3s;
    }
    
    .stCheckbox > div[role="checkbox"]:checked,
    input[type="radio"]:checked {
        background-color: #1a3c5a;
        border-color: #1a3c5a;
    }
    
    /* Dark mode adjustments */
    @media (prefers-color-scheme: dark) {
        .main {
            background: linear-gradient(135deg, #1c2331 0%, #121a24 100%);
            color: #e1e5eb;
        }
        
        h1, h2, h3 {
            color: #e1e5eb;
        }
        
        .document-tab {
            background-color: rgba(30, 41, 59, 0.8);
            border: 1px solid rgba(50, 60, 80, 0.5);
        }
        
        .timeline-content {
            background: linear-gradient(to bottom right, #1c2331, #121a24);
            color: #e1e5eb;
        }
        
        .history-container {
            background: linear-gradient(to bottom, #1c2331, #121a24);
            border-color: #2a3441;
        }
        
        .history-item {
            background-color: #1e293b;
            color: #e1e5eb;
        }
        
        .stTextInput>div>div>input,
        .stTextArea>div>div>textarea, 
        .stSelectbox>div>div>div {
            background-color: rgba(30, 41, 59, 0.8);
            border-color: #2a3441;
            color: #e1e5eb;
        }
    }
    
    /* UI animations and interactions for legal document elements */
    .contract-section {
        margin-bottom: 20px;
        padding: 15px;
        border-radius: 8px;
        background-color: #fff;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        position: relative;
        overflow: hidden;
        transition: all 0.3s;
    }
    
    .contract-section::before {
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        height: 100%;
        width: 5px;
        background-color: #1a3c5a;
        transform: scaleY(0);
        transition: transform 0.3s ease;
    }
    
    .contract-section:hover {
        transform: translateX(5px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.15);
    }
    
    .contract-section:hover::before {
        transform: scaleY(1);
    }
    
    .contract-heading {
        font-family: 'Playfair Display', serif;
        color: #1a3c5a;
        border-bottom: 2px solid #e9ecef;
        padding-bottom: 10px;
        margin-bottom: 15px;
        position: relative;
    }
    
    .contract-content {
        line-height: 1.6;
        color: #495057;
    }
    
    /* Signature line animation */
    .signature-line {
        display: block;
        width: 100%;
        height: 1px;
        background-color: #000;
        margin: 15px 0;
        position: relative;
    }
    
    .signature-line::after {
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        width: 0;
        height: 100%;
        background-color: #1a3c5a;
        transition: width 1.5s ease;
    }
    
    .signature-line:hover::after {
        width: 100%;
    }
    
    /* Party labels in contracts */
    .party-label {
        display: inline-block;
        background-color: rgba(26, 60, 90, 0.1);
        padding: 3px 8px;
        border-radius: 4px;
        font-weight: 500;
        color: #1a3c5a;
        margin-right: 5px;
        transition: all 0.2s;
    }
    
    .party-label:hover {
        background-color: rgba(26, 60, 90, 0.2);
        transform: translateY(-2px);
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    
    /* Enhanced form inputs for legal information */
    .legal-form-group {
        margin-bottom: 20px;
        position: relative;
    }
    
    .legal-form-label {
        display: block;
        margin-bottom: 8px;
        font-weight: 500;
        color: #1a3c5a;
        transition: all 0.3s;
    }
    
    .legal-form-input {
        width: 100%;
        padding: 12px 15px;
        border: 2px solid #e1e5eb;
        border-radius: 8px;
        font-size: 16px;
        transition: all 0.3s;
    }
    
    .legal-form-input:focus {
        border-color: #1a3c5a;
        box-shadow: 0 0 0 2px rgba(26, 60, 90, 0.2);
        outline: none;
    }
    
    .legal-form-input:focus + .legal-form-label {
        color: #2a5a85;
        transform: translateY(-25px) scale(0.8);
    }
    
    /* Loading states and transitions */
    .analysis-loading {
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 20px;
    }
    
    .loading-dot {
        width: 10px;
        height: 10px;
        background-color: #1a3c5a;
        border-radius: 50%;
        margin: 0 5px;
        animation: bounce 1.5s infinite ease-in-out;
    }
    
    .loading-dot:nth-child(1) {animation-delay: 0s;}
    .loading-dot:nth-child(2) {animation-delay: 0.2s;}
    .loading-dot:nth-child(3) {animation-delay: 0.4s;}
    
    @keyframes bounce {
        0%, 80%, 100% {transform: scale(0);}
        40% {transform: scale(1);}
    }
    
    /* Help tooltips for legal terms */
    .legal-tooltip {
        position: relative;
        display: inline-block;
        border-bottom: 1px dotted #1a3c5a;
        cursor: help;
    }
    
    .legal-tooltip .tooltip-text {
        visibility: hidden;
        width: 300px;
        background-color: #1a3c5a;
        color: #fff;
        text-align: center;
        border-radius: 6px;
        padding: 10px;
        position: absolute;
        z-index: 1;
        bottom: 125%;
        left: 50%;
        transform: translateX(-50%);
        opacity: 0;
        transition: opacity 0.3s;
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    }
    
    .legal-tooltip:hover .tooltip-text {
        visibility: visible;
        opacity: 1;
    }
    
    /* Evidence and Exhibits styling */
    .exhibit-container {
        border-left: 3px solid #1a3c5a;
        padding-left: 15px;
        margin: 20px 0;
        background-color: rgba(26, 60, 90, 0.05);
        padding: 15px;
        border-radius: 0 8px 8px 0;
        transition: all 0.3s;
    }
    
    .exhibit-container:hover {
        background-color: rgba(26, 60, 90, 0.1);
        transform: translateX(5px);
    }
    
    .exhibit-label {
        font-weight: 700;
        color: #1a3c5a;
        display: block;
        margin-bottom: 10px;
    }
    
    .exhibit-content {
        font-style: italic;
        color: #495057;
    }
    
    /* Contract template with elegant styling - fixed layout */
    .contract-template {
        padding: 30px;
        background-color: #f8f8f8;
        background-image: linear-gradient(45deg, #f9f9f9 25%, transparent 25%, transparent 75%, #f9f9f9 75%, #f9f9f9), 
                        linear-gradient(45deg, #f9f9f9 25%, transparent 25%, transparent 75%, #f9f9f9 75%, #f9f9f9);
        background-size: 20px 20px;
        background-position: 0 0, 10px 10px;
        border: 1px solid #ddd;
        border-radius: 8px;
        font-family: 'Playfair Display', serif;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        margin-bottom: 25px;
        width: 100%;
        box-sizing: border-box;
        overflow: auto;
    }

    /* Fix contract section styling */
    .contract-section {
        margin-bottom: 20px;
        padding: 15px;
        border-radius: 8px;
        background-color: rgba(255, 255, 255, 0.9);
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        position: relative;
        overflow: hidden;
        transition: all 0.3s;
        width: 100%;
        box-sizing: border-box;
    }

    /* Enhanced loading indicator */
    .loading-container {
        width: 100%;
        padding: 30px;
        text-align: center;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
    }

    .loading-dot {
        width: 20px;
        height: 20px;
        background: linear-gradient(135deg, #1a3c5a 0%, #2a5a85 100%);
        border-radius: 50%;
        margin: 0 10px;
        display: inline-block;
        animation: bounce 1.5s infinite ease-in-out;
    }

    @keyframes bounce {
        0%, 80%, 100% {transform: translateY(0) scale(0.8);}
        40% {transform: translateY(-20px) scale(1);}
    }
    </style>
    """, unsafe_allow_html=True)

INDIAN_LANGUAGES = {
    "English": "en",
    "Hindi (हिन्दी)": "hi",
    "Tamil (தமிழ்)": "ta",
    "Telugu (తెలుగు)": "te",
    "Kannada (ಕನ್ನಡ)": "kn",
    "Malayalam (മലയാളം)": "ml",
    "Marathi (मराठी)": "mr",
    "Gujarati (ગુજરાતી)": "gu",
    "Bengali (বাংলা)": "bn",
    "Punjabi (ਪੰਜਾਬੀ)": "pa",
    "Odia (ଓଡ଼ିଆ)": "or",
    "Urdu (اردو)": "ur"
}

def translate_text(text, target_lang):
    """Translate text into the selected Indian language with error handling."""
    if target_lang == "en" or not text:
        return text
    
    try:
        # Split long text into smaller chunks to avoid translation errors
        max_chunk_length = 5000
        if len(text) > max_chunk_length:
            chunks = []
            for i in range(0, len(text), max_chunk_length):
                chunks.append(text[i:i+max_chunk_length])
            
            translated_chunks = []
            for chunk in chunks:
                translated_chunks.append(translator.translate(chunk, dest=target_lang).text)
            
            return "".join(translated_chunks)
        else:
            return translator.translate(text, dest=target_lang).text
    except Exception as e:
        print(f"Translation error: {str(e)}")
        return text  # Return original text if translation fails



def translate_ui_text(text_dict, target_lang):
    """Translate a dictionary of UI text elements to target language."""
    if target_lang == "en":
        return text_dict
    
    translated_dict = {}
    for key, text in text_dict.items():
        translated_dict[key] = translate_text(text, target_lang)
    
    return translated_dict

# Dictionary of UI text for translation
UI_TEXT = {
    "app_title": "Legal Assistant Pro",
    "chat_tab": "Chat",
    "document_analysis_tab": "Document Analysis",
    "contract_generator_tab": "Contract Generator",
    "history_tab": "History",
    "settings": "Settings & Tools",
    "language": "Choose Language:",
    "document_processing": "Document Processing",
    "upload_docs": "Upload your PDF Files",
    "process_button": "Process Documents",
    "processing_complete": "Processing complete. Ready for Q&A.",
    "ask_question": "Ask about your legal documents",
    "question_placeholder": "Ask your question...",
    "document_preview": "Document Preview:",
    "analyze_button": "Analyze Document",
    "key_info": "Key Information",
    "timeline": "Timeline of Events",
    "risk_assessment": "Risk Assessment",
    "legal_entities": "Legal Entities",
    "obligations": "Obligations Summary",
    "timeline_analysis": "Timeline Analysis",
    "legal_entities_info": "Legal Entities and Key Information",
    "select_contract": "Select contract type:",
    "employment_agreement": "Employment Agreement",
    "lease_agreement": "Lease Agreement",
    "nda": "Non-Disclosure Agreement (NDA)",
    "custom_contract": "Custom Contract",
    "employer_name": "Employer Name:",
    "employer_address": "Employer Address:",
    "agreement_date": "Agreement Date:",
    "employee_name": "Employee Name:",
    "employee_address": "Employee Address:",
    "position_title": "Position Title:",
    "landlord_name": "Landlord Name:",
    "landlord_address": "Landlord Address:",
    "tenant_name": "Tenant Name:",
    "tenant_address": "Tenant Address:",
    "property_description": "Property Description:",
    "party1_name": "First Party Name:",
    "party1_address": "First Party Address:",
    "party2_name": "Second Party Name:",
    "party2_address": "Second Party Address:",
    "purpose_disclosure": "Purpose of Disclosure:",
    "contract_description": "Describe the contract you need:",
    "parties_involved": "List parties involved (separated by comma):",
    "governing_law": "Governing Law:",
    "generate_contract": "Generate Contract",
    "generated_contract": "Generated Contract",
    "preview": "Preview:",
    "download_txt": "Download Text",
    "download_docx": "Download Word",
    "download_pdf": "Download PDF",
    "chat_history": "Chat History",
    "clear_history": "Clear History",
    "history_cleared": "Chat history cleared",
    "error_processing": "Error processing your question:",
    "try_again": "Try uploading and processing your documents again.",
    "upload_first": "Please upload and process documents first to enable analysis",
    "no_history": "No chat history found"
}

def get_pdf_text(pdf_docs):
    """Extract text from uploaded PDFs with unicode error handling."""
    text = ""
    for pdf in pdf_docs:
        pdf_reader = PdfReader(pdf)
        for page in pdf_reader.pages:
            try:
                page_text = page.extract_text()
                if page_text:
                    # Clean text of problematic unicode characters
                    page_text = clean_text(page_text)
                    text += page_text + "\n"
            except Exception as e:
                st.warning(f"Error extracting text from a page: {str(e)}")
    return text

def clean_text(text):
    """Clean text of problematic unicode characters."""
    if not text:
        return ""
    
    # Replace problematic unicode characters
    cleaned = ""
    for char in text:
        try:
            # Test if character can be encoded
            char.encode('utf-8')
            cleaned += char
        except UnicodeEncodeError:
            # Replace problematic character with a space or similar
            cleaned += " "
    return cleaned

def get_text_chunks(text):
    """Split text into chunks for vector storage."""
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=10000, chunk_overlap=1000)
    return text_splitter.split_text(text)

def get_vector_store(text_chunks):
    """Create FAISS vector store from text chunks with error handling."""
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    
    # Process in smaller batches to avoid issues with very large documents
    vector_store = None
    batch_size = 100  # Adjust based on your needs
    
    try:
        for i in range(0, len(text_chunks), batch_size):
            batch = text_chunks[i:i+batch_size]
            
            # Process this batch
            try:
                if vector_store is None:
                    vector_store = FAISS.from_texts(batch, embedding=embeddings)
                else:
                    batch_vectors = FAISS.from_texts(batch, embedding=embeddings)
                    vector_store.merge_from(batch_vectors)
                
                # Show progress
                progress = min(100, int((i + batch_size) / len(text_chunks) * 100))
                st.progress(progress / 100)
                
            except UnicodeEncodeError as e:
                st.warning(f"Unicode error in batch {i//batch_size + 1}. Cleaning batch and retrying.")
                # Clean the batch more aggressively
                cleaned_batch = [clean_text_aggressive(chunk) for chunk in batch]
                
                if vector_store is None:
                    vector_store = FAISS.from_texts(cleaned_batch, embedding=embeddings)
                else:
                    batch_vectors = FAISS.from_texts(cleaned_batch, embedding=embeddings)
                    vector_store.merge_from(batch_vectors)
        
        # Save the vector store
        if vector_store:
            vector_store.save_local("faiss_index")
            return True
        return False
    
    except Exception as e:
        st.error(f"Error creating vector store: {str(e)}")
        return False

def clean_text_aggressive(text):
    """More aggressive text cleaning for problematic chunks."""
    if not text:
        return ""
    
    # Replace all non-ASCII characters with spaces
    return ''.join(c if ord(c) < 128 else ' ' for c in text)

def get_conversational_chain():
    """Initialize Gemini conversational chain."""
    prompt_template = """
    Answer the question as detailed as possible from the provided context. 
    If the answer is not in the provided context, respond with "answer is not available in the context".
    
    Context:\n {context}\n
    Question: \n{question}\n
    Answer:
    """
    model = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.3)
    prompt = PromptTemplate(template=prompt_template, input_variables=["context", "question"])
    return load_qa_chain(model, chain_type="stuff", prompt=prompt)

# Update user_input function to use new styling
def user_input(user_question, target_lang):
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

    # Ensure FAISS index exists
    if not os.path.exists("faiss_index"):
        st.error("No FAISS index found. Please upload and process PDFs first.")
        return

    # Load FAISS index safely
    new_db = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)
    
    docs = new_db.similarity_search(user_question)
    chain = get_conversational_chain()
    
    with st.status("Processing your question...", expanded=True) as status:
        st.write("Searching through documents...")
        response = chain({"input_documents": docs, "question": user_question}, return_only_outputs=True)
        reply = response.get("output_text", "No response generated.")
        
        st.write("Translating response...")
        translated_reply = translate_text(reply, target_lang)
        status.update(label="Complete!", state="complete")
    
    # Display in custom message container
    st.markdown(
        f'<div class="chat-message user"><div class="message-content"><b>{translate_text("You", target_lang)}:</b> {user_question}</div></div>', 
        unsafe_allow_html=True
    )
    
    # Add a small delay for visual effect
    import time
    time.sleep(0.5)
    
    st.markdown(
        f'<div class="chat-message bot"><div class="message-content"><b>{translate_text("Legal Assistant", target_lang)}:</b> {translated_reply}</div></div>', 
        unsafe_allow_html=True
    )
    
    # Save to history
    save_chat_history(user_question, translated_reply)
    
    return reply

# Chat history management function
def save_chat_history(question, answer):
    """Save chat interaction to history file"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    history_item = {
        "timestamp": timestamp,
        "question": question,
        "answer": answer
    }
    
    # Create directory if it doesn't exist
    os.makedirs("history", exist_ok=True)
    
    history_file = "history/chat_history.json"
    try:
        if os.path.exists(history_file):
            with open(history_file, "r") as f:
                history = json.load(f)
        else:
            history = []
            
        history.append(history_item)
        
        with open(history_file, "w") as f:
            json.dump(history, f, indent=4)
    except Exception as e:
        st.error(f"Error saving history: {str(e)}")

def get_chat_history():
    """Retrieve chat history from file"""
    history_file = "history/chat_history.json"
    if os.path.exists(history_file):
        try:
            with open(history_file, "r") as f:
                return json.load(f)
        except:
            return []
    return []

def display_chat_history():
    """Display chat history in the UI"""
    history = get_chat_history()
    
    if not history:
        st.info("No chat history found")
        return
        
    st.markdown("<div class='history-container'>", unsafe_allow_html=True)
    
    for item in reversed(history):  # Most recent first
        st.markdown(
            f"<div class='history-item'>"
            f"<small>{item['timestamp']}</small><br>"
            f"<strong>Q: {item['question']}</strong><br>"
            f"A: {item['answer'][:100]}{'...' if len(item['answer']) > 100 else ''}"
            f"</div>", 
            unsafe_allow_html=True
        )
    
    st.markdown("</div>", unsafe_allow_html=True)

def extract_timeline(document_text):
    """Extract a chronological timeline of events from legal document with proper formatting."""
    prompt = """
    Extract a chronological timeline of key events from this legal document.
    For each event, provide:
    1. Date (if available)
    2. Event description
    3. Relevant parties involved
    4. Page reference (if available)
    
    Format EXACTLY as a JSON array of objects with the following keys:
    [
      {
        "date": "YYYY-MM-DD or textual date",
        "description": "Description of the event",
        "parties": "Parties involved",
        "page": "Page reference"
      },
      ...
    ]
    
    Ensure your output is valid JSON only, with no additional text before or after.
    
    Document text:
    {text}
    """
    
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt.format(text=document_text[:50000]))
        
        # Try to parse as JSON
        try:
            # Strip any extra text or formatting that might be around the JSON
            response_text = response.text.strip()
            
            # Find the start and end of what looks like a JSON array
            if '[' in response_text and ']' in response_text:
                start = response_text.find('[')
                end = response_text.rfind(']') + 1
                json_str = response_text[start:end]
                
                # Parse the JSON
                timeline_data = json.loads(json_str)
                return timeline_data
            else:
                return response.text
        except json.JSONDecodeError:
            # If not valid JSON, return the raw text
            return response.text
    except Exception as e:
        return f"Error extracting timeline: {str(e)}"

def extract_legal_entities(document_text):
    """Extract key legal entities and information from the document."""
    prompt = """
    Extract key legal entities and information from this document. Include:
    
    1. All named parties (individuals and organizations)
    2. Key dates and deadlines
    3. Monetary values and financial terms
    4. Property or asset descriptions
    5. Legal obligations and requirements
    
    Format the response as structured JSON with these categories as keys, and lists of extracted items as values.
    Only return the JSON, no additional text.
    
    Document text:
    {text}
    """
    
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt.format(text=document_text[:50000]))
        
        # Parse the JSON response
        try:
            # Extract only the JSON part if there's other text
            response_text = response.text
            if '{' in response_text and '}' in response_text:
                start = response_text.find('{')
                end = response_text.rfind('}') + 1
                json_str = response_text[start:end]
                return json.loads(json_str)
            else:
                return {"error": "Could not extract structured data"}
        except json.JSONDecodeError:
            return {"error": "Invalid JSON response", "raw": response.text[:500]}
    except Exception as e:
        return {"error": f"Error extracting entities: {str(e)}"}

def display_timeline(timeline_data):
    """Display timeline in a visually appealing format."""
    if isinstance(timeline_data, list):
        # It's properly formatted JSON
        st.markdown("<div class='timeline-container'>", unsafe_allow_html=True)
        
        for i, event in enumerate(timeline_data):
            date = event.get('date', 'No date')
            description = event.get('description', 'No description')
            parties = event.get('parties', 'Not specified')
            page = event.get('page', 'N/A')
            
            position = "left" if i%2==0 else "right"
            
            # Fix timeline CSS layout issues
            st.markdown(
                f"""
                <div class='timeline-item {position}' style='clear: both;'>
                    <div class='timeline-content' style='width: 100%; box-sizing: border-box;'>
                        <div class='timeline-date'>{date}</div>
                        <h4>{description}</h4>
                        <p><strong>Parties:</strong> {parties}</p>
                        <p><strong>Page:</strong> {page}</p>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
        
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        # It's raw text
        st.markdown("### Timeline")
        st.text_area("Timeline extraction result:", timeline_data, height=300)

def generate_contract_template(context_info):
    """Generate a contract template based on user input."""
    contract_types = {
        "employment": """
        EMPLOYMENT AGREEMENT

        This Employment Agreement (the "Agreement") is made and entered into as of [DATE], by and between:

        EMPLOYER: [EMPLOYER_NAME], with its principal place of business at [EMPLOYER_ADDRESS] ("Employer")

        EMPLOYEE: [EMPLOYEE_NAME], residing at [EMPLOYEE_ADDRESS] ("Employee")

        1. POSITION AND DUTIES
        [POSITION_DETAILS]

        2. TERM OF EMPLOYMENT
        [TERM_DETAILS]

        3. COMPENSATION AND BENEFITS
        [COMPENSATION_DETAILS]

        4. TERMINATION
        [TERMINATION_DETAILS]

        5. CONFIDENTIALITY
        [CONFIDENTIALITY_DETAILS]

        6. NON-COMPETE
        [NON_COMPETE_DETAILS]

        7. GOVERNING LAW
        This Agreement shall be governed by and construed in accordance with the laws of [JURISDICTION].

        IN WITNESS WHEREOF, the parties hereto have executed this Agreement as of the date first above written.

        ________________________
        [EMPLOYER_NAME]
        By: [AUTHORIZED_SIGNATORY]
        Title: [TITLE]

        ________________________
        [EMPLOYEE_NAME]
        """,
        
        "lease": """
        LEASE AGREEMENT

        This Lease Agreement (the "Lease") is made and entered into as of [DATE], by and between:

        LANDLORD: [LANDLORD_NAME], with an address of [LANDLORD_ADDRESS] ("Landlord")

        TENANT: [TENANT_NAME], with an address of [TENANT_ADDRESS] ("Tenant")

        1. PREMISES
        [PROPERTY_DETAILS]

        2. TERM
        [LEASE_TERM]

        3. RENT
        [RENT_DETAILS]

        4. SECURITY DEPOSIT
        [DEPOSIT_DETAILS]

        5. UTILITIES AND SERVICES
        [UTILITIES_DETAILS]

        6. MAINTENANCE AND REPAIRS
        [MAINTENANCE_DETAILS]

        7. DEFAULT
        [DEFAULT_DETAILS]

        8. GOVERNING LAW
        This Lease shall be governed by and construed in accordance with the laws of [JURISDICTION].

        IN WITNESS WHEREOF, the parties hereto have executed this Lease as of the date first above written.

        ________________________
        [LANDLORD_NAME]

        ________________________
        [TENANT_NAME]
        """,
        
        "nda": """
        NON-DISCLOSURE AGREEMENT

        This Non-Disclosure Agreement (the "Agreement") is made and entered into as of [DATE], by and between:

        PARTY 1: [PARTY1_NAME], with its principal place of business at [PARTY1_ADDRESS] ("Disclosing Party")

        PARTY 2: [PARTY2_NAME], with its principal place of business at [PARTY2_ADDRESS] ("Receiving Party")

        1. PURPOSE
        [PURPOSE_DETAILS]

        2. DEFINITION OF CONFIDENTIAL INFORMATION
        [CONFIDENTIAL_INFO_DETAILS]

        3. OBLIGATIONS OF RECEIVING PARTY
        [OBLIGATIONS_DETAILS]

        4. TERM
        [TERM_DETAILS]

        5. REMEDIES
        [REMEDIES_DETAILS]

        6. GOVERNING LAW
        This Agreement shall be governed by and construed in accordance with the laws of [JURISDICTION].

        IN WITNESS WHEREOF, the parties hereto have executed this Agreement as of the date first above written.

        ________________________
        [PARTY1_NAME]
        By: [AUTHORIZED_SIGNATORY1]
        Title: [TITLE1]

        ________________________
        [PARTY2_NAME]
        By: [AUTHORIZED_SIGNATORY2]
        Title: [TITLE2]
        """
    }
    
    # Fill template with context
    contract_type = context_info.get("contract_type", "employment")
    template = contract_types.get(contract_type, contract_types["employment"])
    
    # Basic replacements
    for key, value in context_info.items():
        placeholder = f"[{key.upper()}]"
        if placeholder in template:
            template = template.replace(placeholder, value)
    
    # Generate remaining sections using AI
    remaining_placeholders = [p for p in re.findall(r'\[(.*?)\]', template)]
    if remaining_placeholders:
        try:
            # Generate content for remaining placeholders
            model = genai.GenerativeModel('gemini-1.5-flash')
            for placeholder in remaining_placeholders:
                prompt = f"Generate appropriate legal language for the {placeholder} section of a {contract_type} contract."
                response = model.generate_content(prompt)
                template = template.replace(f"[{placeholder}]", response.text)
        except Exception as e:
            pass  # Keep placeholder if generation fails
    
    return template

def generate_structured_contract(template_type, context_info):
    """Generate a structured contract based on template and context information."""
    # Basic contract templates with formatting
    templates = {
        "employment": {
            "title": "EMPLOYMENT AGREEMENT",
            "sections": [
                {"heading": "PARTIES", "content": """
This Employment Agreement (the "Agreement") is made and entered into as of {date}, by and between:

EMPLOYER: {employer_name}, with its principal place of business at {employer_address} ("Employer")

EMPLOYEE: {employee_name}, residing at {employee_address} ("Employee")
                """},
                {"heading": "POSITION AND DUTIES", "content": """
Employer hereby employs Employee as {position}, and Employee accepts such employment, on the terms and conditions set forth in this Agreement. Employee shall perform such duties as are customarily performed by others in similar positions at Employer, as well as such other duties as may be assigned from time to time by Employer.
                """},
                {"heading": "TERM OF EMPLOYMENT", "content": """
The term of this Agreement shall commence on {date} and shall continue until terminated in accordance with the provisions of this Agreement.
                """},
                {"heading": "COMPENSATION AND BENEFITS", "content": """
Employee shall be paid a base salary of [SALARY_AMOUNT] per [PAY_PERIOD], subject to applicable withholdings and deductions.

Employee shall be eligible to participate in Employer's employee benefit plans as may be in effect from time to time.
                """},
                {"heading": "GOVERNING LAW", "content": """
This Agreement shall be governed by and construed in accordance with the laws of {jurisdiction}.
                """},
                {"heading": "SIGNATURES", "content": """
IN WITNESS WHEREOF, the parties hereto have executed this Agreement as of the date first above written.

________________________
{employer_name}

________________________
{employee_name}
                """}
            ]
        },
        "nda": {
            "title": "NON-DISCLOSURE AGREEMENT",
            "sections": [
                {"heading": "PARTIES", "content": """
This Non-Disclosure Agreement (the "Agreement") is made and entered into as of {date}, by and between:

PARTY 1: {party1_name}, with its principal place of business at {party1_address} ("Disclosing Party")

PARTY 2: {party2_name}, with its principal place of business at {party2_address} ("Receiving Party")
                """},
                {"heading": "PURPOSE", "content": """
{purpose_details}
                """},
                {"heading": "DEFINITION OF CONFIDENTIAL INFORMATION", "content": """
"Confidential Information" means any information disclosed by Disclosing Party to Receiving Party, either directly or indirectly, in writing, orally or by inspection of tangible objects, which is designated as "Confidential," "Proprietary" or some similar designation, or that should reasonably be understood to be confidential given the nature of the information and the circumstances of disclosure.
                """},
                {"heading": "OBLIGATIONS OF RECEIVING PARTY", "content": """
Receiving Party shall hold the Confidential Information in strict confidence and shall not disclose such Confidential Information to any third party. Receiving Party shall protect the confidentiality of the Confidential Information using at least the same degree of care it uses to protect its own confidential information, but no less than reasonable care.
                """},
                {"heading": "GOVERNING LAW", "content": """
This Agreement shall be governed by and construed in accordance with the laws of {jurisdiction}.
                """},
                {"heading": "SIGNATURES", "content": """
IN WITNESS WHEREOF, the parties hereto have executed this Agreement as of the date first above written.

________________________
{party1_name}

________________________
{party2_name}
                """}
            ]
        },
        "lease": {
            "title": "LEASE AGREEMENT",
            "sections": [
                {"heading": "PARTIES", "content": """
This Lease Agreement (the "Lease") is made and entered into as of {date}, by and between:

LANDLORD: {landlord_name}, with an address of {landlord_address} ("Landlord")

TENANT: {tenant_name}, with an address of {tenant_address} ("Tenant")
                """},
                {"heading": "PREMISES", "content": """
{property_details}
                """},
                {"heading": "TERM", "content": """
The term of this Lease shall commence on {date} and shall continue for a period of [LEASE_DURATION], unless sooner terminated in accordance with the provisions of this Lease.
                """},
                {"heading": "RENT", "content": """
Tenant shall pay to Landlord as rent for the Premises the sum of [RENT_AMOUNT] per month, payable in advance on the first day of each month during the term of this Lease.
                """},
                {"heading": "GOVERNING LAW", "content": """
This Lease shall be governed by and construed in accordance with the laws of {jurisdiction}.
                """},
                {"heading": "SIGNATURES", "content": """
IN WITNESS WHEREOF, the parties hereto have executed this Lease as of the date first above written.

________________________
{landlord_name}

________________________
{tenant_name}
                """}
            ]
        }
    }
    
    # Select the appropriate template
    template = templates.get(template_type)
    if not template:
        return "Template type not found."
    
    # Build the contract
    contract = template["title"] + "\n\n"
    
    for section in template["sections"]:
        contract += section["heading"] + "\n\n"
        # Format the content with context info
        content = section["content"]
        for key, value in context_info.items():
            if isinstance(value, str) and value.strip():
                content = content.replace("{" + key + "}", value)
        contract += content.strip() + "\n\n"
    
    # Fill in any remaining placeholders with AI-generated content
    placeholders = re.findall(r'\[(.*?)\]', contract)
    if placeholders:
        try:
            model = genai.GenerativeModel('gemini-1.5-flash')
            for placeholder in placeholders:
                # Add instructions to avoid markdown formatting
                prompt = f"""Generate appropriate legal language for {placeholder} in a {template_type} contract.
                
                IMPORTANT: DO NOT include any markdown formatting symbols like asterisks (*), 
                greater-than symbols (>), or bullet points. Return ONLY clean, plain text suitable 
                for direct inclusion in a legal document. Do not include 'Option 1/2/3' language or disclaimers.
                Keep your response concise and formal in legal language (2-3 sentences maximum)."""
                
                response = model.generate_content(prompt)
                
                # Clean up the response to remove any remaining markdown
                cleaned_response = response.text
                cleaned_response = re.sub(r'[*>•\-]', '', cleaned_response)
                cleaned_response = re.sub(r'Option \d+[:\)]', '', cleaned_response)
                cleaned_response = cleaned_response.replace('', '').strip()
                
                contract = contract.replace(f"[{placeholder}]", cleaned_response)
        except Exception as e:
            # Keep placeholders if generation fails
            print(f"Error generating content: {str(e)}")
    
    return contract

def download_document(document_text, filename="legal_document.txt"):
    """Create a download link for a document with proper formatting"""
    file_ext = filename.split('.')[-1].lower()
    
    if file_ext == 'docx':
        try:
            from docx import Document
            from docx.shared import Pt, Inches
            from docx.enum.text import WD_ALIGN_PARAGRAPH
            
            # Create a professional Word document
            doc = Document()
            
            # Set margins
            sections = doc.sections
            for section in sections:
                section.top_margin = Inches(1)
                section.bottom_margin = Inches(1)
                section.left_margin = Inches(1)
                section.right_margin = Inches(1)
            
            # Add title
            title = doc.add_heading('', 0)
            title_run = title.add_run("LEGAL DOCUMENT")
            title_run.bold = True
            title.alignment = WD_ALIGN_PARAGRAPH.CENTER
            
            # Add content with proper formatting
            paragraphs = document_text.split('\n')
            for para in paragraphs:
                if para.strip():
                    if para.strip().isupper() and len(para.strip()) < 50:  # Likely a heading
                        p = doc.add_heading(para.strip(), level=1)
                        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    else:
                        p = doc.add_paragraph(para)
                        # Check if this is a signature line
                        if "" in para:
                            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            
            # Save to BytesIO object
            docx_bytes = io.BytesIO()
            doc.save(docx_bytes)
            docx_bytes.seek(0)
            file_bytes = docx_bytes.getvalue()
            mime_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        except ImportError:
            # Fall back to text if python-docx is not installed
            file_bytes = document_text.encode()
            mime_type = "text/plain"
            
    elif file_ext == 'pdf':
        try:
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import letter
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
            from reportlab.lib.units import inch
            
            # Create a PDF with professional formatting
            buffer = io.BytesIO()
            
            # Set up the document
            doc = SimpleDocTemplate(
                buffer,
                pagesize=letter,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=72
            )
            
            # Define styles - FIX: Don't redefine existing styles
            styles = getSampleStyleSheet()
            
            # Create a custom heading style instead of modifying the built-in one
            heading_style = ParagraphStyle(
                name='CustomHeading',
                parent=styles['Heading1'],
                alignment=1,  # Center alignment
                spaceAfter=12
            )
            
            body_style = ParagraphStyle(
                name='CustomBody',
                parent=styles['BodyText'],
                spaceBefore=6,
                spaceAfter=6
            )
            
            # Process content
            content = []
            content.append(Paragraph("LEGAL DOCUMENT", heading_style))
            content.append(Spacer(1, 0.25*inch))
            
            # Break text into paragraphs
            paragraphs = document_text.split('\n')
            for para in paragraphs:
                if not para.strip():
                    content.append(Spacer(1, 0.1*inch))
                    continue
                    
                if para.strip().isupper() and len(para.strip()) < 50:  # Likely a heading
                    content.append(Spacer(1, 0.1*inch))
                    content.append(Paragraph(para, heading_style))
                else:
                    # Escape any special characters in the paragraph text
                    para_text = para.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                    content.append(Paragraph(para_text, body_style))
            
            # Build the PDF
            doc.build(content)
            
            buffer.seek(0)
            file_bytes = buffer.getvalue()
            mime_type = "application/pdf"
        except Exception as e:
            # Fall back to text with error information
            file_bytes = f"PDF generation failed: {str(e)}\n\n{document_text}".encode()
            mime_type = "text/plain"
    else:
        # Default to text file
        file_bytes = document_text.encode()
        mime_type = "text/plain"
    
    b64 = base64.b64encode(file_bytes).decode()
    href = f'<a href="data:{mime_type};base64,{b64}" download="{filename}" class="download-button">Download {filename}</a>'
    return href

def show_contract_preview(context_info, contract_type):
    """Show interactive contract preview as user inputs data"""
    try:
        # Check if we have the minimum required information
        has_required_info = False
        if contract_type == "employment" and context_info.get("employer_name"):
            has_required_info = True
        elif contract_type == "nda" and context_info.get("party1_name"):
            has_required_info = True
        elif contract_type == "lease" and context_info.get("landlord_name"):
            has_required_info = True
            
        if not has_required_info:
            return
        
        st.markdown("### Live Contract Preview")
        
        # Show only the first part of the contract in the preview
        if contract_type == "employment":
            preview_html = f"""
            <div class='contract-section'>
                <h4 class='contract-heading'>EMPLOYMENT AGREEMENT</h4>
                <div class='contract-content'>
                    This Employment Agreement (the "Agreement") is made and entered into as of {context_info.get("date", "[DATE]")}, by and between:
                    
                    <p><span class='party-label'>EMPLOYER</span>: <strong>{context_info.get("employer_name", "[EMPLOYER NAME]")}</strong>, 
                    with its principal place of business at {context_info.get("employer_address", "[ADDRESS]")} ("Employer")</p>
                    
                    <p><span class='party-label'>EMPLOYEE</span>: <strong>{context_info.get("employee_name", "[EMPLOYEE NAME]")}</strong>, 
                    residing at {context_info.get("employee_address", "[ADDRESS]")} ("Employee")</p>
                    
                    <p>Employer hereby employs Employee as <strong>{context_info.get("position", "[POSITION]")}</strong>, and Employee accepts such employment, on the terms and conditions set forth in this Agreement.</p>
                </div>
            </div>
            """
        elif contract_type == "nda":
            preview_html = f"""
            <div class='contract-section'>
                <h4 class='contract-heading'>NON-DISCLOSURE AGREEMENT</h4>
                <div class='contract-content'>
                    This Non-Disclosure Agreement (the "Agreement") is made and entered into as of {context_info.get("date", "[DATE]")}, by and between:
                    
                    <p><span class='party-label'>PARTY 1</span>: <strong>{context_info.get("party1_name", "[PARTY 1 NAME]")}</strong>, 
                    with its principal place of business at {context_info.get("party1_address", "[ADDRESS]")} ("Disclosing Party")</p>
                    
                    <p><span class='party-label'>PARTY 2</span>: <strong>{context_info.get("party2_name", "[PARTY 2 NAME]")}</strong>, 
                    with its principal place of business at {context_info.get("party2_address", "[ADDRESS]")} ("Receiving Party")</p>
                    
                    <p><strong>PURPOSE:</strong> {context_info.get("purpose_details", "[PURPOSE OF DISCLOSURE]")}</p>
                </div>
            </div>
            """
        elif contract_type == "lease":
            preview_html = f"""
            <div class='contract-section'>
                <h4 class='contract-heading'>LEASE AGREEMENT</h4>
                <div class='contract-content'>
                    This Lease Agreement (the "Lease") is made and entered into as of {context_info.get("date", "[DATE]")}, by and between:
                    
                    <p><span class='party-label'>LANDLORD</span>: <strong>{context_info.get("landlord_name", "[LANDLORD NAME]")}</strong>, 
                    with an address of {context_info.get("landlord_address", "[ADDRESS]")} ("Landlord")</p>
                    
                    <p><span class='party-label'>TENANT</span>: <strong>{context_info.get("tenant_name", "[TENANT NAME]")}</strong>, 
                    with an address of {context_info.get("tenant_address", "[ADDRESS]")} ("Tenant")</p>
                    
                    <p><strong>PREMISES:</strong> {context_info.get("property_details", "[PROPERTY DETAILS]")}</p>
                </div>
            </div>
            """
        
        # Wrap the preview in the contract template container
        st.markdown(f"<div class='contract-template'>{preview_html}</div>", unsafe_allow_html=True)
        
    except Exception as e:
        st.error(f"Error showing preview: {str(e)}")

# Add a custom loading spinner component
def show_custom_spinner(message="Processing..."):
    with st.container():
        col1, col2, col3 = st.columns([1, 3, 1])
        with col2:
            st.markdown("""
            <div class="loading-container" style="text-align: center;">
                <div style="display: flex; justify-content: center; margin-bottom: 20px;">
                    <div class="loading-dot" style="animation-delay: 0s;"></div>
                    <div class="loading-dot" style="animation-delay: 0.2s;"></div>
                    <div class="loading-dot" style="animation-delay: 0.4s;"></div>
                </div>
                <p>{}</p>
            </div>
            """.format(message), unsafe_allow_html=True)

def main():
    """Main Streamlit UI for PDF Chatbot with translation support."""
    st.set_page_config(page_title="Legal Assist", page_icon="⚖", layout="wide")
    load_css()
    
    # Get language preference
    if 'language' not in st.session_state:
        st.session_state.language = "en"
    
    # Sidebar for language selection (keep this at the top)
    with st.sidebar:
        target_lang = st.selectbox("Choose Language:", list(INDIAN_LANGUAGES.keys()), index=0)
        selected_lang_code = INDIAN_LANGUAGES[target_lang]
        st.session_state.language = selected_lang_code
        
        # Translate UI text based on selected language
        ui_text = translate_ui_text(UI_TEXT, selected_lang_code)
    
    # App title with animation
    st.markdown(
        f"<div class='app-title'>"
        f"<span class='app-icon'>⚖</span>"
        f"<h1>{translate_text(ui_text['app_title'], selected_lang_code)}</h1>"
        f"</div>", 
        unsafe_allow_html=True
    )
    
    # Initialize session state
    if 'document_text' not in st.session_state:
        st.session_state.document_text = ""

    # Sidebar continued
    with st.sidebar:
        st.markdown(f"<h2>{ui_text['settings']}</h2>", unsafe_allow_html=True)
        
        st.markdo