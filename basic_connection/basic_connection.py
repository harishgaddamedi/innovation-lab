from google import genai

client = genai.Client(api_key="AIzaSyC45EQ3pQM74h6BKKyOYvq8DP01qHVGTGc")

response = client.models.generate_content(
    model="gemini-2.0-flash", contents="Explain how AI works in a few words"
)
print(response.text)