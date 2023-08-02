import sys
import requests

def fetch_xml(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            xml_content = response.content.decode('utf-8')
            return xml_content
        else:
            print(f"Failed to fetch XML. Status code: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None

if __name__ == "__main__":
    url = input("Full URL: ")
    xml_content = fetch_xml(url)*25
    if xml_content:
        print(xml_content)
