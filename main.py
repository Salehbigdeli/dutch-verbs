import sys
import requests
from bs4 import BeautifulSoup
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QPushButton, QLabel, QLineEdit, QComboBox, QTextEdit)
from PySide6.QtCore import Qt
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebEngineCore import QWebEnginePage

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dutch Verb Conjugator")
        self.setMinimumSize(800, 600)
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Create input field and button
        self.verb_input = QLineEdit()
        self.verb_input.setPlaceholderText("Enter a Dutch verb (e.g., 'komen')")
        self.verb_input.returnPressed.connect(self.search_verb)
        self.search_button = QPushButton("Search")
        self.search_button.clicked.connect(self.search_verb)
        
        # Create web view for results
        self.web_view = QWebEngineView()
        
        layout.addWidget(self.verb_input)
        layout.addWidget(self.search_button)
        layout.addWidget(self.web_view)
        
    def search_verb(self):
        # Disable the search button and input field while fetching
        self.search_button.setEnabled(False)
        self.verb_input.setEnabled(False)
        
        verb = self.verb_input.text().strip()
        if not verb:
            self.web_view.setHtml("Please enter a verb")
            # Re-enable the search button and input field
            self.search_button.setEnabled(True)
            self.verb_input.setEnabled(True)
            return
            
        url = f"https://cooljugator.com/nl/{verb}"
        try:
            response = requests.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find the conjugation data section
            conjugation_div = soup.find('div', id='conjugation-data')
            if not conjugation_div:
                self.web_view.setHtml("No conjugation data found for this verb")
                # Re-enable the search button and input field
                self.search_button.setEnabled(True)
                self.verb_input.setEnabled(True)
                return
            
            # Get the CSS styles from the original page
            styles = soup.find_all('link', rel='stylesheet')
            css_content = ""
            for style in styles:
                if style.get('href'):
                    css_url = style['href']
                    if not css_url.startswith('http'):
                        css_url = 'https://cooljugator.com' + css_url
                    try:
                        css_response = requests.get(css_url)
                        css_content += css_response.text + "\n"
                    except:
                        pass
            
            # Create HTML with styles
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    {css_content}
                    body {{ 
                        margin: 0; 
                        padding: 10px; 
                        width: 100%; 
                        box-sizing: border-box;
                        font-size: 14px;
                        line-height: 1.4;
                    }}
                    .ribbon {{
                        width: 180% !important;
                        color: black !important;
                        background-color: #f0f0f0 !important;
                        padding: 10px !important;
                        border-radius: 5px !important;
                        margin-bottom: 10px !important;
                    }}
                    #conjugation-data {{ 
                        margin: 0; 
                        width: 100%; 
                        padding: 10px;
                        box-sizing: border-box;
                        overflow-x: auto;
                    }}
                    .ui {{ 
                        margin: 0; 
                        width: 100%; 
                        padding: 10px;
                        box-sizing: border-box;
                    }}
                    .fourteen {{ 
                        margin: 0; 
                        width: 100%; 
                        padding: 10px;
                        box-sizing: border-box;
                    }}
                    table {{
                        width: 100%;
                        border-collapse: collapse;
                        margin: 10px 0;
                    }}
                    td, th {{
                        padding: 8px;
                        border: 1px solid #ddd;
                        word-wrap: break-word;
                    }}
                    @media screen and (max-width: 600px) {{
                        body {{ font-size: 12px; }}
                        td, th {{ padding: 4px; }}
                    }}
                </style>
            </head>
            <body>
                {conjugation_div.prettify()}
            </body>
            </html>
            """
            
            self.web_view.setHtml(html_content)
            
        except requests.RequestException as e:
            self.web_view.setHtml(f"Error fetching data: {str(e)}")
        except Exception as e:
            self.web_view.setHtml(f"An error occurred: {str(e)}")
        finally:
            # Re-enable the search button and input field
            self.search_button.setEnabled(True)
            self.verb_input.setEnabled(True)

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
